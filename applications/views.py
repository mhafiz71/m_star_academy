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
from core.email_service import EmailService

logger = logging.getLogger(__name__)


class ApplicationCreateView(CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/apply.html'
    
    def form_valid(self, form):
        try:
            application = form.save()
            
            logger.info(
                f'Application submitted successfully: {application.reference_number} '
                f'for {application.student_full_name}'
            )
            
            # Send confirmation email
            try:
                email_sent = EmailService.send_application_confirmation(application)
                if email_sent:
                    logger.info(f'Confirmation email sent for application {application.reference_number}')
                    email_message = f' A confirmation email has been sent to {application.guardian_email}.'
                else:
                    logger.warning(f'Failed to send confirmation email for application {application.reference_number}')
                    email_message = ' However, the confirmation email could not be sent.'
            except Exception as e:
                logger.error(f'Error sending confirmation email for {application.reference_number}: {e}')
                email_message = ' However, there was an error sending the confirmation email.'
            
            messages.success(
                self.request, 
                f'Application submitted successfully! Your reference number is {application.reference_number}.{email_message}'
            )
            
            return redirect('applications:success', ref_number=application.reference_number)
            
        except ValidationError as e:
            logger.warning(f'Application validation error: {e}')
            messages.error(
                self.request, 
                'Please check your information and try again.'
            )
            return self.form_invalid(form)
            
        except IntegrityError as e:
            logger.error(f'Database integrity error during application submission: {e}')
            messages.error(
                self.request, 
                'A technical error occurred. Please try submitting your application again.'
            )
            return self.form_invalid(form)
            
        except DatabaseError as e:
            logger.error(f'Database error during application submission: {e}')
            messages.error(
                self.request, 
                'We are experiencing technical difficulties. Please try again in a few minutes.'
            )
            return self.form_invalid(form)
            
        except Exception as e:
            logger.error(f'Unexpected error during application submission: {e}', exc_info=True)
            messages.error(
                self.request, 
                'An unexpected error occurred. Our technical team has been notified. Please try again later.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


class ApplicationSuccessView(TemplateView):
    template_name = 'applications/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ref_number = kwargs.get('ref_number')
        
        if ref_number:
            try:
                application = get_object_or_404(Application, reference_number=ref_number)
                context['application'] = application
                context['reference_number'] = ref_number
                
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
