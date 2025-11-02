"""
URL configuration for administration app.
"""
from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('logout/', views.custom_logout_view, name='logout'),
]