from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date
from applications.models import Application


class AuthenticationTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpass123',
            is_staff=False
        )
        
        # Create test application
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
    
    def test_login_page_accessible(self):
        """Test that login page is accessible"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
    
    def test_staff_user_login(self):
        """Test that staff user can login"""
        response = self.client.post('/accounts/login/', {
            'username': 'staff_user',
            'password': 'testpass123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin-portal/')
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post('/accounts/login/', {
            'username': 'invalid_user',
            'password': 'wrongpass'
        })
        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='staff_user', password='testpass123')
        
        # Test logout
        response = self.client.get('/admin-portal/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Verify user is logged out
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login


class AdminAccessControlTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpass123',
            is_staff=False
        )
        
        # Create test application
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
    
    def test_admin_dashboard_requires_staff(self):
        """Test that admin dashboard requires staff access"""
        # Test unauthenticated access
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
        
        # Test staff user access
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_application_list_requires_staff(self):
        """Test that application list requires staff access"""
        # Test unauthenticated access
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
        
        # Test staff user access
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 200)
    
    def test_application_detail_requires_staff(self):
        """Test that application detail requires staff access"""
        url = f'/admin-portal/applications/{self.application.pk}/'
        
        # Test unauthenticated access
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
        
        # Test staff user access
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_navigation_shows_admin_link_for_staff(self):
        """Test that admin link appears in navigation for staff users"""
        # Test without login
        response = self.client.get('/')
        self.assertNotContains(response, 'Admin')
        
        # Test with regular user
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get('/')
        self.assertNotContains(response, 'Admin')
        
        # Test with staff user
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/')
        self.assertContains(response, 'Admin')
    
    def test_application_status_update_by_staff(self):
        """Test that staff can update application status"""
        self.client.login(username='staff_user', password='testpass123')
        
        # Test status update
        response = self.client.post(f'/admin-portal/applications/{self.application.pk}/', {
            'status': 'approved'
        })
        
        # Should redirect back to detail page
        self.assertEqual(response.status_code, 302)
        
        # Verify status was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'approved')
    
    def test_regular_user_cannot_update_status(self):
        """Test that regular users cannot update application status"""
        self.client.login(username='regular_user', password='testpass123')
        
        # Attempt to update status
        response = self.client.post(f'/admin-portal/applications/{self.application.pk}/', {
            'status': 'approved'
        })
        
        # Should be redirected due to no permission
        self.assertEqual(response.status_code, 302)
        
        # Verify status was not updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')  # Should remain unchanged


class DashboardViewTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
        )
        
        # Create test applications with different statuses
        for i in range(5):
            Application.objects.create(
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
                status='pending' if i < 3 else 'approved'
            )
    
    def test_dashboard_statistics(self):
        """Test that dashboard shows correct statistics"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5')  # Total applications
        self.assertContains(response, '3')  # Pending applications
        self.assertContains(response, '2')  # Approved applications