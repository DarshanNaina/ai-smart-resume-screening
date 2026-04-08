from datetime import timedelta
import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_HR = "HR"
    ROLE_CLIENT = "CLIENT"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_HR, "HR"),
        (ROLE_CLIENT, "Client"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )


class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @classmethod
    def create_for_user(cls, user):
        code = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES),
        )

    def is_valid(self, entered_code):
        return (not self.is_used) and self.expires_at >= timezone.now() and self.code == entered_code


class Job(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_experience = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.organization.name})"


def resume_upload_path(instance, filename):
    return f"resumes/{instance.candidate_id}/{filename}"


def offer_upload_path(instance, filename):
    return f"offers/{instance.candidate_id}/{filename}"


class Application(models.Model):
    STATUS_APPLIED = "APPLIED"
    STATUS_SHORTLISTED = "SHORTLISTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_INTERVIEW = "INTERVIEW"
    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_INTERVIEW, "Interview Scheduled"),
    ]
    SELECTION_NONE = "NONE"
    SELECTION_ROUND2 = "ROUND2"
    SELECTION_ROUND3 = "ROUND3"
    SELECTION_DIRECT = "DIRECT"
    SELECTION_CHOICES = [
        (SELECTION_NONE, "Not Selected"),
        (SELECTION_ROUND2, "Round 2 Selected"),
        (SELECTION_ROUND3, "Round 3 Selected"),
        (SELECTION_DIRECT, "Direct Selection"),
    ]

    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    assigned_hr = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_applications",
        limit_choices_to={"role": User.ROLE_HR},
    )
    resume = models.FileField(upload_to=resume_upload_path)
    ai_score = models.FloatField(default=0.0)
    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    selection_stage = models.CharField(max_length=20, choices=SELECTION_CHOICES, default=SELECTION_NONE)
    is_selected = models.BooleanField(default=False)
    offer_sent = models.BooleanField(default=False)
    custom_offer_letter = models.FileField(upload_to=offer_upload_path, blank=True, null=True)
    feedback = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("candidate", "job")
        ordering = ["-ai_score", "-applied_at"]


class Interview(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="interview")
    scheduled_at = models.DateTimeField()
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
