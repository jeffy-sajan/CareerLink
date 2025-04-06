from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.core.paginator import Paginator
from .models import (
    JobSeekerProfile, EmployerProfile, Job, JobApplication,
    Category, SavedJob, CompanyReview, Notification, Interview, InterviewFeedback
)
from .forms import JobSeekerProfileForm, JobApplicationForm, EmployerProfileForm, JobForm
import os
import json
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Load Admin Credentials from Environment Variables (Security Fix)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Job Seeker Registration View
def job_seeker_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first_name, last_name=last_name
            )
            JobSeekerProfile.objects.create(user=user)
            login(request, user)
            return redirect('job_seeker_dashboard')
        messages.error(request, 'Passwords do not match')
    return render(request, 'job_seeker_register.html')

# Employer Registration View
def employer_register(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = User.objects.create_user(username=email, email=email, password=password)
            EmployerProfile.objects.create(user=user, company_name=company_name)
            login(request, user)
            return redirect('employer_dashboard')
        messages.error(request, 'Passwords do not match')
    return render(request, 'employer_register.html')

# User Login View
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if JobSeekerProfile.objects.filter(user=user).exists():
                return redirect('job_seeker_dashboard')
            elif EmployerProfile.objects.filter(user=user).exists():
                return redirect('employer_dashboard')
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

# Admin Login View
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user, created = User.objects.get_or_create(username=ADMIN_USERNAME, is_superuser=True, is_staff=True)
            if created:
                user.set_password(ADMIN_PASSWORD)
                user.save()
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid admin credentials')
    return render(request, 'admin_login.html')

# Admin Dashboard View
@staff_member_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Get user statistics
    total_users = User.objects.count()
    total_employers = EmployerProfile.objects.count()
    total_job_seekers = JobSeekerProfile.objects.count()
    
    # Get job statistics
    total_jobs = Job.objects.count()
    pending_jobs = Job.objects.filter(approval_status='pending').select_related('company').order_by('-posted_at')
    approved_jobs = Job.objects.filter(approval_status='approved').select_related('company').order_by('-posted_at')[:5]
    
    # Get application statistics
    total_applications = JobApplication.objects.count()
    recent_applications = JobApplication.objects.select_related('job', 'applicant').order_by('-applied_at')[:5]
    
    # Get all users for management
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'total_users': total_users,
        'total_employers': total_employers,
        'total_job_seekers': total_job_seekers,
        'total_jobs': total_jobs,
        'pending_jobs': pending_jobs,
        'approved_jobs': approved_jobs,
        'total_applications': total_applications,
        'applications': recent_applications,
        'users': users,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user != request.user:  # Prevent self-deletion
            user.delete()
            messages.success(request, 'User deleted successfully.')
        else:
            messages.error(request, 'You cannot delete your own account.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('admin_dashboard')

# Logout Views
def user_logout(request):
    logout(request)
    return redirect('login')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# Dashboards
def job_seeker_dashboard(request):
    # Get all categories
    categories = Category.objects.all()
    
    # Get jobs grouped by category (only approved jobs)
    jobs_by_category = {}
    for category in categories:
        jobs = Job.objects.filter(
            is_active=True,
            approval_status='approved',
            category=category
        ).select_related('company').order_by('-posted_at')[:3]  # Show 3 jobs per category
        
        if jobs.exists():
            jobs_by_category[category] = jobs
    
    # Get dashboard statistics
    candidates_count = JobSeekerProfile.objects.count()
    jobs_count = Job.objects.filter(is_active=True, approval_status='approved').count()
    jobs_filled = JobApplication.objects.filter(status='Accepted').count()
    companies_count = EmployerProfile.objects.count()
    
    context = {
        'categories': categories,
        'jobs_by_category': jobs_by_category,
        'candidates_count': candidates_count,
        'jobs_count': jobs_count,
        'jobs_filled': jobs_filled,
        'companies_count': companies_count
    }

    # Add user-specific data if authenticated
    if request.user.is_authenticated:
        try:
            profile = JobSeekerProfile.objects.get(user=request.user)
            saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
            recent_applications = JobApplication.objects.filter(
                applicant=request.user
            ).select_related('job').order_by('-applied_at')[:5]
            
            context.update({
                'profile': profile,
                'saved_jobs': saved_jobs,
                'recent_applications': recent_applications
            })
        except JobSeekerProfile.DoesNotExist:
            if hasattr(request.user, 'employerprofile'):
                return redirect('employer_dashboard')
            elif request.user.is_superuser:
                return redirect('admin_dashboard')
    
    return render(request, 'job_seeker_dashboard.html', context)

@login_required
def update_job_seeker_profile(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    edit_mode = request.GET.get('edit', False)
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('job_seeker_profile')
    else:
        form = JobSeekerProfileForm(instance=profile)
    
    return render(request, 'career/job_seeker_profile.html', {
        'form': form,
        'profile': profile,
        'edit_mode': edit_mode
    })

@login_required
def employer_dashboard(request):
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
        jobs = Job.objects.filter(company=employer_profile).order_by('-posted_at')
        recent_applications = JobApplication.objects.filter(
            job__company=employer_profile
        ).select_related('job', 'applicant').order_by('-applied_at')[:5]
        
        # Calculate application statistics
        total_applications = JobApplication.objects.filter(
            job__company=employer_profile
        ).count()
        pending_applications = JobApplication.objects.filter(
            job__company=employer_profile,
            status='Pending'
        ).count()
        accepted_applications = JobApplication.objects.filter(
            job__company=employer_profile,
            status='Accepted'
        ).count()
        
        company_reviews = CompanyReview.objects.filter(
            company=employer_profile
        ).select_related('reviewer').order_by('-created_at')[:5]
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Employer profile not found.')
        return redirect('login')
    
    return render(request, 'employer_dashboard.html', {
        'employer_profile': employer_profile,
        'jobs': jobs,
        'recent_applications': recent_applications,
        'company_reviews': company_reviews,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
    })

@login_required
def post_job(request):
    if not hasattr(request.user, 'employerprofile'):
        messages.error(request, 'You must be an employer to post jobs.')
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.employerprofile  # Set the company field
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('employer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'career/post_job.html', context)

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    SavedJob.objects.get_or_create(user=request.user, job=job)
    return JsonResponse({'status': 'success'})

@login_required
def unsave_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    SavedJob.objects.filter(user=request.user, job=job).delete()
    return JsonResponse({'status': 'success'})

@login_required
def review_company(request, company_id):
    company = get_object_or_404(EmployerProfile, id=company_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        CompanyReview.objects.create(
            company=company,
            reviewer=request.user,
            rating=rating,
            review_text=review_text
        )
        messages.success(request, 'Review submitted successfully!')
        return redirect('company_profile', company_id=company.id)
    return render(request, 'career/review_company.html', {'company': company})

@login_required
def company_profile(request, company_id):
    company = get_object_or_404(EmployerProfile, id=company_id)
    reviews = CompanyReview.objects.filter(company=company).select_related('reviewer')
    active_jobs = Job.objects.filter(company=company, is_active=True)
    return render(request, 'career/company_profile.html', {
        'company': company,
        'reviews': reviews,
        'active_jobs': active_jobs
    })

@login_required
@require_http_methods(["POST"])
def update_application_status(request, application_id):
    try:
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if the logged-in user is the employer of this job
        if application.job.company.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Parse JSON data
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = dict(JobApplication.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
        
        # Update status
        application.status = new_status
        application.save()
        
        # Create notification for the applicant
        Notification.objects.create(
            user=application.applicant,
            notification_type='application_status',
            title='Application Status Updated',
            message=f'Your application for {application.job.title} has been {new_status.lower()}'
        )
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

# Job Applications
@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied for this job
    existing_application = JobApplication.objects.filter(job=job, applicant=request.user).first()
    if existing_application:
        messages.warning(request, "You have already applied for this job!")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Create notification for the recruiter
            Notification.objects.create(
                user=job.company.user,  # The recruiter
                notification_type='application_status',
                title='New Job Application',
                message=f'A new application has been submitted for the job "{job.title}" by {request.user.get_full_name()}.'
            )
            
            messages.success(request, "Application submitted successfully!")
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobApplicationForm()
    return render(request, 'career/job_application.html', {'form': form, 'job': job})

@login_required
def applied_jobs(request):
    # Get filter status from query parameters
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related(
        'job',
        'job__company'
    ).prefetch_related(
        'interviews'
    ).order_by('-applied_at')
    
    # Apply status filter if not 'all'
    if status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Get application statistics
    total_applications = applications.count()
    status_counts = {
        'pending': applications.filter(status='Pending').count(),
        'reviewed': applications.filter(status='Reviewed').count(),
        'shortlisted': applications.filter(status='Shortlisted').count(),
        'interview': applications.filter(status='Interview').count(),
        'accepted': applications.filter(status='Accepted').count(),
        'rejected': applications.filter(status='Rejected').count()
    }
    
    return render(request, 'career/application_tracking.html', {
        'applications': applications,
        'status_filter': status_filter,
        'total_applications': total_applications,
        'status_counts': status_counts
    })

# Job Search
def job_search(request):
    query = request.GET.get('q', '')
    job_type = request.GET.get('job_type', '')
    experience_level = request.GET.get('experience_level', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')
    
    # Only show active and approved jobs
    jobs = Job.objects.filter(is_active=True, approval_status='approved').select_related('company')
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__company_name__icontains=query)
        )
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(category_id=category)
    
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    return render(request, 'career/job_search.html', {
        'jobs': jobs,
        'filters': {
            'query': query,
            'job_type': job_type,
            'experience_level': experience_level,
            'location': location,
            'category': category
        },
        'categories': Category.objects.all()
    })

# Admin Job Management
@staff_member_required
def manage_jobs(request):
    return render(request, "career/manage_jobs.html", {"jobs": Job.objects.all()})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the user is the owner of the job
    if job.company.user != request.user:
        messages.error(request, "You don't have permission to delete this job.")
        return redirect('job_detail', job_id=job_id)
    
    # Get all affected users before deletion
    applicants = User.objects.filter(applications__job=job)
    saved_by_users = User.objects.filter(saved_jobs__job=job)
    
    # Delete the job (this will cascade delete related records)
    job.delete()
    
    # Create notifications for affected users
    for user in applicants:
        Notification.objects.create(
            user=user,
            notification_type='job_deleted',
            title='Job Deleted',
            message=f'The job "{job.title}" you applied for has been deleted by the employer.'
        )
    
    for user in saved_by_users:
        Notification.objects.create(
            user=user,
            notification_type='job_deleted',
            title='Job Deleted',
            message=f'The job "{job.title}" you saved has been deleted by the employer.'
        )
    
    messages.success(request, "Job has been deleted successfully.")
    return redirect('employer_dashboard')

@staff_member_required
def manage_applications(request):
    applications = JobApplication.objects.select_related("job", "applicant").all()
    return render(request, "career/manage_applications.html", {"applications": applications})

# Home and General Pages
def home(request):
    # Only show active and approved jobs in featured jobs
    featured_jobs = Job.objects.filter(
        is_active=True,
        approval_status='approved'
    ).order_by('-posted_at')[:6]
    
    top_companies = EmployerProfile.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating')[:5]
    
    return render(request, 'career/home.html', {
        'featured_jobs': featured_jobs,
        'top_companies': top_companies
    })

# About and Contact Pages
def about(request):
    return render(request, 'career/about.html')

def contact(request):
    if request.method == 'POST':
        # Here you can add logic to handle contact form submission
        # For example, sending an email or saving to database
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('contact')
    return render(request, 'career/contact.html')

# Job Management
def job_list(request):
    jobs = Job.objects.filter(
        deadline__gte=timezone.now().date()
    ).select_related('company').order_by('-created_at')
    
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    return render(request, 'career/job_list.html', {
        'jobs': jobs,
        'categories': Category.objects.all()
    })

def job_detail(request, job_id):
    # Only allow viewing approved jobs unless user is the employer or admin
    job = get_object_or_404(Job, id=job_id)
    
    if not job.approval_status == 'approved' and not (
        request.user.is_superuser or 
        (request.user.is_authenticated and hasattr(request.user, 'employerprofile') and request.user.employerprofile == job.company)
    ):
        messages.error(request, 'This job posting is not available.')
        return redirect('job_search')
    
    is_saved = False
    is_employer = hasattr(request.user, 'employerprofile')
    is_job_seeker = hasattr(request.user, 'jobseekerprofile')
    has_applied = False
    
    if request.user.is_authenticated:
        if is_job_seeker:
            is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
            has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    
    # Only show approved jobs in similar jobs
    similar_jobs = Job.objects.filter(
        category=job.category,
        is_active=True,
        approval_status='approved'
    ).exclude(id=job.id)[:3]
    
    return render(request, 'career/job_detail.html', {
        'job': job,
        'is_saved': is_saved,
        'is_employer': is_employer,
        'is_job_seeker': is_job_seeker,
        'has_applied': has_applied,
        'similar_jobs': similar_jobs
    })

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company__user=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'career/edit_job.html', {'form': form, 'job': job})

# Company Management
@login_required
def edit_company_profile(request, company_id):
    company = get_object_or_404(EmployerProfile, id=company_id, user=request.user)
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company profile updated successfully!')
            return redirect('company_profile', company_id=company.id)
    else:
        form = EmployerProfileForm(instance=company)
    return render(request, 'career/edit_company_profile.html', {'form': form, 'company': company})

# Job Applications
@login_required
def employer_applications(request):
    if not hasattr(request.user, 'employerprofile'):
        messages.error(request, 'You must be an employer to view applications.')
        return redirect('home')
    
    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Base queryset for applications to the employer's jobs
    applications = JobApplication.objects.filter(
        job__company__user=request.user
    ).select_related(
        'job',
        'applicant',
        'applicant__jobseekerprofile'
    ).order_by('-applied_at')
    
    # Apply search filter if query exists
    if search_query:
        applications = applications.filter(
            Q(applicant__first_name__icontains=search_query) |
            Q(applicant__last_name__icontains=search_query) |
            Q(applicant__username__icontains=search_query)
        )
    
    # Get filter type from query parameters
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Get job filter from query parameters
    job_filter = request.GET.get('job', 'all')
    if job_filter != 'all':
        applications = applications.filter(job_id=job_filter)
    
    # Get active jobs for the filter dropdown
    active_jobs = Job.objects.filter(
        company__user=request.user,
        is_active=True
    ).order_by('-posted_at')
    
    return render(request, 'career/employer_applications.html', {
        'applications': applications,
        'active_jobs': active_jobs,
        'status_filter': status_filter,
        'job_filter': job_filter,
        'search_query': search_query
    })

@login_required
def view_my_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    return render(request, 'career/view_application.html', {
        'application': application
    })

@login_required
def view_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    # Check if user is the employer of this job
    if application.job.company.user != request.user:
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('employer_applications')
    
    return render(request, 'career/view_application.html', {
        'application': application
    })

# Saved Jobs
@login_required
def saved_jobs(request):
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job', 'job__company')
    paginator = Paginator(saved_jobs, 10)
    page = request.GET.get('page')
    saved_jobs = paginator.get_page(page)
    
    return render(request, 'career/saved_jobs.html', {
        'saved_jobs': saved_jobs
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        job.approval_status = 'approved'
        job.approved_at = timezone.now()
        job.approved_by = request.user
        job.save()
        
        # Send notification to employer
        Notification.objects.create(
            user=job.company.user,
            notification_type='application_status',
            title='Job Approved',
            message=f'Your job posting "{job.title}" has been approved and is now visible to job seekers.'
        )
        
        messages.success(request, 'Job has been approved successfully.')
    except Job.DoesNotExist:
        messages.error(request, 'Job not found.')
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        job.approval_status = 'rejected'
        job.save()
        
        # Send notification to employer
        Notification.objects.create(
            user=job.company.user,
            notification_type='application_status',
            title='Job Rejected',
            message=f'Your job posting "{job.title}" has been rejected. Please review and update the posting.'
        )
        
        messages.success(request, 'Job has been rejected.')
    except Job.DoesNotExist:
        messages.error(request, 'Job not found.')
    
    return redirect('admin_dashboard')

# Interview Management
@login_required
def schedule_interview(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if user is the employer
    if application.job.company.user != request.user:
        messages.error(request, 'You do not have permission to schedule interviews.')
        return redirect('employer_applications')
    
    if request.method == 'POST':
        try:
            scheduled_date = timezone.datetime.strptime(request.POST.get('scheduled_date'), '%Y-%m-%dT%H:%M')
            scheduled_date = timezone.make_aware(scheduled_date)  # Make timezone-aware
            duration = int(request.POST.get('duration', 60))
            interview_type = request.POST.get('interview_type')
            location_or_link = request.POST.get('location_or_link')
            notes = request.POST.get('notes')
            
            interview = Interview.objects.create(
                application=application,
                scheduled_date=scheduled_date,
                duration=duration,
                interview_type=interview_type,
                location_or_link=location_or_link,
                notes=notes
            )
            
            # Create notification for the applicant
            Notification.objects.create(
                user=application.applicant,
                notification_type='interview',
                title='Interview Scheduled',
                message=f'An interview has been scheduled for {application.job.title} on {scheduled_date.strftime("%B %d, %Y at %I:%M %p")}.'
            )
            
            # Try to send email notifications, but don't fail if it doesn't work
            try:
                send_interview_notifications(interview)
            except Exception as e:
                # Log the error but don't show it to the user
                print(f"Failed to send interview notification email: {str(e)}")
                messages.warning(request, 'Interview scheduled successfully, but there was an issue sending email notifications.')
            
            messages.success(request, 'Interview scheduled successfully!')
            return redirect('view_application', application_id=application.id)
        except (ValueError, TypeError) as e:
            messages.error(request, 'Invalid date format or duration. Please try again.')
            return render(request, 'career/schedule_interview.html', {
                'application': application
            })
    
    return render(request, 'career/schedule_interview.html', {
        'application': application
    })

@login_required
def manage_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    
    # Check if user is either the employer or the applicant
    if interview.application.job.company.user != request.user and interview.application.applicant != request.user:
        messages.error(request, 'You do not have permission to manage this interview.')
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'reschedule':
            try:
                scheduled_date = timezone.datetime.strptime(request.POST.get('scheduled_date'), '%Y-%m-%dT%H:%M')
                scheduled_date = timezone.make_aware(scheduled_date)  # Make timezone-aware
                duration = int(request.POST.get('duration', 60))
                interview_type = request.POST.get('interview_type')
                location_or_link = request.POST.get('location_or_link')
                notes = request.POST.get('notes')
                
                # Update interview details
                interview.scheduled_date = scheduled_date
                interview.duration = duration
                interview.interview_type = interview_type
                interview.location_or_link = location_or_link
                interview.notes = notes
                interview.status = 'rescheduled'
                interview.save()
                
                # Create notification for the applicant
                Notification.objects.create(
                    user=interview.application.applicant,
                    notification_type='interview',
                    title='Interview Rescheduled',
                    message=f'The interview for {interview.application.job.title} has been rescheduled to {scheduled_date.strftime("%B %d, %Y at %I:%M %p")}.'
                )
                
                # Try to send email notifications
                try:
                    send_interview_reschedule_notification(interview)
                except Exception as e:
                    print(f"Failed to send interview reschedule notification email: {str(e)}")
                    messages.warning(request, 'Interview rescheduled successfully, but there was an issue sending email notifications.')
                
                messages.success(request, 'Interview rescheduled successfully!')
                return redirect('view_application', application_id=interview.application.id)
                
            except (ValueError, TypeError) as e:
                messages.error(request, 'Invalid date format or duration. Please try again.')
                return render(request, 'career/reschedule_interview.html', {
                    'interview': interview
                })
        
        elif action == 'cancel':
            interview.status = 'cancelled'
            interview.save()
            
            # Create notification for the applicant
            Notification.objects.create(
                user=interview.application.applicant,
                notification_type='interview',
                title='Interview Cancelled',
                message=f'The interview for {interview.application.job.title} has been cancelled.'
            )
            
            # Try to send email notifications
            try:
                send_interview_cancellation_notification(interview)
            except Exception as e:
                print(f"Failed to send interview cancellation notification email: {str(e)}")
            
            messages.success(request, 'Interview cancelled successfully!')
            return redirect('view_application', application_id=interview.application.id)
        
        elif action == 'complete':
            interview.status = 'completed'
            interview.save()
            messages.success(request, 'Interview marked as completed!')
            return redirect('view_application', application_id=interview.application.id)
    
    # If it's a GET request, show the rescheduling form
    return render(request, 'career/reschedule_interview.html', {
        'interview': interview
    })

@login_required
def submit_interview_feedback(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    
    # Check if user is the employer
    if interview.application.job.company.user != request.user:
        messages.error(request, 'You do not have permission to submit feedback.')
        return redirect('home')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')
        
        InterviewFeedback.objects.create(
            interview=interview,
            interviewer=request.user,
            rating=rating,
            feedback_text=feedback_text
        )
        
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('view_application', application_id=interview.application.id)
    
    return render(request, 'career/submit_feedback.html', {
        'interview': interview
    })

def send_interview_notifications(interview):
    # Send to applicant
    send_email(
        subject='Interview Scheduled',
        template='emails/interview_scheduled.html',
        context={'interview': interview},
        recipient_list=[interview.application.applicant.email]
    )
    
    # Send to employer
    send_email(
        subject='Interview Scheduled',
        template='emails/interview_scheduled.html',
        context={'interview': interview},
        recipient_list=[interview.application.job.company.user.email]
    )

def send_interview_reschedule_notification(interview):
    # Send to applicant
    send_email(
        subject='Interview Rescheduled',
        template='emails/interview_rescheduled.html',
        context={'interview': interview},
        recipient_list=[interview.application.applicant.email]
    )
    
    # Send to employer
    send_email(
        subject='Interview Rescheduled',
        template='emails/interview_rescheduled.html',
        context={'interview': interview},
        recipient_list=[interview.application.job.company.user.email]
    )

def send_interview_cancellation_notification(interview):
    # Send to applicant
    send_email(
        subject='Interview Cancelled',
        template='emails/interview_cancelled.html',
        context={'interview': interview},
        recipient_list=[interview.application.applicant.email]
    )
    
    # Send to employer
    send_email(
        subject='Interview Cancelled',
        template='emails/interview_cancelled.html',
        context={'interview': interview},
        recipient_list=[interview.application.job.company.user.email]
    )

def send_email(subject, template, context, recipient_list):
    try:
        html_message = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',
            from_email=None,  # Use default from email
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True  # Don't raise an exception if email fails
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        # Don't raise the exception, just log it

@login_required
def get_notifications(request):
    # Get filter type from query parameters
    notification_type = request.GET.get('type', 'all')
    
    # Base queryset
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        'user'
    ).order_by('-created_at')
    
    # Apply type filter if not 'all'
    if notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)
    
    # Mark notifications as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    
    # Determine which template to use based on user type
    if hasattr(request.user, 'employerprofile'):
        template = 'career/recruiter_notifications.html'
    else:
        template = 'career/notifications.html'
    
    return render(request, template, {
        'notifications': notifications,
        'notification_type': notification_type
    })

@login_required
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        messages.success(request, 'Notification deleted successfully.')
    except Notification.DoesNotExist:
        messages.error(request, 'Notification not found.')
    return redirect('notifications')

@login_required
def delete_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, 'All notifications have been cleared.')
    return redirect('notifications')

def cleanup_expired_jobs():
    """
    Function to automatically delete jobs that have passed their deadline.
    This should be called by a scheduled task (e.g., cron job or Celery beat).
    """
    expired_jobs = Job.objects.filter(deadline__lt=timezone.now().date())
    count = expired_jobs.count()
    expired_jobs.delete()
    return count

@login_required
def employer_jobs(request):
    if not hasattr(request.user, 'employerprofile'):
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    
    jobs = Job.objects.filter(
        company=request.user.employerprofile
    ).select_related('company').order_by('-created_at')
    
    # ... rest of the existing employer_jobs view code ...
