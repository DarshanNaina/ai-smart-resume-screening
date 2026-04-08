from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Application, Interview, Job, Organization, User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    organization_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "role", "organization_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]

        org_name = self.cleaned_data.get("organization_name", "").strip()
        if user.role == User.ROLE_HR and org_name:
            org, _ = Organization.objects.get_or_create(name=org_name)
            user.organization = org
        if commit:
            user.save()
        return user


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6)


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "min_experience", "is_active"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume"]
        widgets = {
            "resume": forms.ClearableFileInput(
                attrs={"class": "form-control", "data-max-bytes": settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024}
            )
        }

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        ext = resume.name.lower().split(".")[-1]
        if ext not in {"pdf", "docx"}:
            raise forms.ValidationError("Only PDF and DOCX files are allowed.")
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if resume.size > max_bytes:
            raise forms.ValidationError(f"Max file size is {settings.MAX_UPLOAD_SIZE_MB}MB.")
        return resume


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["scheduled_at", "meeting_link", "notes"]
        widgets = {"scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class ApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status", "selection_stage", "is_selected", "feedback"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "selection_stage": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "is_selected": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "feedback": forms.Textarea(attrs={"class": "form-control form-control-sm", "rows": 2}),
        }
