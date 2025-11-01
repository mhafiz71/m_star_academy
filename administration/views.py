from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'administration/dashboard.html'

class ApplicationListView(StaffRequiredMixin, TemplateView):
    template_name = 'administration/application_list.html'

class ApplicationDetailView(StaffRequiredMixin, TemplateView):
    template_name = 'administration/application_detail.html'
