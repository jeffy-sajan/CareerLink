from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .views import (
    # Authentication
    user_login, user_logout, admin_login, admin_logout,
    # Registration
    job_seeker_register, employer_register,
    # Dashboards
    job_seeker_dashboard, employer_dashboard, admin_dashboard,
    # Job Management
    job_list, job_detail, job_search, post_job, edit_job, delete_job,
    # Company Management
    company_profile, review_company, edit_company_profile,
    # Job Applications
    apply_for_job, applied_jobs, employer_applications, view_application, update_application_status,
    # Job Seeker Profile
    update_job_seeker_profile,
    # Saved Jobs
    saved_jobs, save_job, unsave_job,
    # Admin Views
    manage_jobs, manage_applications,
    # About and Contact
    about, contact,
    # Admin Views
    delete_user, approve_job, reject_job,
    # New URL pattern
    view_my_application,
    # Interview Management
    schedule_interview, manage_interview, submit_interview_feedback,
    # Notifications
    get_notifications, delete_notification, delete_all_notifications,
    # Subscription URLs
    subscription_plans, initiate_subscription, subscription_success, subscription_cancel,
    # New admin views
    admin_users, admin_jobs, admin_premium, admin_revenue, admin_settings
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'jobseekerprofile'):
            return redirect('job_seeker_dashboard')
        elif hasattr(request.user, 'employerprofile'):
            return redirect('employer_dashboard')
    return redirect('login')

# Admin URL patterns
admin_patterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('users/', admin_users, name='admin_users'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('jobs/', admin_jobs, name='admin_jobs'),
    path('companies/', company_profile, name='admin_companies'),
    path('applications/', manage_applications, name='admin_applications'),
    path('jobs/<int:job_id>/approve/', approve_job, name='approve_job'),
    path('jobs/<int:job_id>/reject/', reject_job, name='reject_job'),
]

# Main URL patterns
urlpatterns = [
    # Root URL - Job Seeker Dashboard (Landing Page)
    path('', job_seeker_dashboard, name='home'),

    # About and Contact Pages
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

    # Authentication
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/logout/', admin_logout, name='admin_logout'),

    # Registration
    path('register/', job_seeker_register, name='register'),
    path('register/job-seeker/', job_seeker_register, name='job_seeker_register'),
    path('register/employer/', employer_register, name='employer_register'),

    # Dashboards
    path('job_seeker/dashboard/', job_seeker_dashboard, name='job_seeker_dashboard'),
    path('employer/dashboard/', employer_dashboard, name='employer_dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),

    # Job Management
    path('jobs/', job_list, name='job_list'),
    path('job/<int:job_id>/', job_detail, name='job_detail'),
    path('job/search/', job_search, name='job_search'),
    path('employer/post-job/', post_job, name='post_job'),
    path('employer/job/<int:job_id>/edit/', edit_job, name='edit_job'),
    path('job/<int:job_id>/delete/', delete_job, name='delete_job'),

    # Company Management
    path('company/<int:company_id>/', company_profile, name='company_profile'),
    path('company/<int:company_id>/review/', review_company, name='review_company'),
    path('company/<int:company_id>/edit/', edit_company_profile, name='edit_company_profile'),

    # Job Applications
    path('apply/<int:job_id>/', apply_for_job, name='apply_for_job'),
    path('my-applications/', applied_jobs, name='applied_jobs'),
    path('my-applications/<int:application_id>/', view_my_application, name='view_my_application'),
    path('employer/applications/', employer_applications, name='employer_applications'),
    path('employer/applications/<int:application_id>/', login_required(view_application), name='view_application'),
    path('employer/application/<int:application_id>/update/', update_application_status, name='update_application_status'),

    # Job Seeker Profile
    path('job-seeker/profile/', login_required(update_job_seeker_profile), name='job_seeker_profile'),
    path('job-seeker/profile/update/', login_required(update_job_seeker_profile), name='update_job_seeker_profile'),
    path('job-seeker/applications/', login_required(applied_jobs), name='job_seeker_applications'),

    # Saved Jobs
    path('job-seeker/saved-jobs/', login_required(saved_jobs), name='saved_jobs'),
    path('save-job/<int:job_id>/', save_job, name='save_job'),
    path('unsave-job/<int:job_id>/', unsave_job, name='unsave_job'),

    # Employer URLs
    path('employer/profile/', login_required(employer_dashboard), name='employer_profile'),
    path('employer/profile/update/', login_required(employer_dashboard), name='update_employer_profile'),
    path('employer/jobs/', login_required(job_list), name='employer_jobs'),
    path('employer/jobs/<int:job_id>/edit/', login_required(edit_job), name='edit_job'),
    path('employer/jobs/<int:job_id>/delete/', login_required(delete_job), name='delete_job'),
    path('employer/applications/', login_required(employer_applications), name='employer_applications'),
    path('employer/applications/<int:application_id>/', login_required(view_application), name='view_application'),
    path('employer/applications/<int:application_id>/update-status/', login_required(update_application_status), name='update_application_status'),

    # Job URLs
    path('jobs/<int:job_id>/apply/', login_required(apply_for_job), name='apply_job'),
    path('jobs/<int:job_id>/save/', login_required(save_job), name='save_job'),
    path('jobs/<int:job_id>/unsave/', login_required(unsave_job), name='unsave_job'),

    # Company URLs
    path('companies/', company_profile, name='company_list'),
    path('companies/<int:company_id>/', company_profile, name='company_detail'),
    path('companies/<int:company_id>/review/', login_required(review_company), name='company_review'),

    # Search URLs
    path('search/', job_search, name='job_search'),

    # Interview Management URLs
    path('employer/application/<int:application_id>/schedule-interview/', schedule_interview, name='schedule_interview'),
    path('interview/<int:interview_id>/manage/', manage_interview, name='manage_interview'),
    path('interview/<int:interview_id>/feedback/', submit_interview_feedback, name='submit_interview_feedback'),

    # Notifications
    path('notifications/', get_notifications, name='notifications'),
    path('notifications/<int:notification_id>/delete/', delete_notification, name='delete_notification'),
    path('notifications/delete-all/', delete_all_notifications, name='delete_all_notifications'),

    # Subscription URLs
    path('subscription/plans/', subscription_plans, name='subscription_plans'),
    path('subscription/initiate/<str:plan_type>/', initiate_subscription, name='initiate_subscription'),
    path('subscription/success/', subscription_success, name='subscription_success'),
    path('subscription/cancel/', subscription_cancel, name='subscription_cancel'),

    # New URL pattern
    path('update-application-status/<int:application_id>/', update_application_status, name='update_application_status'),

    # New admin URLs
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/jobs/', admin_jobs, name='admin_jobs'),
    path('admin/premium/', admin_premium, name='admin_premium'),
    path('admin/revenue/', admin_revenue, name='admin_revenue'),
    path('admin/applications/', manage_applications, name='admin_applications'),
    path('admin/settings/', admin_settings, name='admin_settings'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
