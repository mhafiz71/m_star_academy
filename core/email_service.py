import logging
import uuid
from datetime import datetime, timedelta
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from applications.models import Application

logger = logging.getLogger(__name__)


class EmailService:
    
    @staticmethod
    def send_application_confirmation(application):
        try:
            subject = f"Application Received - Morning Star Academy (Ref: {application.reference_number})"
            
            context = {
                'application': application,
                'school_name': 'Morning Star Academy',
                'school_email': settings.ADMIN_EMAIL,
                'verification_url': EmailService._generate_verification_url(application),
            }
            
            html_content = render_to_string('emails/application_confirmation.html', context)
            text_content = strip_tags(html_content)
            success = EmailService._send_email(
                subject=subject,
                message=text_content,
                html_message=html_content,
                recipient_list=[application.guardian_email],
                email_type='confirmation',
                application=application
            )
            
            if success:
                logger.info(f"Confirmation email sent for application {application.reference_number}")
            
            return success
            
        except Exception as e:
            ref_num = getattr(application, 'reference_number', 'Unknown') if application else 'None'
            logger.error(f"Failed to send confirmation email for {ref_num}: {e}")
            return False
    
    @staticmethod
    def send_status_update(application, old_status, new_status):
        """
        Send email notification when application status changes
        """
        try:
            # Determine email template and subject based on new status
            status_templates = {
                'approved': {
                    'template': 'emails/status_approved.html',
                    'subject': f"Congratulations! Application Approved - Morning Star Academy"
                },
                'rejected': {
                    'template': 'emails/status_rejected.html',
                    'subject': f"Application Update - Morning Star Academy"
                },
                'waitlist': {
                    'template': 'emails/status_waitlist.html',
                    'subject': f"Application Waitlisted - Morning Star Academy"
                }
            }
            
            if new_status not in status_templates:
                logger.warning(f"No email template for status: {new_status}")
                return False
            
            template_info = status_templates[new_status]
            
            # Prepare context
            context = {
                'application': application,
                'old_status': old_status,
                'new_status': new_status,
                'school_name': 'Morning Star Academy',
                'school_email': settings.ADMIN_EMAIL,
                'contact_phone': '+233 XX XXX XXXX',  # Replace with actual phone
            }
            
            # Render email content
            html_content = render_to_string(template_info['template'], context)
            text_content = strip_tags(html_content)
            
            # Send email
            success = EmailService._send_email(
                subject=template_info['subject'],
                message=text_content,
                html_message=html_content,
                recipient_list=[application.guardian_email],
                email_type=f'status_update_{new_status}',
                application=application
            )
            
            if success:
                logger.info(f"Status update email sent for application {application.reference_number}: {old_status} -> {new_status}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send status update email for {application.reference_number}: {e}")
            return False
    
    @staticmethod
    def send_verification_email(application):
        """
        Send email verification email
        """
        try:
            subject = "Please Verify Your Email - Morning Star Academy"
            
            context = {
                'application': application,
                'school_name': 'Morning Star Academy',
                'verification_url': EmailService._generate_verification_url(application),
                'expiry_hours': 24,
            }
            
            html_content = render_to_string('emails/email_verification.html', context)
            text_content = strip_tags(html_content)
            
            success = EmailService._send_email(
                subject=subject,
                message=text_content,
                html_message=html_content,
                recipient_list=[application.guardian_email],
                email_type='verification',
                application=application
            )
            
            if success:
                logger.info(f"Verification email sent for application {application.reference_number}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send verification email for {application.reference_number}: {e}")
            return False
    
    @staticmethod
    def send_reminder_email(application):
        """
        Send reminder email for unverified email addresses
        """
        try:
            subject = "Reminder: Please Verify Your Email - Morning Star Academy"
            
            context = {
                'application': application,
                'school_name': 'Morning Star Academy',
                'verification_url': EmailService._generate_verification_url(application),
                'days_since_submission': (timezone.now() - application.created_at).days,
            }
            
            html_content = render_to_string('emails/email_reminder.html', context)
            text_content = strip_tags(html_content)
            
            success = EmailService._send_email(
                subject=subject,
                message=text_content,
                html_message=html_content,
                recipient_list=[application.guardian_email],
                email_type='reminder',
                application=application
            )
            
            if success:
                logger.info(f"Reminder email sent for application {application.reference_number}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send reminder email for {application.reference_number}: {e}")
            return False
    
    @staticmethod
    def _send_email(subject, message, recipient_list, html_message=None, email_type=None, application=None):
        """
        Internal method to send emails with logging
        """
        try:
            if html_message:
                # Send HTML email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipient_list
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                # Send plain text email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    fail_silently=False
                )
            
            # Log email sending (we'll implement EmailLog model later)
            EmailService._log_email(
                application=application,
                email_type=email_type,
                recipient=recipient_list[0] if recipient_list else '',
                subject=subject,
                success=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            
            # Log failed email
            EmailService._log_email(
                application=application,
                email_type=email_type,
                recipient=recipient_list[0] if recipient_list else '',
                subject=subject,
                success=False,
                error_message=str(e)
            )
            
            return False
    
    @staticmethod
    def _generate_verification_url(application):
        """
        Generate email verification URL (placeholder for now)
        """
        # We'll implement proper token generation later
        token = str(uuid.uuid4())
        return f"http://localhost:8000/verify-email/{token}/"
    
    @staticmethod
    def _log_email(application, email_type, recipient, subject, success, error_message=''):
        """
        Log email sending attempt (placeholder for now)
        """
        # We'll implement EmailLog model later
        logger.info(f"Email log: {email_type} to {recipient} - {'Success' if success else 'Failed'}")
        if error_message:
            logger.error(f"Email error: {error_message}")


class EmailTemplateContext:
    """
    Helper class for generating consistent email template contexts
    """
    
    @staticmethod
    def get_base_context():
        """
        Get base context used in all email templates
        """
        return {
            'school_name': 'Morning Star Academy',
            'school_address': 'Tamale, Gbanyamli, Northern Region, Ghana',
            'school_phone': '+233 XX XXX XXXX',
            'school_email': settings.ADMIN_EMAIL,
            'school_website': 'https://morningstaracademy.edu.gh',
            'current_year': datetime.now().year,
        }
    
    @staticmethod
    def get_application_context(application):
        """
        Get application-specific context
        """
        base_context = EmailTemplateContext.get_base_context()
        base_context.update({
            'application': application,
            'student_name': application.student_full_name,
            'guardian_name': application.guardian_full_name,
            'reference_number': application.reference_number,
            'submission_date': application.created_at.strftime('%B %d, %Y'),
        })
        return base_context