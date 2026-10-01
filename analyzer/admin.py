from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "file",
        "uploaded_at",
        "match_percentage",
    )

    search_fields = (
        "file",
        "job_description",
    )

    list_filter = (
        "uploaded_at",
    )