from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

class JobSeekerProfile(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    phone = models.CharField(max_length=15, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, blank=True, null=True)
    preferred_location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['preferred_job_type']),
        ]

class EmployerProfile(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-200', '51-200'),
        ('201-500', '201-500'),
        ('501-1000', '501-1000'),
        ('1000+', '1000+'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES, blank=True, null=True)
    founded_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employer: {self.user.username} - {self.company_name}"

    class Meta:
        indexes = [
            models.Index(fields=['industry']),
            models.Index(fields=['company_size']),
        ]

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_categories(cls):
        return [
            {
                'name': 'Information Technology',
                'description': 'Jobs in software development, IT support, and technology'
            },
            {
                'name': 'Healthcare',
                'description': 'Jobs in medical, nursing, and healthcare services'
            },
            {
                'name': 'Finance',
                'description': 'Jobs in banking, accounting, and financial services'
            },
            {
                'name': 'Education',
                'description': 'Jobs in teaching, training, and educational services'
            },
            {
                'name': 'Marketing',
                'description': 'Jobs in advertising, digital marketing, and public relations'
            },
            {
                'name': 'Sales',
                'description': 'Jobs in sales, business development, and account management'
            },
            {
                'name': 'Engineering',
                'description': 'Jobs in mechanical, electrical, and civil engineering'
            },
            {
                'name': 'Customer Service',
                'description': 'Jobs in customer support and service roles'
            },
            {
                'name': 'Human Resources',
                'description': 'Jobs in HR management, recruitment, and employee relations'
            },
            {
                'name': 'Operations',
                'description': 'Jobs in operations management and logistics'
            },
            {
                'name': 'Design',
                'description': 'Jobs in graphic design, UI/UX, and creative roles'
            },
            {
                'name': 'Legal',
                'description': 'Jobs in law, legal services, and compliance'
            },
            {
                'name': 'Manufacturing',
                'description': 'Jobs in production, manufacturing, and industrial roles'
            },
            {
                'name': 'Research',
                'description': 'Jobs in research, analysis, and development'
            },
            {
                'name': 'Other',
                'description': 'Other job categories not listed above'
            }
        ]

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]

    EXPERIENCE_CHOICES = [
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
        ('Lead', 'Lead'),
        ('Manager', 'Manager'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    company = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="jobs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="jobs")
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full-time')
    required_skills = models.TextField(blank=True, null=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default='Entry')
    deadline = models.DateField(null=True, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_jobs')

    def __str__(self):
        return self.title

    def clean(self):
        if self.deadline and self.deadline < timezone.now().date():
            raise ValidationError("Deadline cannot be in the past")

    @property
    def is_visible(self):
        return self.is_active and self.approval_status == 'approved'

    class Meta:
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['job_type']),
            models.Index(fields=['experience_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['approval_status']),
        ]

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

    class Meta:
        unique_together = ['job', 'applicant']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['applied_at']),
        ]

class SavedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_jobs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"

    class Meta:
        unique_together = ['job', 'user']

class CompanyReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    company = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Review for {self.company.company_name} by {self.reviewer.username}"

    class Meta:
        unique_together = ['company', 'reviewer']

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application_status', 'Application Status Update'),
        ('new_job', 'New Job Posted'),
        ('deadline', 'Application Deadline'),
        ('interview', 'Interview Invitation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"

    class Meta:
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

class Interview(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    scheduled_date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes", default=60)
    interview_type = models.CharField(max_length=50, choices=[
        ('phone', 'Phone Interview'),
        ('video', 'Video Call'),
        ('in_person', 'In-Person'),
    ])
    location_or_link = models.CharField(max_length=255, help_text="Physical location or video call link")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reminder_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Interview for {self.application.job.title} - {self.application.applicant.get_full_name()}"

    class Meta:
        ordering = ['scheduled_date']

class InterviewFeedback(models.Model):
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='feedback')
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.interview}"
