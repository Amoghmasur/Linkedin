# Generated by Django 4.2.5 on 2023-09-25 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Linkapp', '0006_delete_employeedetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comp_name', models.CharField(max_length=255)),
                ('website', models.URLField(max_length=250)),
                ('emp_info', models.TextField()),
            ],
        ),
    ]
