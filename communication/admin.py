"""
communication.admin
~~~~~~~~~~~~~~~~~~~

Admin config for communication app.
"""

from django.contrib import admin

from .models import Messages


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    """Admin view for employee messages."""
    list_display = ["sender", "receiver", "subject", "is_read", "created_at"]
    list_filter = ["is_read"]
    search_fields = ["sender__user__email", "receiver__user__email", "subject"]
    readonly_fields = ["slug", "created_at"]
    ordering = ["-created_at"]


# Customize admin site titles
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management"
admin.site.index_title = "Admin Dashboard"
