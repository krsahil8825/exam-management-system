"""
exam.models
~~~~~~~~~~~

Models for online examination system.

Structure:

Employee
    |-- Exam
            |-- Question

Candidate
    |-- Registration
            |-- Answer
            |-- Result
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.models import Employee, Candidate
import uuid
import random


# =========================================================
# Utility Functions
# =========================================================
def question_image_upload_path(instance, filename):
    """
    Upload path:
    question_photos/<exam_code>/<filename>
    """
    return f"question_photos/{instance.exam.code}/{filename}"


# =========================================================
# Exam Model
# =========================================================
class Exam(models.Model):
    """
    Represents an examination created by an employee.
    """

    slug = models.SlugField(unique=True, blank=True)
    code = models.CharField(max_length=20, unique=True, blank=True)

    title = models.CharField(max_length=200)

    DRAFT = "D"
    PUBLISHED = "P"
    CLOSED = "C"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
        (CLOSED, "Closed"),
    ]

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DRAFT)

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="created_exams"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    total_marks = models.PositiveIntegerField(default=0)
    pass_percentage = models.FloatField(default=40)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        """
        Generates a unique exam code in format EXAM-XXXXXXXX.
        """
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        code = "EXAM-" + "".join(random.choices(chars, k=8))

        while Exam.objects.filter(code=code).exists():
            code = "EXAM-" + "".join(random.choices(chars, k=8))
        return code

    def save(self, *args, **kwargs):
        """Override save to auto-generate code and slug."""
        if not self.code:
            self.code = self.generate_code()

        if not self.slug:
            self.slug = str(uuid.uuid4())

        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of exam showing code and title."""
        return f"{self.code} - {self.title[:50]}"


# =========================================================
# Question Model
# =========================================================
class Question(models.Model):
    """
    Question belongs to ONE exam.
    Many questions can belong to one exam.
    """

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")

    text = models.TextField()

    photo = models.ImageField(
        upload_to=question_image_upload_path, blank=True, null=True
    )

    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)

    OPTION_CHOICES = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    correct_answer = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        """Override save to update total marks of exam."""
        super().save(*args, **kwargs)

        # Update total marks of exam automatically
        total = self.exam.questions.aggregate(total=models.Sum("marks"))["total"] or 0

        self.exam.total_marks = total
        self.exam.save(update_fields=["total_marks"])

    def __str__(self):
        """
        String representation of question showing exam code and first 40 chars of text.
        """
        return f"{self.exam.code} - {self.text[:40]}"


# =========================================================
# Registration Model
# =========================================================
class Registration(models.Model):
    """
    Candidate registers for an exam.
    Prevents duplicate registration.
    """

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="registrations"
    )

    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="registrations"
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        """
        Enforces unique registration per candidate per exam.
        """

        constraints = [
            models.UniqueConstraint(
                fields=["exam", "candidate"], name="unique_exam_registration"
            )
        ]

    def submit_exam(self):
        """
        Marks exam as submitted and triggers result calculation.
        """
        if self.is_submitted:
            raise ValidationError("Exam already submitted.")

        self.is_submitted = True
        self.submitted_at = timezone.now()

        if self.submitted_at > self.exam.end_time:
            raise ValidationError("Cannot submit after exam end time.")
        self.save()

        result, created = Result.objects.get_or_create(registration=self)
        result.calculate_result()

    def __str__(self):
        """
        String representation of registration showing candidate username and exam code.
        """
        return f"{self.candidate.user.username} - {self.exam.code}"


# =========================================================
# Answer Model
# =========================================================
class Answer(models.Model):
    """
    Stores candidate answer per question.
    One answer per question per registration.
    """

    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="answers"
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.CharField(max_length=1, choices=Question.OPTION_CHOICES)

    class Meta:
        """
        Enforces one answer per question per registration.
        """

        unique_together = ("registration", "question")

    def clean(self):
        """
        Ensure question belongs to same exam as registration.
        """
        if self.question.exam != self.registration.exam:
            raise ValidationError("Question does not belong to this exam.")

    def __str__(self):
        """
        String representation of answer showing registration and question id.
        """
        return f"{self.registration} - Q{self.question.id}"


# =========================================================
# Result Model
# =========================================================
class Result(models.Model):
    """
    Auto-calculated result after submission.
    """

    registration = models.OneToOneField(
        Registration, on_delete=models.CASCADE, related_name="result"
    )

    score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)

    calculated_at = models.DateTimeField(auto_now_add=True)

    def calculate_result(self):
        """
        Calculates total score and pass status.
        """
        registration = self.registration
        exam = registration.exam

        total_marks = 0
        obtained_marks = 0

        for answer in registration.answers.select_related("question"):
            total_marks += answer.question.marks

            if answer.selected_option == answer.question.correct_answer:
                obtained_marks += answer.question.marks

        self.score = obtained_marks

        if total_marks > 0:
            self.percentage = (obtained_marks / total_marks) * 100

        self.passed = self.percentage >= exam.pass_percentage

        self.save()

    def __str__(self):
        """
        String representation of result showing candidate username and score.
        """
        return f"{self.registration.candidate.user.username} - {self.score}"
