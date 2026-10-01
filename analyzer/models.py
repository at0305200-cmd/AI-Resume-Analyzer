from django.db import models


class Resume(models.Model):
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    extracted_text = models.TextField(blank=True)

    detected_skills = models.TextField(blank=True)

    job_description = models.TextField(blank=True)

    match_percentage = models.FloatField(null=True, blank=True)

    nlp_score = models.FloatField(null=True, blank=True)

    skill_score = models.FloatField(null=True, blank=True)

    matched_skills = models.TextField(blank=True)

    missing_skills = models.TextField(blank=True)

    def __str__(self):
        return self.file.name