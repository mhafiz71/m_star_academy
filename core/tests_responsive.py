from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from applications.models import Application
from datetime import date


class ResponsiveDesignTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create staff user for admin tests
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@morningstaracademy.edu.gh',
            password='testpass123',
            is_staff=True
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
    
    def test_viewport_meta_tag(self):
        """Test that viewport meta tag is present for mobile optimization"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, 'width=device-width, initial-scale=1.0')
    
    def test_mobile_navigation_elements(self):
        """Test that mobile navigation elements are present"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile menu button
        self.assertContains(response, 'mobile-menu-button')
        self.assertContains(response, 'hamburger-icon')
        self.assertContains(response, 'close-icon')
        
        # Check for mobile menu
        self.assertContains(response, 'mobile-menu')
        self.assertContains(response, 'md:hidden')
    
    def test_responsive_grid_classes(self):
        """Test that responsive grid classes are used"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive grid classes
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-2')
        self.assertContains(response, 'lg:grid-cols-3')
    
    def test_application_form_mobile_optimization(self):
        """Test that application form has mobile optimizations"""
        response = self.client.get('/apply/')
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile-optimized input types
        self.assertContains(response, 'type="tel"')
        self.assertContains(response, 'type="email"')
        self.assertContains(response, 'type="date"')
        
        # Check for responsive form layout
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-2')
    
    def test_admin_dashboard_responsive(self):
        """Test that admin dashboard is responsive"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/')
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive statistics cards
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-2')
        self.assertContains(response, 'lg:grid-cols-5')
    
    def test_application_list_responsive(self):
        """Test that application list is responsive"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get('/admin-portal/applications/')
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive table
        self.assertContains(response, 'overflow-x-auto')
        self.assertContains(response, 'min-w-full')
        
        # Check for responsive filter form
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'md:grid-cols-4')
    
    def test_application_detail_responsive(self):
        """Test that application detail page is responsive"""
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get(f'/admin-portal/applications/{self.application.pk}/')
        self.assertEqual(response.status_code, 200)
        
        # Check for responsive layout
        self.assertContains(response, 'lg:col-span-2')
        self.assertContains(response, 'grid-cols-1')
        self.assertContains(response, 'lg:grid-cols-3')
    
    def test_touch_friendly_elements(self):
        """Test that elements are touch-friendly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for button classes that ensure minimum touch targets
        self.assertContains(response, 'btn-primary')
        self.assertContains(response, 'btn-secondary')
    
    def test_font_size_mobile_optimization(self):
        """Test that font sizes are optimized for mobile"""
        response = self.client.get('/apply/')
        self.assertEqual(response.status_code, 200)
        
        # Check that form inputs have appropriate font size (16px minimum to prevent zoom on iOS)
        # This is handled in our CSS, so we check for the form-input class
        self.assertContains(response, 'form-input')
    
    def test_loading_component_present(self):
        """Test that loading component is included"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for loading overlay
        self.assertContains(response, 'loading-overlay')
        self.assertContains(response, 'animate-spin')
    
    def test_mobile_menu_javascript(self):
        """Test that mobile menu JavaScript is present"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile menu JavaScript functionality
        self.assertContains(response, 'mobile-menu-button')
        self.assertContains(response, 'toggleMenu')
        self.assertContains(response, 'closeMenu')
    
    def test_performance_optimizations(self):
        """Test that performance optimizations are in place"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for preconnect links
        self.assertContains(response, 'rel="preconnect"')
        
        # Check for theme color meta tag
        self.assertContains(response, 'name="theme-color"')
        
        # Check for apple mobile web app meta tags
        self.assertContains(response, 'apple-mobile-web-app-capable')


class MobileFormTest(TestCase):
    
    def test_form_submission_mobile_optimized(self):
        """Test that form submission works on mobile"""
        form_data = {
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
        
        # Simulate mobile user agent
        response = self.client.post('/apply/', data=form_data, HTTP_USER_AGENT='Mobile')
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Check that application was created
        self.assertEqual(Application.objects.count(), 1)
    
    def test_mobile_input_types(self):
        """Test that mobile-optimized input types are used"""
        response = self.client.get('/apply/')
        self.assertEqual(response.status_code, 200)
        
        # Check for tel input type for phone numbers
        self.assertContains(response, 'type="tel"')
        
        # Check for email input type
        self.assertContains(response, 'type="email"')
        
        # Check for date input type
        self.assertContains(response, 'type="date"')
        
        # Check for inputmode attributes
        self.assertContains(response, 'inputmode="tel"')
        self.assertContains(response, 'inputmode="email"')