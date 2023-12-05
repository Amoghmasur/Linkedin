from django.contrib import admin
from django.urls import path
from Linkapp import views

urlpatterns = [
    path('home', views.user_page),
    path('comp', views.company_page),
    path('scrape',views.user_detials_scrape, name='user_detials_scrape'),
    path('login',views.user_login),
    path('register',views.register),
    path('logout',views.user_logout),
    path('',views.user_login),
    path('company',views.company_page),
    path('search',views.searchcomp)
]
