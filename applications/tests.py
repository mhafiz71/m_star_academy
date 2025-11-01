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
