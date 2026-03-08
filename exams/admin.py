"""
exams.admin
~~~~~~~~~~~

Admin configuration for the exams app, including models for Exam, Question, Registration, Answer, and Result. This module defines how these models are displayed and managed in the Django admin interface.

"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Answer, Exam, Question, Registration, Result


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin view for Exam model."""

    list_display = (
        "code",
        "title",
        "status",
        "start_time",
        "end_time",
        "total_questions",
        "total_marks",
    )
    list_filter = ("status", "start_time", "end_time")
    search_fields = ("code", "title", "slug")
    readonly_fields = ("code", "slug", "total_questions", "total_marks", "created_at")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin view for Question model."""

    list_display = (
        "id",
        "exam",
        "short_text",
        "correct_answer",
        "marks",
        "created_at",
    )

    list_filter = ("exam", "correct_answer")
    search_fields = ("text", "exam__code", "exam__title")

    readonly_fields = ("image_preview",)

    fields = (
        "exam",
        "text",
        "photo",
        "image_preview",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "marks",
    )

    @staticmethod
    def short_text(obj):
        """Return truncated question text."""
        return obj.text[:60]

    def image_preview(self, obj):
        """Return HTML for image preview in admin."""
        if obj.photo:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height:100px; border-radius:5px;" />'
                "</a>",
                obj.photo.url,
            )
        return "No Image"

    image_preview.short_description = "Question Image"


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Admin view for Registration model."""

    list_display = (
        "registration_no",
        "exam",
        "candidate",
        "is_submitted",
        "registered_at",
        "submitted_at",
    )
    list_filter = ("is_submitted", "registered_at")
    search_fields = (
        "registration_no",
        "exam__code",
        "candidate__user__email",
    )
    readonly_fields = ("registration_no", "registered_at", "submitted_at")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin view for Answer model."""

    list_display = ("id", "registration", "question", "selected_option", "answered_at")
    list_filter = ("selected_option", "answered_at")
    search_fields = ("registration__registration_no", "question__text")
    readonly_fields = ("answered_at",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """Admin view for Result model."""

    list_display = ("registration", "score", "percentage", "passed", "calculated_at")
    list_filter = ("passed", "calculated_at")
    search_fields = (
        "registration__registration_no",
        "registration__candidate__user__email",
        "registration__exam__code",
    )
    readonly_fields = ("calculated_at",)


# Customize admin site titles
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management"
admin.site.index_title = "Admin Dashboard"
