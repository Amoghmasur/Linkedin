from django.db import models

class ScrapedData1(models.Model):
    profile_url=models.URLField(max_length=250)
    name = models.CharField(max_length=255)
    works_at = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    exp = models.TextField()
    about = models.TextField()
    uname = models.CharField(max_length=255)
    education = models.TextField()

class CompanyData1(models.Model):
    comp_name=models.CharField(max_length=255,primary_key=True)
    website=models.URLField(max_length=250)
    industry=models.TextField()
    company_size=models.TextField()
    headquarter=models.TextField()
    founded=models.CharField(max_length=255)
    foll=models.CharField(max_length=255)
    specialties=models.TextField()


class EmployeeDetail1(models.Model):
    e_name=models.CharField(max_length=255)
    e_head=models.TextField()
    e_link=models.TextField()
    company = models.ForeignKey(CompanyData1, on_delete=models.CASCADE, related_name='employees')
    



