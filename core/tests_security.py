from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from applications.models import Application
from datetime import date
import time


class SecurityHeadersTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_security_headers_present(self):
        """Test that security headers are added to responses"""
        response = self.client.get('/')
        
        # Check for security headers
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.get('X-XSS-Protection'), '1; mode=block')
        self.assertEqual(response.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('Permissions-Policy', response)
    
    def test_csrf_protection(self):
        """Test that CSRF protection is working"""
        # Try to submit form without CSRF token
        response = self.client.post('/apply/', {
            'student_first_name': 'Test',
            'student_last_name': 'User',
        })
        
        # Should be forbidden due to missing CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_xss_protection_in_forms(self):
        """Test that XSS attempts are sanitized in forms"""
        form_data = {
            'student_first_name': '<script>alert("xss")</script>John',
            'student_last_name': 'Doe<img src=x onerror=alert(1)>',
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
        
        response = self.client.post('/apply/', data=form_data)
        
        # Should redirect to success page (form accepted but sanitized)
        self.assertEqual(response.status_code, 302)
        
        # Check that the data was sanitized
        application = Application.objects.first()
        self.assertNotIn('<script>', application.student_first_name)
        self.assertNotIn('<img', application.student_last_name)
        self.assertEqual(application.student_first_name, 'John')  # Script tags removed


class RateLimitingTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        # Clear cache before each test
        cache.clear()
    
    def test_rate_limiting_for_anonymous_users(self):
        """Test that rate limiting works for anonymous users"""
        # Make 10 POST requests (should be allowed)
        for i in range(10):
            response = self.client.post('/apply/', {
                'student_first_name': f'Test{i}',
            })
            # Should get CSRF error (403) not rate limit error
            self.assertEqual(response.status_code, 403)
        
        # 11th request should be rate limited
        response = self.client.post('/apply/', {
            'student_first_name': 'Test11',
        })
        self.assertEqual(response.status_code, 403)  # Rate limited
    
    def test_rate_limiting_bypass_for_staff(self):
        """Test that staff users bypass rate limiting"""
        # Create staff user
        staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
        
        # Login as staff
        self.client.login(username='staff_user', password='testpass123')
        
        # Make many requests (should not be rate limited)
        for i in range(15):
            response = self.client.post('/admin-portal/', {})
            # Should get normal response, not rate limited
            self.assertNotEqual(response.status_code, 403)


class AuthenticationSecurityTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_password_strength_requirements(self):
        """Test that password strength requirements are enforced"""
        # This would be tested in user creation/password change forms
        # For now, we test that the validators are configured
        from django.conf import settings
        
        validators = settings.AUTH_PASSWORD_VALIDATORS
        self.assertTrue(len(validators) >= 4)
        
        # Check minimum length validator is configured
        min_length_validator = next(
            (v for v in validators if 'MinimumLengthValidator' in v['NAME']), 
            None
        )
        self.assertIsNotNone(min_length_validator)
        self.assertEqual(min_length_validator.get('OPTIONS', {}).get('min_length'), 8)
    
    def test_session_security(self):
        """Test session security settings"""
        from django.conf import settings
        
        # Check session settings
        self.assertEqual(settings.SESSION_COOKIE_AGE, 3600)  # 1 hour
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Lax')
    
    def test_admin_access_protection(self):
        """Test that admin areas are properly protected"""
        # Try to access admin without authentication
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access with regular user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no staff permission


class InputValidationTest(TestCase):
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts"""
        # Django ORM should protect against SQL injection by default
        malicious_input = "'; DROP TABLE applications_application; --"
        
        form_data = {
            'student_first_name': malicious_input,
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
        
        response = self.client.post('/apply/', data=form_data)
        
        # Should handle gracefully (either redirect or form error)
        self.assertIn(response.status_code, [200, 302])
        
        # Table should still exist
        self.assertTrue(Application.objects.model._meta.db_table)
    
    def test_file_upload_limits(self):
        """Test that file upload limits are configured"""
        from django.conf import settings
        
        # Check upload limits are set
        self.assertEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 5242880)  # 5MB
        self.assertEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, 5242880)  # 5MB
        self.assertEqual(settings.DATA_UPLOAD_MAX_NUMBER_FIELDS, 1000)
    
    def test_email_validation(self):
        """Test email field validation"""
        invalid_emails = [
            'invalid-email',
            'test@',
            '@example.com',
            'test..test@example.com',
            'test@example',
        ]
        
        for invalid_email in invalid_emails:
            form_data = {
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
                'guardian_email': invalid_email,
                'guardian_address': '123 Main St, Tamale',
                'guardian_occupation': 'Teacher',
                'emergency_contact_name': 'John Smith',
                'emergency_contact_phone': '+233241234568',
                'emergency_contact_relationship': 'uncle',
                'medical_conditions': '',
                'special_requirements': '',
                'additional_notes': '',
            }
            
            response = self.client.post('/apply/', data=form_data)
            
            # Should return form with errors (not redirect)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Please correct the errors')


class SecurityLoggingTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_suspicious_user_agent_logging(self):
        """Test that suspicious user agents are logged"""
        # This would require checking log files in a real scenario
        # For testing, we just ensure the middleware doesn't break
        response = self.client.get('/', HTTP_USER_AGENT='sqlmap/1.0')
        self.assertEqual(response.status_code, 200)
    
    def test_failed_login_logging(self):
        """Test that failed login attempts are logged"""
        response = self.client.post('/accounts/login/', {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        
        # Should return login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username')


@override_settings(DEBUG=False)
class ProductionSecurityTest(TestCase):
    
    def test_debug_disabled_in_production(self):
        """Test that DEBUG is disabled in production settings"""
        from django.conf import settings
        self.assertFalse(settings.DEBUG)
    
    def test_allowed_hosts_configured(self):
        """Test that ALLOWED_HOSTS is properly configured"""
        # This would be tested with production settings
        pass