from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse
from .models import Application
from .forms import ApplicationForm


class ApplicationCreateView(CreateView):
    """
    View for handling application form submission
    """
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/apply.html'
    
    def form_valid(self, form):
        """Handle successful form submission"""
        try:
            # Save the application
            application = form.save()
            
            # Add success message
            messages.success(
                self.request, 
                f'Application submitted successfully! Your reference number is {application.reference_number}'
            )
            
            # Redirect to success page with reference number
            return redirect('applications:success', ref_number=application.reference_number)
            
        except Exception as e:
            # Handle any errors during save
            messages.error(
                self.request, 
                'An error occurred while submitting your application. Please try again.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


class ApplicationSuccessView(TemplateView):
    """
    View for displaying application success page
    """
    template_name = 'applications/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the reference number from URL
        ref_number = kwargs.get('ref_number')
        
        if ref_number:
            try:
                # Get the application to verify it exists
                application = get_object_or_404(Application, reference_number=ref_number)
                context['application'] = application
                context['reference_number'] = ref_number
            except Application.DoesNotExist:
                context['error'] = 'Application not found.'
        else:
            context['error'] = 'No reference number provided.'
        
        return context
