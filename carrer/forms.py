from django import forms
from django.utils import timezone
from .models import (
    JobSeekerProfile, EmployerProfile, Job, 
    JobApplication, CompanyReview
)

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            'profile_picture', 'phone', 'skills', 'resume', 
            'experience', 'education', 'location', 'linkedin',
            'expected_salary', 'preferred_job_type', 'preferred_location'
        ]
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List your skills'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your work experience'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your degree & university'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your city/country'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Profile URL'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your phone number'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected salary'}),
            'preferred_job_type': forms.Select(attrs={'class': 'form-control'}),
            'preferred_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preferred job location'}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'phone', 'profile_picture', 'company_description',
            'company_website', 'industry', 'company_size', 'founded_year'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company phone number'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Company description'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Company website'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry'}),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year founded'}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'location', 'salary_range',
            'job_type', 'required_skills', 'experience_level', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job location'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $50,000 - $70,000'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'required_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Required skills'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_type'].choices = [
            ('', 'Select job type'),
            ('Full-time', 'Full-time'),
            ('Part-time', 'Part-time'),
            ('Contract', 'Contract'),
            ('Internship', 'Internship'),
        ]
        self.fields['experience_level'].choices = [
            ('', 'Select experience level'),
            ('Entry', 'Entry Level'),
            ('Mid', 'Mid Level'),
            ('Senior', 'Senior Level'),
            ('Lead', 'Lead'),
            ('Manager', 'Manager'),
        ]

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline

    def clean_salary_range(self):
        salary_range = self.cleaned_data.get('salary_range')
        if salary_range:
            try:
                # Basic validation for salary range format
                if not any(c.isdigit() for c in salary_range):
                    raise forms.ValidationError("Please enter a valid salary range")
            except:
                raise forms.ValidationError("Please enter a valid salary range")
        return salary_range

    def clean_required_skills(self):
        required_skills = self.cleaned_data.get('required_skills')
        if not required_skills:
            raise forms.ValidationError("Please specify required skills")
        return required_skills

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter', 'expected_salary', 'availability_date', 'notes']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write a brief cover letter...'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected salary'}),
            'availability_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

    def clean_availability_date(self):
        date = self.cleaned_data.get('availability_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Availability date cannot be in the past")
        return date

class CompanyReviewForm(forms.ModelForm):
    class Meta:
        model = CompanyReview
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review...'})
        }