from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from applications.models import Application
from core.email_service import EmailService
from datetime import date


class EmailServiceTest(TestCase):
    """
    Test cases for email service functionality
    """
    
    def setUp(self):
        """Set up test data"""
        self.application = Application.objects.create(
            student_first_name='John',
            student_last_name='Doe',
            student_date_of_birth=date(2015, 5, 15),
            student_gender='M',
            student_place_of_birth='Tamale',
            grade_applying_for='primary_1',
            guardian_first_name='Jane',
            guardian_last_name='Doe',
            guardian_relationship='mother',
            guardian_phone='+233241234567',
            guardian_email='jane.doe@example.com',
            guardian_address='123 Main St, Tamale',
            guardian_occupation='Teacher',
            emergency_contact_name='John Smith',
            emergency_contact_phone='+233241234568',
            emergency_contact_relationship='uncle',
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_application_confirmation(self):
        """Test sending application confirmation email"""
        # Clear any existing emails
        mail.outbox = []
        
        # Send confirmation email
        success = EmailService.send_application_confirmation(self.application)
        
        # Check that email was sent
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn(self.application.reference_number, email.subject)
        self.assertEqual(email.to, [self.application.guardian_email])
        self.assertIn('Morning Star Academy', email.body)
        self.assertIn(self.application.student_full_name, email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_status_update_approved(self):
        """Test sending status update email for approved application"""
        mail.outbox = []
        
        # Send status update email
        success = EmailService.send_status_update(self.application, 'pending', 'approved')
        
        # Check that email was sent
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Congratulations', email.subject)
        self.assertEqual(email.to, [self.application.guardian_email])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_verification_email(self):
        """Test sending email verification email"""
        mail.outbox = []
        
        # Send verification email
        success = EmailService.send_verification_email(self.application)
        
        # Check that email was sent
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Verify Your Email', email.subject)
        self.assertEqual(email.to, [self.application.guardian_email])
    
    def test_email_template_context(self):
        """Test email template context generation"""
        from core.email_service import EmailTemplateContext
        
        # Test base context
        base_context = EmailTemplateContext.get_base_context()
        self.assertIn('school_name', base_context)
        self.assertEqual(base_context['school_name'], 'Morning Star Academy')
        
        # Test application context
        app_context = EmailTemplateContext.get_application_context(self.application)
        self.assertIn('application', app_context)
        self.assertIn('student_name', app_context)
        self.assertEqual(app_context['student_name'], 'John Doe')
        self.assertEqual(app_context['reference_number'], self.application.reference_number)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_sending_failure_handling(self):
        """Test handling of email sending failures"""
        # Test with None application - should handle gracefully
        success = EmailService.send_application_confirmation(None)
        self.assertFalse(success)
        
        # Test with invalid status update
        success = EmailService.send_status_update(self.application, 'pending', 'invalid_status')
        self.assertFalse(success)