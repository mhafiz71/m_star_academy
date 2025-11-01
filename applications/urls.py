"""
URL configuration for applications app.
"""
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.ApplicationCreateView.as_view(), name='apply'),
    path('success/<str:ref_id>/', views.ApplicationSuccessView.as_view(), name='success'),
]