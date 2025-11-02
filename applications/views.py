from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from django.http import Http404
import logging
from .models import Application
from .forms import ApplicationForm

logger = logging.getLogger(__name__)


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
            
            # Log successful submission
            logger.info(
                f'Application submitted successfully: {application.reference_number} '
                f'for {application.student_full_name}'
            )
            
            # Add success message
            messages.success(
                self.request, 
                f'Application submitted successfully! Your reference number is {application.reference_number}'
            )
            
            # Redirect to success page with reference number
            return redirect('applications:success', ref_number=application.reference_number)
            
        except ValidationError as e:
            # Handle validation errors
            logger.warning(f'Application validation error: {e}')
            messages.error(
                self.request, 
                'Please check your information and try again.'
            )
            return self.form_invalid(form)
            
        except IntegrityError as e:
            # Handle database integrity errors (e.g., duplicate reference numbers)
            logger.error(f'Database integrity error during application submission: {e}')
            messages.error(
                self.request, 
                'A technical error occurred. Please try submitting your application again.'
            )
            return self.form_invalid(form)
            
        except DatabaseError as e:
            # Handle general database errors
            logger.error(f'Database error during application submission: {e}')
            messages.error(
                self.request, 
                'We are experiencing technical difficulties. Please try again in a few minutes.'
            )
            return self.form_invalid(form)
            
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f'Unexpected error during application submission: {e}', exc_info=True)
            messages.error(
                self.request, 
                'An unexpected error occurred. Our technical team has been notified. Please try again later.'
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
                
                # Log successful access to success page
                logger.info(f'Success page accessed for application: {ref_number}')
                
            except Http404:
                logger.warning(f'Attempt to access success page with invalid reference: {ref_number}')
                context['error'] = 'Application not found. Please check your reference number.'
            except Exception as e:
                logger.error(f'Error accessing success page for {ref_number}: {e}')
                context['error'] = 'An error occurred while retrieving your application information.'
        else:
            logger.warning('Success page accessed without reference number')
            context['error'] = 'No reference number provided.'
        
        return context
