from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from applications.models import Application
from datetime import date


class PublicViewsTest(TestCase):
    """
    Test cases for public views (core app)
    """
    
    def setUp(self):
        self.client = Client()
    
    def test_home_view(self):
        """Test home page view"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Morning Star Academy')
        self.assertContains(response, 'Quality Education')
        self.assertContains(response, 'Apply Now')
        
        # Check for key sections
        self.assertContains(response, 'Why Choose Morning Star Academy')
        self.assertContains(response, 'Our Impact')
        self.assertContains(response, 'Ready to Join Our Community')
    
    def test_about_view(self):
        """Test about page view"""
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About Morning Star Academy')
        self.assertContains(response, 'Founded in 2016')
        self.assertContains(response, 'Tamale, Gbanyamli')
        self.assertContains(response, 'NASIA Approved')
        
        # Check for key sections
        self.assertContains(response, 'Our Story')
        self.assertContains(response, 'Our Location')
        self.assertContains(response, 'Our Mission')
        self.assertContains(response, 'Our Team')
    
    def test_navigation_links(self):
        """Test that navigation links are present and working"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for navigation links
        self.assertContains(response, 'href="/"')  # Home link
        self.assertContains(response, 'href="/apply/"')  # Apply link
        self.assertContains(response, 'href="/about/"')  # About link
    
    def test_responsive_elements(self):
        """Test that responsive elements are present"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive classes
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-2')
        self.assertContains(response, 'lg:grid-cols-3')
        
        # Check for mobile menu
        self.assertContains(response, 'mobile-menu-button')
        self.assertContains(response, 'md:hidden')
    
    def test_footer_content(self):
        """Test footer content"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check footer content
        self.assertContains(response, 'Morning Star Academy')
        self.assertContains(response, 'Tamale, Gbanyamli')
        self.assertContains(response, 'Quick Links')


class ApplicationViewsTest(TestCase):
    """
    Test cases for application views
    """
    
    def setUp(self):
        self.client = Client()
        self.valid_form_data = {
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
    
    def test_application_form_get(self):
        """Test GET request to application form"""
        response = self.client.get('/apply/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apply to Morning Star Academy')
        
        # Check for form sections
        self.assertContains(response, 'Student Information')
        self.assertContains(response, 'Academic Information')
        self.assertContains(response, 'Guardian Information')
        self.assertContains(response, 'Emergency Contact')
        self.assertContains(response, 'Additional Information')
        
        # Check for form fields
        self.assertContains(response, 'name="student_first_name"')
        self.assertContains(response, 'name="guardian_email"')
        self.assertContains(response, 'name="grade_applying_for"')
    
    def test_application_form_post_valid(self):
        """Test POST request with valid data"""
        response = self.client.post('/apply/', data=self.valid_form_data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Check that application was created
        self.assertEqual(Application.objects.count(), 1)
        application = Application.objects.first()
        self.assertEqual(application.student_first_name, 'John')
        self.assertEqual(application.guardian_email, 'jane.doe@example.com')
        
        # Check redirect URL
        self.assertIn('/apply/success/', response.url)
        self.assertIn(application.reference_number, response.url)
    
    def test_application_form_post_invalid(self):
        """Test POST request with invalid data"""
        invalid_data = self.valid_form_data.copy()
        invalid_data['student_first_name'] = ''  # Required field
        invalid_data['guardian_email'] = 'invalid-email'  # Invalid email
        
        response = self.client.post('/apply/', data=invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        
        # No application should be created
        self.assertEqual(Application.objects.count(), 0)
    
    def test_application_success_view_valid(self):
        """Test success view with valid reference number"""
        # Create application first
        application = Application.objects.create(
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
        
        response = self.client.get(f'/apply/success/{application.reference_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Application Submitted Successfully')
        self.assertContains(response, application.reference_number)
        self.assertContains(response, 'John Doe')
        
        # Check for next steps information
        self.assertContains(response, 'What Happens Next')
        self.assertContains(response, 'Return to Home')
    
    def test_application_success_view_invalid(self):
        """Test success view with invalid reference number"""
        response = self.client.get('/apply/success/INVALID123/')
        self.assertEqual(response.status_code, 404)
    
    def test_form_field_validation(self):
        """Test individual form field validation"""
        # Test date validation
        invalid_data = self.valid_form_data.copy()
        invalid_data['student_date_of_birth'] = '2030-01-01'  # Future date
        
        response = self.client.post('/apply/', data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Date of birth cannot be in the future')
        
        # Test phone validation
        invalid_data = self.valid_form_data.copy()
        invalid_data['guardian_phone'] = 'invalid-phone'
        
        response = self.client.post('/apply/', data=invalid_data)
        self.assertEqual(response.status_code, 200)
        # Should contain phone validation error
    
    def test_form_security_features(self):
        """Test form security features"""
        # Test CSRF protection
        response = self.client.post('/apply/', data=self.valid_form_data, 
                                  HTTP_X_CSRFTOKEN='invalid')
        self.assertEqual(response.status_code, 403)  # CSRF failure
        
        # Test XSS protection
        xss_data = self.valid_form_data.copy()
        xss_data['student_first_name'] = '<script>alert("xss")</script>John'
        
        response = self.client.post('/apply/', data=xss_data)
        if response.status_code == 302:  # If form was accepted
            application = Application.objects.first()
            # Script tags should be stripped
            self.assertNotIn('<script>', application.student_first_name)


class AdminViewsTest(TestCase):
    """
    Test cases for admin views
    """
    
    def setUp(self):
        self.client = Client()
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
        )
        
        # Create regular user
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
    
    def test_dashboard_view_staff_access(self):
        """Test dashboard view with staff access"""
        self.client.login(username='staff_user', password='testpass123')
        
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
        self.assertContains(response, 'Welcome back')
        
        # Check for statistics
        self.assertContains(response, 'Total Applications')
        self.assertContains(response, 'Pending Review')
        self.assertContains(response, '1')  # Should show 1 application
    
    def test_dashboard_view_no_access(self):
        """Test dashboard view without proper access"""
        # Test unauthenticated access
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='regular_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
    
    def test_application_list_view(self):
        """Test application list view"""
        self.client.login(username='staff_user', password='testpass123')
        
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Application Management')
        self.assertContains(response, self.application.reference_number)
        self.assertContains(response, 'John Doe')
        
        # Check for filter options
        self.assertContains(response, 'All Statuses')
        self.assertContains(response, 'All Grades')
        self.assertContains(response, 'name="search"')
    
    def test_application_detail_view(self):
        """Test application detail view"""
        self.client.login(username='staff_user', password='testpass123')
        
        response = self.client.get(f'/admin-portal/applications/{self.application.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Application Details')
        self.assertContains(response, self.application.reference_number)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'jane.doe@example.com')
        
        # Check for status update form
        self.assertContains(response, 'Update Status')
        self.assertContains(response, 'name="status"')
    
    def test_application_status_update(self):
        """Test application status update"""
        self.client.login(username='staff_user', password='testpass123')
        
        response = self.client.post(f'/admin-portal/applications/{self.application.pk}/', {
            'status': 'approved'
        })
        
        # Should redirect back to detail page
        self.assertEqual(response.status_code, 302)
        
        # Verify status was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'approved')
    
    def test_application_search_functionality(self):
        """Test application search functionality"""
        self.client.login(username='staff_user', password='testpass123')
        
        # Search by student name
        response = self.client.get('/admin-portal/applications/?search=John')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # Search by reference number
        response = self.client.get(f'/admin-portal/applications/?search={self.application.reference_number}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.application.reference_number)
        
        # Search with no results
        response = self.client.get('/admin-portal/applications/?search=NonExistent')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No applications found')
    
    def test_application_filtering(self):
        """Test application filtering"""
        self.client.login(username='staff_user', password='testpass123')
        
        # Filter by status
        response = self.client.get('/admin-portal/applications/?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # Filter by grade
        response = self.client.get('/admin-portal/applications/?grade=primary_1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # Filter with no results
        response = self.client.get('/admin-portal/applications/?status=approved')
        self.assertEqual(response.status_code, 200)
        # Should not contain the pending application
    
    def test_admin_navigation(self):
        """Test admin navigation elements"""
        self.client.login(username='staff_user', password='testpass123')
        
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        
        # Check for navigation elements
        self.assertContains(response, 'View All Applications')
        self.assertContains(response, 'Review Pending Applications')
        self.assertContains(response, 'View Public Website')


class AuthenticationViewsTest(TestCase):
    """
    Test cases for authentication views
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')
        self.assertContains(response, 'Morning Star Academy Admin Portal')
        
        # Check for form fields
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
    
    def test_login_view_post_valid(self):
        """Test login with valid credentials"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # User should be logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
    
    def test_login_view_post_invalid(self):
        """Test login with invalid credentials"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Should return login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test logout
        response = self.client.get('/admin-portal/logout/')
        self.assertEqual(response.status_code, 302)
        
        # Should redirect to home page
        self.assertRedirects(response, '/')
    
    def test_login_redirect(self):
        """Test login redirect functionality"""
        # Try to access protected page
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 302)
        
        # Should redirect to login
        self.assertIn('/accounts/login/', response.url)