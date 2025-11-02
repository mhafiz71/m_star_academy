"""
URL configuration for applications app.
"""
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.ApplicationCreateView.as_view(), name='apply'),
    path('success/<str:ref_number>/', views.ApplicationSuccessView.as_view(), name='success'),
    path('download/', views.DownloadApplicationView.as_view(), name='download'),
    path('view/<str:ref_number>/', views.view_application, name='view_application'),
]