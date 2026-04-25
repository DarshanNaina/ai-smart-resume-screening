import csv
from io import BytesIO
import os
from urllib.parse import quote, unquote

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ApplicationForm,
    ApplicationReviewForm,
    InterviewForm,
    JobForm,
    LoginForm,
    OTPForm,
    SecretCodeForm,
    UserRegisterForm,
)
from .models import Application, Job, OTPCode, Organization, User
from .services import score_resume_against_job, send_offer_letter_email, send_plain_mail


def home(request):
    jobs = Job.objects.filter(is_active=True, organization__is_blocked=False)
    q = request.GET.get("q", "").strip()
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(description__icontains=q)
    return render(request, "home.html", {"jobs": jobs})


def verify_secret_view(request):
    role = request.GET.get('role', 'CLIENT')
    if role.upper() not in ['ADMIN', 'HR']:
        return redirect('home')
    
    if request.method == "POST":
        form = SecretCodeForm(request.POST)
        if form.is_valid():
            secret_code = os.getenv('ADMIN_HR_SECRET_CODE', 'default_secret')
            if form.cleaned_data['secret_code'] == secret_code:
                request.session['secret_verified'] = True
                next_url = unquote(request.GET.get('next', 'home'))
                
                # If this is for login, store user_id in session
                user_id = request.GET.get('user_id')
                if user_id:
                    request.session['pending_login_user_id'] = user_id
                
                return redirect(next_url)
            else:
                messages.error(request, "Invalid secret code.")
    else:
        form = SecretCodeForm()
    return render(request, "verify_secret.html", {"form": form})


def register_view(request):
    # Handle pending registration after secret verification
    pending_registration = request.session.get('pending_registration')
    if pending_registration:
        request.session.pop('pending_registration', None)
        request.session.pop('secret_verified', None)  # Clear after use
        
        # Recreate form with stored data
        form = UserRegisterForm(pending_registration)
        if form.is_valid():
            user = form.save()
            send_plain_mail(
                "Registration Successful",
                "Your account has been created successfully.",
                user.email,
            )
            messages.success(request, "Registration complete. Please login.")
            return redirect("login")
        # If form is invalid, show it again
    
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            if role in ['ADMIN', 'HR']:
                if not request.session.get('secret_verified'):
                    # Store form data in session
                    request.session['pending_registration'] = dict(request.POST)
                    next_url = '/register/'
                    return redirect(f'/verify-secret/?role={role}&next={quote(next_url)}')
            
            # Clear secret verification after use
            request.session.pop('secret_verified', None)
            
            user = form.save()
            send_plain_mail(
                "Registration Successful",
                "Your account has been created successfully.",
                user.email,
            )
            messages.success(request, "Registration complete. Please login.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    # Handle pending login after secret verification
    pending_user_id = request.session.get('pending_login_user_id')
    if pending_user_id:
        try:
            user = User.objects.get(id=pending_user_id)
            request.session.pop('pending_login_user_id', None)
            request.session.pop('secret_verified', None)  # Clear after use
            
            otp = OTPCode.create_for_user(user)
            request.session["otp_user_id"] = user.id
            try:
                send_plain_mail("Your OTP Code", f"OTP: {otp.code}. Expires in 5 minutes.", user.email)
            except Exception as exc:
                messages.error(request, f"OTP email failed: {exc}")
                return redirect("login")
            messages.info(request, "OTP sent to your email.")
            return redirect("verify-otp")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("login")
    
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user needs secret verification
            if user.role in ['ADMIN', 'HR']:
                if not request.session.get('secret_verified'):
                    next_url = '/login/'
                    return redirect(f'/verify-secret/?role={user.role}&next={quote(next_url)}&user_id={user.id}')
            
            # Clear secret verification after use
            request.session.pop('secret_verified', None)
            
            otp = OTPCode.create_for_user(user)
            request.session["otp_user_id"] = user.id
            try:
                send_plain_mail("Your OTP Code", f"OTP: {otp.code}. Expires in 5 minutes.", user.email)
            except Exception as exc:
                messages.error(request, f"OTP email failed: {exc}")
                return redirect("login")
            messages.info(request, "OTP sent to your email.")
            return redirect("verify-otp")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def verify_otp_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("login")
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data["otp"]
            otp = OTPCode.objects.filter(user=user, is_used=False).order_by("-created_at").first()
            if otp and otp.is_valid(entered):
                otp.is_used = True
                otp.save(update_fields=["is_used"])
                login(request, user)
                request.session.pop("otp_user_id", None)
                return redirect("dashboard")
            messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPForm()
    return render(request, "registration/verify_otp.html", {"form": form})


class CustomLogoutView(LogoutView):
    next_page = "login"


@login_required
def dashboard(request):
    user = request.user
    if user.role == User.ROLE_ADMIN:
        admin_apps_qs = Application.objects.select_related("candidate", "job", "job__organization").order_by("-applied_at")
        admin_paginator = Paginator(admin_apps_qs, 8)
        admin_page_obj = admin_paginator.get_page(request.GET.get("page"))
        context = {
            "organizations": user.__class__.objects.filter(role=User.ROLE_HR).count(),
            "jobs_count": Job.objects.count(),
            "applications_count": Application.objects.count(),
            "shortlisted_count": Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
            "applications": admin_page_obj,
            "page_obj": admin_page_obj,
        }
        return render(request, "dashboard_admin.html", context)

    if user.role == User.ROLE_HR:
        jobs = Job.objects.filter(organization=user.organization)
        applications_qs = Application.objects.filter(job__organization=user.organization).select_related(
            "candidate", "job", "job__organization"
        )
        status_filter = request.GET.get("status", "").strip()
        min_score = request.GET.get("min_score", "").strip()
        skill = request.GET.get("skill", "").strip()
        sort = request.GET.get("sort", "score_desc").strip()
        if status_filter:
            applications_qs = applications_qs.filter(status=status_filter)
        if min_score:
            try:
                applications_qs = applications_qs.filter(ai_score__gte=float(min_score))
            except ValueError:
                messages.warning(request, "Invalid min score filter ignored.")
        if skill:
            applications_qs = applications_qs.filter(matched_skills__icontains=skill)
        ordering_map = {
            "score_desc": "-ai_score",
            "score_asc": "ai_score",
            "latest": "-applied_at",
            "oldest": "applied_at",
        }
        ordering = ordering_map.get(sort, "-ai_score")
        applications_qs = applications_qs.order_by(ordering, "-applied_at")
        paginator = Paginator(applications_qs, 8)
        page_obj = paginator.get_page(request.GET.get("page"))
        context = {
            "jobs": jobs,
            "applications": page_obj,
            "page_obj": page_obj,
            "sort": sort,
            "total_apps": applications_qs.count(),
            "shortlisted_apps": applications_qs.filter(status=Application.STATUS_SHORTLISTED).count(),
            "interview_apps": applications_qs.filter(status=Application.STATUS_INTERVIEW).count(),
            "status_chart_labels": ["Applied", "Shortlisted", "Rejected", "Interview"],
            "status_chart_values": [
                applications_qs.filter(status=Application.STATUS_APPLIED).count(),
                applications_qs.filter(status=Application.STATUS_SHORTLISTED).count(),
                applications_qs.filter(status=Application.STATUS_REJECTED).count(),
                applications_qs.filter(status=Application.STATUS_INTERVIEW).count(),
            ],
        }
        return render(request, "dashboard_hr.html", context)

    my_apps_qs = Application.objects.filter(candidate=user).select_related("job", "job__organization", "interview")
    paginator = Paginator(my_apps_qs, 8)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard_client.html", {"applications": page_obj, "page_obj": page_obj})


@login_required
def create_job(request):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.organization = request.user.organization
            job.created_by = request.user
            job.save()
            messages.success(request, "Job posted.")
            return redirect("dashboard")
    else:
        form = JobForm()
    return render(request, "job_form.html", {"form": form})


@login_required
def apply_job(request, job_id):
    if request.user.role != User.ROLE_CLIENT:
        return redirect("dashboard")
    job = get_object_or_404(Job, id=job_id, is_active=True)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            # default: unassigned HR; can be set later by client/HR
            application.save()

            result = score_resume_against_job(application.resume.path, job.description)
            application.ai_score = result["ai_score"]
            application.matched_skills = ", ".join(result["matched_skills"])
            application.missing_skills = ", ".join(result["missing_skills"])
            if application.ai_score >= 65:
                application.status = Application.STATUS_SHORTLISTED
                send_plain_mail(
                    "Shortlisted for Interview",
                    "Congratulations! You have been shortlisted. Please login to continue.",
                    request.user.email,
                )
            application.save()

            send_plain_mail(
                "Application Submitted",
                f"You have applied for {job.title}.",
                request.user.email,
            )
            messages.success(request, "Application submitted successfully.")
            return redirect("dashboard")
    else:
        form = ApplicationForm()
    return render(request, "apply_job.html", {"form": form, "job": job})


@login_required
def schedule_interview(request, application_id):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.created_by = request.user
            interview.save()
            application.status = Application.STATUS_INTERVIEW
            application.save(update_fields=["status"])
            interview_dt = timezone.localtime(interview.scheduled_at)
            meeting_link = interview.meeting_link if interview.meeting_link else "Will be shared soon."
            notes = interview.notes if interview.notes else "No additional notes."
            send_plain_mail(
                "Interview Scheduled",
                (
                    f"Hello {application.candidate.username},\n\n"
                    f"Your interview has been scheduled for: {application.job.title}\n"
                    f"Organization: {application.job.organization.name}\n"
                    f"Date: {interview_dt.strftime('%Y-%m-%d')}\n"
                    f"Time: {interview_dt.strftime('%I:%M %p')}\n"
                    f"Meeting Link: {meeting_link}\n"
                    f"Notes: {notes}\n\n"
                    "Please login to your dashboard for the latest updates."
                ),
                application.candidate.email,
            )
            messages.success(request, "Interview scheduled.")
            return redirect("dashboard")
    else:
        form = InterviewForm()
    return render(request, "schedule_interview.html", {"form": form, "application": application})


def logout_view(request):
    logout(request)
    request.session.pop('secret_verified', None)
    request.session.pop('pending_registration', None)
    request.session.pop('pending_login_user_id', None)
    return redirect("login")


@login_required
def review_application(request, application_id):
    if request.user.role not in {User.ROLE_HR, User.ROLE_ADMIN}:
        return redirect("dashboard")
    if request.user.role == User.ROLE_HR:
        application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    else:
        application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            updated = form.save()
            if request.user.role == User.ROLE_HR and updated.assigned_hr is None:
                updated.assigned_hr = request.user
                updated.save(update_fields=["assigned_hr"])
            if updated.status == Application.STATUS_SHORTLISTED:
                send_plain_mail(
                    "Application Shortlisted",
                    "Congratulations! You have been shortlisted. Please login to continue.",
                    updated.candidate.email,
                )
            elif updated.status == Application.STATUS_REJECTED:
                send_plain_mail(
                    "Application Update",
                    "Thank you for applying. Your application is not selected for this role.",
                    updated.candidate.email,
                )
            if (
                updated.status == Application.STATUS_INTERVIEW
                and updated.is_selected
                and not updated.offer_sent
            ):
                send_offer_letter_email(
                    candidate_name=updated.candidate.username,
                    job_title=updated.job.title,
                    organization_name=updated.job.organization.name,
                    to_email=updated.candidate.email,
                )
                updated.offer_sent = True
                updated.save(update_fields=["offer_sent"])
            messages.success(request, "Application review updated.")
    return redirect("dashboard")


@login_required
def assign_hr(request, application_id):
    if request.user.role != User.ROLE_CLIENT:
        return redirect("dashboard")
    application = get_object_or_404(Application, id=application_id, candidate=request.user)
    if request.method == "POST":
        hr_id = request.POST.get("hr_id")
        if hr_id:
            hr = get_object_or_404(
                User,
                id=hr_id,
                role=User.ROLE_HR,
                organization=application.job.organization,
            )
            application.assigned_hr = hr
            application.save(update_fields=["assigned_hr"])
            messages.success(request, f"Assigned HR set to {hr.username}.")
    return redirect("dashboard")


@login_required
def upload_offer_letter(request, application_id):
    if request.user.role not in {User.ROLE_HR, User.ROLE_ADMIN}:
        return redirect("dashboard")
    if request.user.role == User.ROLE_HR:
        application = get_object_or_404(Application, id=application_id, job__organization=request.user.organization)
    else:
        application = get_object_or_404(Application, id=application_id)

    if request.method == "POST":
        offer_file = request.FILES.get("offer_letter")
        if not offer_file:
            messages.error(request, "Please choose a PDF file.")
            return redirect("dashboard")
        if not offer_file.name.lower().endswith(".pdf"):
            messages.error(request, "Only PDF offer letters are allowed.")
            return redirect("dashboard")

        application.custom_offer_letter = offer_file
        application.save(update_fields=["custom_offer_letter"])

        email = EmailMessage(
            subject=f"Offer Letter - {application.job.title}",
            body=(
                f"Dear {application.candidate.username},\n\n"
                "Please find your offer letter attached.\n\n"
                "Regards,\n"
                f"{application.job.organization.name} HR Team"
            ),
            to=[application.candidate.email],
        )
        email.attach(offer_file.name, offer_file.read(), "application/pdf")
        email.send(fail_silently=False)

        application.offer_sent = True
        application.save(update_fields=["offer_sent"])
        messages.success(request, "Custom offer letter uploaded and emailed successfully.")
    return redirect("dashboard")


@login_required
def admin_analytics(request):
    if request.user.role != User.ROLE_ADMIN:
        return redirect("dashboard")
    context = {
        "total_orgs": Organization.objects.count(),
        "approved_orgs": Organization.objects.filter(is_approved=True).count(),
        "blocked_orgs": Organization.objects.filter(is_blocked=True).count(),
        "total_hr": User.objects.filter(role=User.ROLE_HR).count(),
        "total_candidates": User.objects.filter(role=User.ROLE_CLIENT).count(),
        "total_jobs": Job.objects.count(),
        "active_jobs": Job.objects.filter(is_active=True).count(),
        "total_apps": Application.objects.count(),
        "shortlisted_apps": Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
        "interview_apps": Application.objects.filter(status=Application.STATUS_INTERVIEW).count(),
        "generated_at": timezone.now(),
        "chart_labels": ["Applied", "Shortlisted", "Rejected", "Interview"],
        "chart_values": [
            Application.objects.filter(status=Application.STATUS_APPLIED).count(),
            Application.objects.filter(status=Application.STATUS_SHORTLISTED).count(),
            Application.objects.filter(status=Application.STATUS_REJECTED).count(),
            Application.objects.filter(status=Application.STATUS_INTERVIEW).count(),
        ],
    }
    return render(request, "admin_analytics.html", context)


@login_required
def export_applications(request):
    if request.user.role != User.ROLE_HR:
        return redirect("dashboard")
    export_format = request.GET.get("format", "csv").lower()
    applications = (
        Application.objects.filter(job__organization=request.user.organization)
        .select_related("candidate", "job")
        .order_by("-ai_score")
    )

    rows = [
        {
            "Candidate": app.candidate.username,
            "Email": app.candidate.email,
            "Job": app.job.title,
            "Score": app.ai_score,
            "Status": app.status,
            "Matched Skills": app.matched_skills,
            "Missing Skills": app.missing_skills,
            "Applied At": app.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for app in applications
    ]

    if export_format == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            messages.error(request, "PDF package not installed; downloaded CSV instead.")
            export_format = "csv"
        else:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 40
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, "Applications Export Report")
            y -= 24
            pdf.setFont("Helvetica", 9)
            for idx, row in enumerate(rows, start=1):
                line = (
                    f"{idx}. {row['Candidate']} | {row['Job']} | "
                    f"Score: {row['Score']} | Status: {row['Status']}"
                )
                pdf.drawString(40, y, line[:130])
                y -= 14
                if y < 50:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 9)
                    y = height - 40
            pdf.save()
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="applications_export.pdf"'
            return response

    if export_format == "xlsx":
        try:
            import pandas as pd
        except Exception:
            messages.error(request, "Pandas/openpyxl not installed; downloaded CSV instead.")
            export_format = "csv"
        else:
            df = pd.DataFrame(rows)
            output = BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            output.seek(0)
            response = HttpResponse(
                output.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="applications_export.xlsx"'
            return response

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="applications_export.csv"'
    writer = csv.DictWriter(
        response,
        fieldnames=["Candidate", "Email", "Job", "Score", "Status", "Matched Skills", "Missing Skills", "Applied At"],
    )
    writer.writeheader()
    writer.writerows(rows)
    return response
