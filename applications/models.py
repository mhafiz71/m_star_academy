from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlist', 'Waitlisted'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    GRADE_CHOICES = [
        ('preschool', 'Preschool'),
        ('nursery_1', 'Nursery 1'),
        ('nursery_2', 'Nursery 2'),
        ('kindergarten_1', 'Kindergarten 1'),
        ('kindergarten_2', 'Kindergarten 2'),
        ('primary_1', 'Primary 1'),
        ('primary_2', 'Primary 2'),
        ('primary_3', 'Primary 3'),
        ('primary_4', 'Primary 4'),
        ('primary_5', 'Primary 5'),
        ('primary_6', 'Primary 6'),
        ('jhs_1', 'JHS 1'),
        ('jhs_2', 'JHS 2'),
        ('jhs_3', 'JHS 3'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('grandparent', 'Grandparent'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('other', 'Other'),
    ]
    
    # Reference and tracking
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Student Information
    student_first_name = models.CharField(max_length=100, verbose_name="Student's First Name")
    student_last_name = models.CharField(max_length=100, verbose_name="Student's Last Name")
    student_date_of_birth = models.DateField(verbose_name="Student's Date of Birth")
    student_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Student's Gender")
    student_place_of_birth = models.CharField(max_length=200, verbose_name="Student's Place of Birth")
    
    # Academic Information
    previous_school = models.CharField(max_length=200, blank=True, verbose_name="Previous School (if any)")
    grade_applying_for = models.CharField(max_length=50, choices=GRADE_CHOICES, verbose_name="Grade Applying For")
    
    # Guardian Information
    guardian_first_name = models.CharField(max_length=100, verbose_name="Guardian's First Name")
    guardian_last_name = models.CharField(max_length=100, verbose_name="Guardian's Last Name")
    guardian_relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, verbose_name="Relationship to Student")
    guardian_phone = models.CharField(max_length=20, verbose_name="Guardian's Phone Number")
    guardian_email = models.EmailField(verbose_name="Guardian's Email Address")
    guardian_address = models.TextField(verbose_name="Guardian's Address")
    guardian_occupation = models.CharField(max_length=100, verbose_name="Guardian's Occupation")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, verbose_name="Emergency Contact Name")
    emergency_contact_phone = models.CharField(max_length=20, verbose_name="Emergency Contact Phone")
    emergency_contact_relationship = models.CharField(max_length=50, verbose_name="Emergency Contact Relationship")
    
    # Additional Information
    medical_conditions = models.TextField(blank=True, verbose_name="Medical Conditions/Allergies (if any)")
    special_requirements = models.TextField(blank=True, verbose_name="Special Educational Requirements (if any)")
    additional_notes = models.TextField(blank=True, verbose_name="Additional Notes")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Application"
        verbose_name_plural = "Applications"
    
    def __str__(self):
        return f"{self.reference_number} - {self.student_first_name} {self.student_last_name}"
    
    def clean(self):
        """Custom model validation"""
        super().clean()
        
        # Validate that student is not too old/young for the grade
        if self.student_date_of_birth and self.grade_applying_for:
            age = self.age_at_application
            if age < 3:
                raise ValidationError("Student must be at least 3 years old for preschool.")
            if age > 18:
                raise ValidationError("Student cannot be older than 18 years for basic education.")
        
        # Validate phone number format (basic validation)
        if self.guardian_phone and not self.guardian_phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValidationError("Guardian phone number must contain only digits, spaces, hyphens, and plus sign.")
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        """Generate unique reference number like MSA2024001"""
        year = timezone.now().year
        # Get the count of applications this year
        year_applications = Application.objects.filter(
            created_at__year=year
        ).count()
        
        # Generate reference number
        sequence = year_applications + 1
        return f"MSA{year}{sequence:03d}"
    
    @property
    def student_full_name(self):
        return f"{self.student_first_name} {self.student_last_name}"
    
    @property
    def guardian_full_name(self):
        return f"{self.guardian_first_name} {self.guardian_last_name}"
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    @property
    def age_at_application(self):
        """Calculate student's age at time of application"""
        today = timezone.now().date()
        return today.year - self.student_date_of_birth.year - (
            (today.month, today.day) < (self.student_date_of_birth.month, self.student_date_of_birth.day)
        )
