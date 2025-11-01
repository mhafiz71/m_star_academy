from django.shortcuts import render
from django.views.generic import CreateView, TemplateView

class ApplicationCreateView(TemplateView):
    template_name = 'applications/apply.html'

class ApplicationSuccessView(TemplateView):
    template_name = 'applications/success.html'
