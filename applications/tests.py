from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Application

class ApplicationModelTest(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.valid_application_data = {
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': date(2015, 5, 15),
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
        }
    
    def test_application_creation(self):
        """Test that an application can be created with valid data"""
        application = Application.objects.create(**self.valid_application_data)
        
        self.assertEqual(application.student_first_name, 'John')
        self.assertEqual(application.student_last_name, 'Doe')
        self.assertEqual(application.status, 'pending')
        self.assertIsNotNone(application.reference_number)
        self.assertIsNotNone(application.created_at)
    
    def test_reference_number_generation(self):
        """Test that reference numbers are generated correctly"""
        application1 = Application.objects.create(**self.valid_application_data)
        
        # Modify data for second application
        data2 = self.valid_application_data.copy()
        data2['student_first_name'] = 'Alice'
        data2['guardian_email'] = 'alice.parent@example.com'
        application2 = Application.objects.create(**data2)
        
        # Check reference number format
        year = timezone.now().year
        self.assertTrue(application1.reference_number.startswith(f'MSA{year}'))
        self.assertTrue(application2.reference_number.startswith(f'MSA{year}'))
        
        # Check uniqueness
        self.assertNotEqual(application1.reference_number, application2.reference_number)
    
    def test_student_full_name_property(self):
        """Test the student_full_name property"""
        application = Application.objects.create(**self.valid_application_data)
        self.assertEqual(application.student_full_name, 'John Doe')
    
    def test_guardian_full_name_property(self):
        """Test the guardian_full_name property"""
        application = Application.objects.create(**self.valid_application_data)
        self.assertEqual(application.guardian_full_name, 'Jane Doe')
    
    def test_age_calculation(self):
        """Test age calculation at application"""
        application = Application.objects.create(**self.valid_application_data)
        expected_age = timezone.now().year - 2015
        # Account for birthday not yet passed this year
        if timezone.now().date() < date(timezone.now().year, 5, 15):
            expected_age -= 1
        self.assertEqual(application.age_at_application, expected_age)
    
    def test_status_display_property(self):
        """Test status display property"""
        application = Application.objects.create(**self.valid_application_data)
        self.assertEqual(application.status_display, 'Pending Review')
        
        application.status = 'approved'
        application.save()
        self.assertEqual(application.status_display, 'Approved')
    
    def test_string_representation(self):
        """Test the __str__ method"""
        application = Application.objects.create(**self.valid_application_data)
        expected_str = f"{application.reference_number} - John Doe"
        self.assertEqual(str(application), expected_str)
    
    def test_model_ordering(self):
        """Test that applications are ordered by creation date (newest first)"""
        app1 = Application.objects.create(**self.valid_application_data)
        
        # Create second application
        data2 = self.valid_application_data.copy()
        data2['student_first_name'] = 'Alice'
        data2['guardian_email'] = 'alice.parent@example.com'
        app2 = Application.objects.create(**data2)
        
        applications = Application.objects.all()
        self.assertEqual(applications[0], app2)  # Newest first
        self.assertEqual(applications[1], app1)
    
    def test_required_fields(self):
        """Test that required fields are enforced through model validation"""
        # Test with missing required field
        incomplete_data = self.valid_application_data.copy()
        incomplete_data['student_first_name'] = ''  # Empty string instead of missing
        
        application = Application(**incomplete_data)
        with self.assertRaises(ValidationError):
            application.full_clean()  # This triggers model validation


class ApplicationFormTest(TestCase):
    
    def setUp(self):
        """Set up test data for form testing"""
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
    
    def test_valid_form(self):
        """Test that form is valid with correct data"""
        from .forms import ApplicationForm
        form = ApplicationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_required_fields_validation(self):
        """Test that required fields are validated"""
        from .forms import ApplicationForm
        
        # Test missing student first name
        data = self.valid_form_data.copy()
        data['student_first_name'] = ''
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_first_name', form.errors)
    
    def test_date_of_birth_validation(self):
        """Test date of birth validation"""
        from .forms import ApplicationForm
        
        # Test future date
        data = self.valid_form_data.copy()
        data['student_date_of_birth'] = '2030-01-01'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_date_of_birth', form.errors)
        
        # Test too young (under 3)
        data['student_date_of_birth'] = '2023-01-01'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_date_of_birth', form.errors)
        
        # Test too old (over 18)
        data['student_date_of_birth'] = '2000-01-01'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_date_of_birth', form.errors)
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        from .forms import ApplicationForm
        
        # Test invalid phone number
        data = self.valid_form_data.copy()
        data['guardian_phone'] = 'invalid-phone'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('guardian_phone', form.errors)
        
        # Test short phone number
        data['guardian_phone'] = '123'
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('guardian_phone', form.errors)
    
    def test_emergency_contact_different_from_guardian(self):
        """Test that emergency contact phone must be different from guardian phone"""
        from .forms import ApplicationForm
        
        data = self.valid_form_data.copy()
        data['emergency_contact_phone'] = data['guardian_phone']  # Same as guardian
        form = ApplicationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class ApplicationViewTest(TestCase):
    
    def setUp(self):
        """Set up test data for view testing"""
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
        self.assertContains(response, 'Student Information')
    
    def test_application_form_post_valid(self):
        """Test POST request with valid data"""
        response = self.client.post('/apply/', data=self.valid_form_data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Check that application was created
        self.assertEqual(Application.objects.count(), 1)
        application = Application.objects.first()
        self.assertEqual(application.student_first_name, 'John')
        self.assertEqual(application.student_last_name, 'Doe')
        
        # Check redirect URL contains reference number
        self.assertIn(application.reference_number, response.url)
    
    def test_application_form_post_invalid(self):
        """Test POST request with invalid data"""
        invalid_data = self.valid_form_data.copy()
        invalid_data['student_first_name'] = ''  # Missing required field
        
        response = self.client.post('/apply/', data=invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        
        # No application should be created
        self.assertEqual(Application.objects.count(), 0)
    
    def test_success_page_with_valid_reference(self):
        """Test success page with valid reference number"""
        # Create an application first
        application = Application.objects.create(**{
            'student_first_name': 'John',
            'student_last_name': 'Doe',
            'student_date_of_birth': date(2015, 5, 15),
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
        })
        
        response = self.client.get(f'/apply/success/{application.reference_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Application Submitted Successfully')
        self.assertContains(response, application.reference_number)
        self.assertContains(response, 'John Doe')
    
    def test_success_page_with_invalid_reference(self):
        """Test success page with invalid reference number"""
        response = self.client.get('/apply/success/INVALID123/')
        self.assertEqual(response.status_code, 404)
