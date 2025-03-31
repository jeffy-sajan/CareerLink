from django.db import migrations

def add_default_categories(apps, schema_editor):
    Category = apps.get_model('carrer', 'Category')
    default_categories = [
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
    
    for category_data in default_categories:
        Category.objects.get_or_create(
            name=category_data['name'],
            defaults={'description': category_data['description']}
        )

def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('carrer', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('carrer', '0007_alter_category_options_remove_category_slug_and_more'),
    ]

    operations = [
        migrations.RunPython(add_default_categories, remove_default_categories),
    ] 