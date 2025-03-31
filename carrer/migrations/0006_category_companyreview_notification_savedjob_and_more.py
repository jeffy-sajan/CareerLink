# Generated by Django 5.1.6 on 2025-03-23 09:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrer', '0005_alter_job_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CompanyReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])),
                ('review_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('application_status', 'Application Status Update'), ('new_job', 'New Job Posted'), ('deadline', 'Application Deadline'), ('interview', 'Interview Invitation')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SavedJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='job',
            name='salary',
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='company_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='company_size',
            field=models.CharField(blank=True, choices=[('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'), ('201-500', '201-500'), ('501-1000', '501-1000'), ('1000+', '1000+')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='company_website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='founded_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employerprofile',
            name='industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='experience_level',
            field=models.CharField(choices=[('Entry', 'Entry Level'), ('Mid', 'Mid Level'), ('Senior', 'Senior Level'), ('Lead', 'Lead'), ('Manager', 'Manager')], default='Entry', max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract'), ('Internship', 'Internship')], default='Full-time', max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='required_skills',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_range',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='availability_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='expected_salary',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='jobseekerprofile',
            name='expected_salary',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='jobseekerprofile',
            name='preferred_job_type',
            field=models.CharField(blank=True, choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'), ('Contract', 'Contract'), ('Internship', 'Internship')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='jobseekerprofile',
            name='preferred_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='jobapplication',
            unique_together={('job', 'applicant')},
        ),
        migrations.AddIndex(
            model_name='employerprofile',
            index=models.Index(fields=['industry'], name='carrer_empl_industr_cd8d76_idx'),
        ),
        migrations.AddIndex(
            model_name='employerprofile',
            index=models.Index(fields=['company_size'], name='carrer_empl_company_d5dfb6_idx'),
        ),
        migrations.AddIndex(
            model_name='jobapplication',
            index=models.Index(fields=['status'], name='carrer_joba_status_2d368b_idx'),
        ),
        migrations.AddIndex(
            model_name='jobapplication',
            index=models.Index(fields=['applied_at'], name='carrer_joba_applied_a90101_idx'),
        ),
        migrations.AddIndex(
            model_name='jobseekerprofile',
            index=models.Index(fields=['location'], name='carrer_jobs_locatio_b79f60_idx'),
        ),
        migrations.AddIndex(
            model_name='jobseekerprofile',
            index=models.Index(fields=['preferred_job_type'], name='carrer_jobs_preferr_e34e8a_idx'),
        ),
        migrations.AddField(
            model_name='job',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs', to='carrer.category'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['location'], name='carrer_job_locatio_d410ad_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['job_type'], name='carrer_job_job_typ_f2133b_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['experience_level'], name='carrer_job_experie_bb9a96_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['is_active'], name='carrer_job_is_acti_fd2c3e_idx'),
        ),
        migrations.AddField(
            model_name='companyreview',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='carrer.employerprofile'),
        ),
        migrations.AddField(
            model_name='companyreview',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='savedjob',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_jobs', to='carrer.job'),
        ),
        migrations.AddField(
            model_name='savedjob',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_jobs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='companyreview',
            unique_together={('company', 'reviewer')},
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['is_read'], name='carrer_noti_is_read_6f18c1_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['created_at'], name='carrer_noti_created_e52cb2_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='savedjob',
            unique_together={('job', 'user')},
        ),
    ]
