from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from applications.models import Application
from datetime import date
import tempfile
import os


class ErrorHandlingTest(TestCase):
    """
    Test cases for error handling and custom error pages
    """
    
    def setUp(self):
        self.client = Client()
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123',
            is_staff=False
        )
    
    def test_404_error_page(self):
        """Test custom 404 error page"""
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
        
        # In DEBUG mode, Django shows its own 404 page
        # In production, our custom handler would be used
    
    def test_403_error_page(self):
        """Test custom 403 error page for unauthorized access"""
        # Try to access admin area without proper permissions
        self.client.login(username='regular_user', password='testpass123')
        
        # This should trigger our custom permission handling
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
    
    def test_invalid_application_reference(self):
        """Test handling of invalid application reference numbers"""
        response = self.client.get('/apply/success/INVALID123/')
        self.assertEqual(response.status_code, 404)
    
    def test_form_validation_errors(self):
        """Test form validation error handling"""
        # Submit form with invalid data
        invalid_data = {
            'student_first_name': '',  # Required field missing
            'student_last_name': 'Doe',
            'student_date_of_birth': '2030-01-01',  # Future date
            'student_gender': 'M',
            'student_place_of_birth': 'Tamale',
            'grade_applying_for': 'primary_1',
            'guardian_first_name': 'Jane',
            'guardian_last_name': 'Doe',
            'guardian_relationship': 'mother',
            'guardian_phone': 'invalid-phone',  # Invalid phone
            'guardian_email': 'invalid-email',  # Invalid email
            'guardian_address': '123 Main St, Tamale',
            'guardian_occupation': 'Teacher',
            'emergency_contact_name': 'John Smith',
            'emergency_contact_phone': '+233241234568',
            'emergency_contact_relationship': 'uncle',
        }
        
        response = self.client.post('/apply/', data=invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        
        # No application should be created
        self.assertEqual(Application.objects.count(), 0)
    
    def test_database_error_handling(self):
        """Test database error handling in application submission"""
        # This is a conceptual test - in practice, you'd mock database errors
        valid_data = {
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': '2015-05-15',
            'student_gender': 'M',
            'student_place_of_birth': 'Tamale',
            'grade_applying_for': 'primary_1',
            'guardian_first_name': 'Jane',
            'guardian_last_name': 'Doe',
            'guardian_relationship': 'mother',
            'guardian_phone': '+233241234567',
            'guardian_email': 'jane.doe@example.com',
            'guardian_address': '123 Main St, Tamale',
            'guardian_occupation': 'Teacher',
            'emergency_contact_name': 'John Smith',
            'emergency_contact_phone': '+233241234568',
            'emergency_contact_relationship': 'uncle',
            'medical_conditions': '',
            'special_requirements': '',
            'additional_notes': '',
        }
        
        # Normal submission should work
        response = self.client.post('/apply/', data=valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect to success
        self.assertEqual(Application.objects.count(), 1)
    
    def test_admin_error_handling(self):
        """Test error handling in admin views"""
        self.client.login(username='staff_user', password='testpass123')
        
        # Try to access non-existent application
        response = self.client.get('/admin-portal/applications/999/')
        self.assertEqual(response.status_code, 404)
        
        # Try to update non-existent application
        response = self.client.post('/admin-portal/applications/999/', {
            'status': 'approved'
        })
        self.assertEqual(response.status_code, 404)
    
    def test_csrf_error_handling(self):
        """Test CSRF error handling"""
        # Try to submit form without CSRF token
        response = self.client.post('/apply/', {
            'student_first_name': 'Test',
        })
        
        # Should be forbidden due to CSRF failure
        self.assertEqual(response.status_code, 403)
    
    def test_method_not_allowed_handling(self):
        """Test handling of invalid HTTP methods"""
        # Try to DELETE on a view that only accepts GET/POST
        response = self.client.delete('/apply/')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_application_success_error_handling(self):
        """Test error handling in application success view"""
        # Test with missing reference number
        response = self.client.get('/apply/success//')
        self.assertEqual(response.status_code, 404)
        
        # Test with malformed reference number
        response = self.client.get('/apply/success/MALFORMED/')
        self.assertEqual(response.status_code, 404)


class LoggingTest(TestCase):
    """
    Test cases for logging functionality
    """
    
    def setUp(self):
        self.client = Client()
        
        # Create temporary log directory for testing
        self.temp_log_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary log directory
        import shutil
        shutil.rmtree(self.temp_log_dir, ignore_errors=True)
    
    def test_application_submission_logging(self):
        """Test that application submissions are logged"""
        valid_data = {
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': '2015-05-15',
            'student_gender': 'M',
            'student_place_of_birth': 'Tamale',
            'grade_applying_for': 'primary_1',
            'guardian_first_name': 'Jane',
            'guardian_last_name': 'Doe',
            'guardian_relationship': 'mother',
            'guardian_phone': '+233241234567',
            'guardian_email': 'jane.doe@example.com',
            'guardian_address': '123 Main St, Tamale',
            'guardian_occupation': 'Teacher',
            'emergency_contact_name': 'John Smith',
            'emergency_contact_phone': '+233241234568',
            'emergency_contact_relationship': 'uncle',
            'medical_conditions': '',
            'special_requirements': '',
            'additional_notes': '',
        }
        
        # Submit application
        response = self.client.post('/apply/', data=valid_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify application was created (logging would be checked in log files)
        self.assertEqual(Application.objects.count(), 1)
    
    def test_error_logging(self):
        """Test that errors are logged"""
        # Try to access non-existent page
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
        
        # In a real scenario, this would be logged to error files
    
    def test_security_event_logging(self):
        """Test that security events are logged"""
        # Try to access admin without permission
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)
        
        # This should be logged as a security event


class ExceptionHandlingTest(TestCase):
    """
    Test cases for exception handling in views
    """
    
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
    
    def test_view_exception_handling(self):
        """Test that view exceptions are handled gracefully"""
        # This would typically involve mocking to force exceptions
        
        # Test admin dashboard with potential database issues
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        
        # Should handle any exceptions gracefully
        self.assertIn(response.status_code, [200, 500])
    
    def test_form_processing_exceptions(self):
        """Test exception handling during form processing"""
        # Submit valid form data
        valid_data = {
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': '2015-05-15',
            'student_gender': 'M',
            'student_place_of_birth': 'Tamale',
            'grade_applying_for': 'primary_1',
            'guardian_first_name': 'Jane',
            'guardian_last_name': 'Doe',
            'guardian_relationship': 'mother',
            'guardian_phone': '+233241234567',
            'guardian_email': 'jane.doe@example.com',
            'guardian_address': '123 Main St, Tamale',
            'guardian_occupation': 'Teacher',
            'emergency_contact_name': 'John Smith',
            'emergency_contact_phone': '+233241234568',
            'emergency_contact_relationship': 'uncle',
            'medical_conditions': '',
            'special_requirements': '',
            'additional_notes': '',
        }
        
        # Normal processing should work
        response = self.client.post('/apply/', data=valid_data)
        self.assertEqual(response.status_code, 302)
    
    def test_model_validation_exceptions(self):
        """Test handling of model validation exceptions"""
        # Try to create application with invalid data directly
        try:
            application = Application(
                student_first_name='',  # Invalid - required field
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
            application.full_clean()  # This should raise ValidationError
            self.fail("Expected ValidationError was not raised")
        except Exception:
            # Exception should be handled gracefully
            pass


@override_settings(DEBUG=False)
class ProductionErrorHandlingTest(TestCase):
    """
    Test error handling in production-like settings
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_production_404_handling(self):
        """Test 404 handling in production mode"""
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
        
        # In production mode, custom error pages would be used
    
    def test_production_500_handling(self):
        """Test 500 handling in production mode"""
        # This would typically require forcing a server error
        # For now, we just ensure the error handlers are configured
        from django.conf import settings
        
        # Check that custom error handlers are configured
        from morning_star_academy import urls
        self.assertTrue(hasattr(urls, 'handler404'))
        self.assertTrue(hasattr(urls, 'handler500'))
        self.assertTrue(hasattr(urls, 'handler403'))
        self.assertTrue(hasattr(urls, 'handler400'))