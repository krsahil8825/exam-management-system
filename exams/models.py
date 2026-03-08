"""
exams.models
~~~~~~~~~~~~

Models for exams, questions, registrations, answers, and results.
"""

import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import Candidate, Employee


def question_image_upload_path(instance, filename):
    """Generate upload path for question images based on exam code."""
    exam_code = instance.exam.code if instance.exam_id else "unassigned"
    return f"question_photos/{exam_code}/{filename}"


class Exam(models.Model):
    """Model representing an exam with its details, status, and timing."""

    class Status(models.TextChoices):
        """Status choices for the exam lifecycle."""

        DRAFT = "D", "Draft"
        PUBLISHED = "P", "Published"
        CLOSED = "C", "Closed"

    slug = models.SlugField(unique=True, blank=True, editable=False)
    code = models.CharField(max_length=25, unique=True, editable=False)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="created_exams"
    )

    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)

    total_marks = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)

    pass_percentage = models.FloatField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Defines ordering and indexes."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "start_time"]),
        ]

    def clean(self):
        """Validate that end time is after start time."""
        super().clean()

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

    @staticmethod
    def _generate_code():
        """Generate a unique exam code."""
        return f"EXAM-{uuid.uuid4().hex[:10].upper()}"

    def _generate_unique_code(self):
        """Ensure generated exam code is unique."""
        code = self._generate_code()
        while Exam.objects.filter(code=code).exists():
            code = self._generate_code()
        return code

    def _generate_unique_slug(self):
        """Generate a unique slug based on the title and a random suffix."""
        base = slugify(self.title) or "exam"
        slug = f"{base}-{uuid.uuid4().hex[:6]}"
        while Exam.objects.filter(slug=slug).exists():
            slug = f"{base}-{uuid.uuid4().hex[:6]}"
        return slug

    def refresh_exam_totals(self):
        """Recalculate total marks and question count based on related questions."""
        totals = self.questions.aggregate(total_marks=Sum("marks"))
        self.total_marks = totals["total_marks"] or 0
        self.total_questions = self.questions.count()
        self.save(update_fields=["total_marks", "total_questions"])

    def is_active(self):
        """Check if the exam is currently active based on status and timing."""
        now = timezone.now()
        return (
            self.status == self.Status.PUBLISHED
            and self.start_time <= now <= self.end_time
        )

    def save(self, *args, **kwargs):
        """Generate code and slug if not set, then save the exam."""

        if not self.code:
            self.code = self._generate_unique_code()

        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the exam showing code and title."""
        return f"{self.code} - {self.title}"


class Question(models.Model):
    """Model representing a question belonging to an exam, with options and correct answer."""

    class Option(models.TextChoices):
        """Choices for the correct answer option."""

        A = "A", "Option A"
        B = "B", "Option B"
        C = "C", "Option C"
        D = "D", "Option D"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")

    text = models.TextField()

    photo = models.ImageField(
        upload_to=question_image_upload_path, blank=True, null=True
    )

    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)

    correct_answer = models.CharField(max_length=1, choices=Option.choices)

    marks = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Defines ordering and indexes for questions."""

        ordering = ["id"]
        indexes = [
            models.Index(fields=["exam"]),
        ]

    def clean(self):
        """Validate that the question cannot be modified after the exam has started."""
        super().clean()

        if not self.exam_id:
            return

        if self.exam.start_time <= timezone.now():
            raise ValidationError("Cannot modify questions after exam has started.")

    def save(self, *args, **kwargs):
        """Save the question and refresh exam totals after saving."""

        super().save(*args, **kwargs)
        self.exam.refresh_exam_totals()

    def delete(self, *args, **kwargs):
        """Delete the question and refresh exam totals after deletion."""
        if self.exam.start_time <= timezone.now():
            raise ValidationError("Cannot delete questions after exam has started.")
        exam = self.exam
        super().delete(*args, **kwargs)
        exam.refresh_exam_totals()

    def __str__(self):
        """String representation of the question showing exam code and question text."""
        return f"{self.exam.code} - {self.text[:40]}"


class Registration(models.Model):
    """Model representing a candidate's registration for an exam, including submission status and timestamps."""

    registration_no = models.CharField(max_length=25, unique=True, editable=False)

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="registrations"
    )

    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="registrations"
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    is_submitted = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Defines unique constraints and indexes for registrations."""

        constraints = [
            models.UniqueConstraint(
                fields=["exam", "candidate"], name="unique_exam_registration"
            )
        ]

        indexes = [
            models.Index(fields=["exam", "candidate"]),
        ]

    @staticmethod
    def _generate_registration_no():
        """Generate a unique registration number for the candidate's exam registration."""
        return f"REG-{uuid.uuid4().hex[:12].upper()}"

    def _generate_unique_registration_no(self):
        """Ensure the generated registration number is unique across all registrations."""
        registration_no = self._generate_registration_no()
        while Registration.objects.filter(registration_no=registration_no).exists():
            registration_no = self._generate_registration_no()
        return registration_no

    def clean(self):
        """Validate that the registration is valid based on exam status and timing, and that it cannot be modified after submission."""
        super().clean()

        if not self.exam_id:
            return

        now = timezone.now()

        if self.exam.status != Exam.Status.PUBLISHED:
            raise ValidationError("Exam is not open.")

        if now < self.exam.start_time:
            raise ValidationError("Exam has not started yet.")

        if now > self.exam.end_time:
            raise ValidationError("Exam already ended.")

    def save(self, *args, **kwargs):
        """Generate a unique registration number if not set, then save the registration."""

        if not self.registration_no:
            self.registration_no = self._generate_unique_registration_no()

        super().save(*args, **kwargs)

    def submit_exam(self):
        """Mark the exam as submitted, set submission timestamp, and calculate the result in a single transaction."""
        with transaction.atomic():
            registration = Registration.objects.select_for_update().get(pk=self.pk)
            if registration.is_submitted:
                return

            now = timezone.now()
            registration.is_submitted = True
            registration.submitted_at = now
            registration.save(update_fields=["is_submitted", "submitted_at"])

            result, _ = Result.objects.get_or_create(registration=registration)
            result.calculate_result()

    def __str__(self):
        """String representation of the registration showing candidate email and exam code."""
        return f"{self.candidate.user.email} - {self.exam.code}"


class Answer(models.Model):
    """Model representing a candidate's answer to a specific question in an exam registration."""

    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="answers"
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.CharField(max_length=1, choices=Question.Option.choices)

    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Defines unique constraints and indexes for answers."""

        constraints = [
            models.UniqueConstraint(
                fields=["registration", "question"],
                name="unique_answer_per_question_per_registration",
            )
        ]

        indexes = [
            models.Index(fields=["registration"]),
            models.Index(fields=["question"]),
        ]

    def clean(self):
        """Validate that the answer is valid based on registration status, exam timing, and question-exam consistency."""
        super().clean()

        if not self.registration_id or not self.question_id:
            return

        exam = self.registration.exam
        now = timezone.now()

        if self.question.exam_id != self.registration.exam_id:
            raise ValidationError("Question does not belong to this exam.")

        if self.registration.is_submitted:
            raise ValidationError("Exam already submitted.")

        if now < exam.start_time:
            raise ValidationError("Exam has not started yet.")

        if now > exam.end_time:
            raise ValidationError("Exam already ended.")

    def __str__(self):
        """String representation of the answer showing registration number and question ID."""
        return f"{self.registration.registration_no} - Q{self.question.id}"


class Result(models.Model):
    """Model representing the result of an exam registration, including score, percentage, and pass status."""

    registration = models.OneToOneField(
        Registration, on_delete=models.CASCADE, related_name="result"
    )

    score = models.PositiveIntegerField(default=0)

    percentage = models.FloatField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    passed = models.BooleanField(default=False)

    calculated_at = models.DateTimeField(auto_now_add=True)

    def calculate_result(self):
        """Calculate the result based on the registration's answers and the exam's total marks, then save the result."""
        registration = self.registration
        exam = registration.exam

        obtained_marks = 0
        answers = registration.answers.select_related("question")
        for answer in answers:
            if answer.selected_option == answer.question.correct_answer:
                obtained_marks += answer.question.marks

        total_marks = exam.total_marks
        percentage = 0
        if total_marks > 0:
            percentage = (obtained_marks / total_marks) * 100

        self.score = obtained_marks
        self.percentage = percentage
        self.passed = percentage >= exam.pass_percentage
        self.save(update_fields=["score", "percentage", "passed"])

    def __str__(self):
        """String representation of the result showing candidate email and score."""
        return f"{self.registration.candidate.user.email} - {self.score}"
