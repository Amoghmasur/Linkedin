# Generated by Django 4.2.5 on 2023-10-03 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Linkapp', '0016_alter_employeedetail_company'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CompanyData',
            new_name='CompanyData1',
        ),
        migrations.RenameModel(
            old_name='EmployeeDetail',
            new_name='EmployeeDetail1',
        ),
    ]
