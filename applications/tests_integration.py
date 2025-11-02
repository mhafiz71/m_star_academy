from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from applications.models import Application
from datetime import date
import re


class ApplicationWorkflowIntegrationTest(TestCase):
    """
    Integration tests for the complete application submission workflow
    """
    
    def setUp(self):
        self.client = Client()
        
        # Create staff user for admin tests
        self.staff_user = User.objects.create_user(
            username='admin_user',
            email='admin@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
        )
        
        self.valid_application_data = {
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': '2015-05-15',
            'student_gender': 'M',
            'student_place_of_birth': 'Tamale',
            'grade_applying_for': 'primary_1',
            'previous_school': 'ABC Nursery',
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
    
    def test_complete_application_submission_workflow(self):
        """Test the complete application submission workflow from start to finish"""
        
        # Step 1: User visits home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Morning Star Academy')
        
        # Step 2: User clicks Apply button
        response = self.client.get('/apply/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apply to Morning Star Academy')
        
        # Step 3: User fills and submits application form
        response = self.client.post('/apply/', data=self.valid_application_data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Step 4: Verify application was created
        self.assertEqual(Application.objects.count(), 1)
        application = Application.objects.first()
        self.assertEqual(application.student_first_name, 'John')
        self.assertEqual(application.status, 'pending')
        self.assertIsNotNone(application.reference_number)
        
        # Step 5: Follow redirect to success page
        success_url = response.url
        response = self.client.get(success_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Application Submitted Successfully')
        self.assertContains(response, application.reference_number)
        
        # Step 6: Admin logs in and reviews application
        self.client.login(username='admin_user', password='testpass123')
        
        # Step 7: Admin accesses dashboard
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
        self.assertContains(response, '1')  # Should show 1 total application
        
        # Step 8: Admin views application list
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.reference_number)
        self.assertContains(response, 'John Doe')
        
        # Step 9: Admin views application detail
        response = self.client.get(f'/admin-portal/applications/{application.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.reference_number)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'jane.doe@example.com')
        
        # Step 10: Admin updates application status
        response = self.client.post(f'/admin-portal/applications/{application.pk}/', {
            'status': 'approved'
        })
        self.assertEqual(response.status_code, 302)
        
        # Step 11: Verify status was updated
        application.refresh_from_db()
        self.assertEqual(application.status, 'approved')
    
    def test_application_form_validation_workflow(self):
        """Test form validation workflow with invalid data"""
        
        # Submit form with missing required fields
        invalid_data = self.valid_application_data.copy()
        invalid_data['student_first_name'] = ''
        invalid_data['guardian_email'] = 'invalid-email'
        
        response = self.client.post('/apply/', data=invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        
        # No application should be created
        self.assertEqual(Application.objects.count(), 0)
    
    def test_admin_authentication_workflow(self):
        """Test admin authentication and authorization workflow"""
        
        # Try to access admin without login
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Follow redirect to login page
        login_url = response.url
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
        
        # Login with valid credentials
        response = self.client.post('/accounts/login/', {
            'username': 'admin_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Now should be able to access admin
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
    
    def test_navigation_workflow(self):
        """Test navigation between different pages"""
        
        # Test public navigation
        pages = [
            ('/', 'Morning Star Academy'),
            ('/about/', 'About Morning Star Academy'),
            ('/apply/', 'Apply to Morning Star Academy'),
        ]
        
        for url, expected_content in pages:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, expected_content)
    
    def test_responsive_navigation_workflow(self):
        """Test mobile navigation workflow"""
        
        # Test that mobile navigation elements are present
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile menu elements
        self.assertContains(response, 'mobile-menu-button')
        self.assertContains(response, 'mobile-menu')
    
    def test_application_search_and_filter_workflow(self):
        """Test application search and filtering workflow"""
        
        # Create multiple applications
        for i in range(5):
            data = self.valid_application_data.copy()
            data['student_first_name'] = f'Student{i}'
            data['guardian_email'] = f'guardian{i}@example.com'
            data['grade_applying_for'] = 'primary_1' if i % 2 == 0 else 'primary_2'
            
            Application.objects.create(
                student_first_name=data['student_first_name'],
                student_last_name='Doe',
                student_date_of_birth=date(2015, 5, 15),
                student_gender='M',
                student_place_of_birth='Tamale',
                grade_applying_for=data['grade_applying_for'],
                guardian_first_name='Jane',
                guardian_last_name='Doe',
                guardian_relationship='mother',
                guardian_phone=f'+23324123456{i}',
                guardian_email=data['guardian_email'],
                guardian_address='123 Main St, Tamale',
                guardian_occupation='Teacher',
                emergency_contact_name='John Smith',
                emergency_contact_phone=f'+23324123457{i}',
                emergency_contact_relationship='uncle',
            )
        
        # Login as admin
        self.client.login(username='admin_user', password='testpass123')
        
        # Test search functionality
        response = self.client.get('/admin-portal/applications/?search=Student1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student1')
        self.assertNotContains(response, 'Student2')
        
        # Test grade filtering
        response = self.client.get('/admin-portal/applications/?grade=primary_1')
        self.assertEqual(response.status_code, 200)
        # Should contain applications with primary_1 grade
        
        # Test status filtering
        response = self.client.get('/admin-portal/applications/?status=pending')
        self.assertEqual(response.status_code, 200)
        # All applications should be pending by default


class ErrorHandlingIntegrationTest(TestCase):
    """
    Integration tests for error handling scenarios
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_404_error_handling(self):
        """Test 404 error handling for non-existent pages"""
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_application_id_handling(self):
        """Test handling of invalid application IDs"""
        # Create staff user
        staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='staff_user', password='testpass123')
        
        # Try to access non-existent application
        response = self.client.get('/admin-portal/applications/999/')
        self.assertEqual(response.status_code, 404)
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied scenarios"""
        # Create regular user (not staff)
        regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123',
            is_staff=False
        )
        self.client.login(username='regular_user', password='testpass123')
        
        # Try to access admin area
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission


class PerformanceIntegrationTest(TestCase):
    """
    Integration tests for performance-related functionality
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets in admin views"""
        # Create staff user
        staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
        
        # Create many applications
        applications = []
        for i in range(50):  # Create 50 applications
            applications.append(Application(
                student_first_name=f'Student{i}',
                student_last_name='Test',
                student_date_of_birth=date(2015, 5, 15),
                student_gender='M',
                student_place_of_birth='Tamale',
                grade_applying_for='primary_1',
                guardian_first_name='Guardian',
                guardian_last_name='Test',
                guardian_relationship='mother',
                guardian_phone=f'+23324123456{i}',
                guardian_email=f'guardian{i}@example.com',
                guardian_address='123 Main St, Tamale',
                guardian_occupation='Teacher',
                emergency_contact_name='Emergency',
                emergency_contact_phone=f'+23324123457{i}',
                emergency_contact_relationship='uncle',
            ))
        
        Application.objects.bulk_create(applications)
        
        # Login and test admin views
        self.client.login(username='staff_user', password='testpass123')
        
        # Test dashboard with many applications
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50')  # Should show 50 total applications
        
        # Test application list with pagination
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 200)
        # Should handle pagination properly
    
    def test_concurrent_application_submissions(self):
        """Test handling of concurrent application submissions"""
        # This is a basic test - in a real scenario, you'd use threading
        
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
        
        # Submit multiple applications
        for i in range(5):
            data = valid_data.copy()
            data['guardian_email'] = f'guardian{i}@example.com'
            response = self.client.post('/apply/', data=data)
            self.assertEqual(response.status_code, 302)
        
        # Verify all applications were created with unique reference numbers
        applications = Application.objects.all()
        self.assertEqual(applications.count(), 5)
        
        reference_numbers = [app.reference_number for app in applications]
        self.assertEqual(len(reference_numbers), len(set(reference_numbers)))  # All unique