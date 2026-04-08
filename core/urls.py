from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp_view, name="verify-otp"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("jobs/create/", views.create_job, name="create-job"),
    path("jobs/<int:job_id>/apply/", views.apply_job, name="apply-job"),
    path("applications/<int:application_id>/schedule/", views.schedule_interview, name="schedule-interview"),
    path("applications/<int:application_id>/review/", views.review_application, name="review-application"),
    path("applications/<int:application_id>/assign-hr/", views.assign_hr, name="assign-hr"),
    path("applications/<int:application_id>/upload-offer/", views.upload_offer_letter, name="upload-offer"),
    path("analytics/admin/", views.admin_analytics, name="admin-analytics"),
    path("applications/export/", views.export_applications, name="export-applications"),
]
