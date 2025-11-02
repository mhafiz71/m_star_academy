from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import date, timedelta
import re
from .models import Application


class ApplicationForm(forms.ModelForm):
    """
    Form for student application submission with comprehensive validation
    """
    
    class Meta:
        model = Application
        fields = [
            # Student Information
            'student_first_name',
            'student_last_name', 
            'student_date_of_birth',
            'student_gender',
            'student_place_of_birth',
            
            # Academic Information
            'previous_school',
            'grade_applying_for',
            
            # Guardian Information
            'guardian_first_name',
            'guardian_last_name',
            'guardian_relationship',
            'guardian_phone',
            'guardian_email',
            'guardian_address',
            'guardian_occupation',
            
            # Emergency Contact
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            
            # Additional Information
            'medical_conditions',
            'special_requirements',
            'additional_notes',
        ]
        
        widgets = {
            # Student Information
            'student_first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name'
            }),
            'student_last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name'
            }),
            'student_date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'student_gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'student_place_of_birth': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Place of Birth'
            }),
            
            # Academic Information
            'previous_school': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Previous School (if any)'
            }),
            'grade_applying_for': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            # Guardian Information
            'guardian_first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First Name'
            }),
            'guardian_last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last Name'
            }),
            'guardian_relationship': forms.Select(attrs={
                'class': 'form-select'
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number'
            }),
            'guardian_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email Address'
            }),
            'guardian_address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Full Address',
                'rows': 3
            }),
            'guardian_occupation': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Occupation'
            }),
            
            # Emergency Contact
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Full Name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number'
            }),
            'emergency_contact_relationship': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            # Additional Information
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Any medical conditions we should be aware of',
                'rows': 3
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Any special requirements or accommodations needed',
                'rows': 3
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Any additional information you would like to provide',
                'rows': 3
            }),
        }
    
    def clean_student_first_name(self):
        value = self.cleaned_data['student_first_name']
        if not re.match(r'^[A-Za-z\s\-\']+$', value):
            raise ValidationError("Name should only contain letters, spaces, hyphens, and apostrophes.")
        return value
    
    def clean_student_last_name(self):
        value = self.cleaned_data['student_last_name']
        if not re.match(r'^[A-Za-z\s\-\']+$', value):
            raise ValidationError("Name should only contain letters, spaces, hyphens, and apostrophes.")
        return value
    
    def clean_student_date_of_birth(self):
        dob = self.cleaned_data['student_date_of_birth']
        today = date.today()
        
        # Check if date is in the future
        if dob > today:
            raise ValidationError("Date of birth cannot be in the future.")
        
        # Check if student is too old (e.g., over 20 years)
        max_age = today - timedelta(days=365*20)
        if dob < max_age:
            raise ValidationError("Student appears to be over 20 years old. Please verify the date.")
        
        # Check if student is too young (e.g., under 2 years)
        min_age = today - timedelta(days=365*2)
        if dob > min_age:
            raise ValidationError("Student appears to be under 2 years old. Please verify the date.")
            
        return dob
    
    def clean_guardian_first_name(self):
        value = self.cleaned_data['guardian_first_name']
        if not re.match(r'^[A-Za-z\s\-\']+$', value):
            raise ValidationError("Name should only contain letters, spaces, hyphens, and apostrophes.")
        return value
    
    def clean_guardian_last_name(self):
        value = self.cleaned_data['guardian_last_name']
        if not re.match(r'^[A-Za-z\s\-\']+$', value):
            raise ValidationError("Name should only contain letters, spaces, hyphens, and apostrophes.")
        return value
    
    def clean_guardian_phone(self):
        phone = self.cleaned_data['guardian_phone']
        # Remove any spaces, dashes, or parentheses
        phone_digits = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if the phone number has a reasonable length
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise ValidationError("Please enter a valid phone number with at least 10 digits.")
            
        # Check if the phone number contains only digits and possibly a leading +
        if not re.match(r'^\+?\d+$', phone_digits):
            raise ValidationError("Phone number should only contain digits and possibly a leading + symbol.")
            
        return phone
    
    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data['emergency_contact_phone']
        # Remove any spaces, dashes, or parentheses
        phone_digits = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if the phone number has a reasonable length
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise ValidationError("Please enter a valid phone number with at least 10 digits.")
            
        # Check if the phone number contains only digits and possibly a leading +
        if not re.match(r'^\+?\d+$', phone_digits):
            raise ValidationError("Phone number should only contain digits and possibly a leading + symbol.")
            
        return phone
    
    def clean_emergency_contact_name(self):
        value = self.cleaned_data['emergency_contact_name']
        if not re.match(r'^[A-Za-z\s\-\']+$', value):
            raise ValidationError("Name should only contain letters, spaces, hyphens, and apostrophes.")
        return value
    
    def clean_medical_conditions(self):
        value = self.cleaned_data['medical_conditions']
        # Strip HTML tags for security
        return strip_tags(value)
    
    def clean_special_requirements(self):
        value = self.cleaned_data['special_requirements']
        # Strip HTML tags for security
        return strip_tags(value)
    
    def clean_additional_notes(self):
        value = self.cleaned_data['additional_notes']
        # Strip HTML tags for security
        return strip_tags(value)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if emergency contact is different from guardian
        guardian_phone = cleaned_data.get('guardian_phone')
        emergency_phone = cleaned_data.get('emergency_contact_phone')
        
        if guardian_phone and emergency_phone and guardian_phone == emergency_phone:
            self.add_error('emergency_contact_phone', 
                          "Emergency contact should be different from guardian.")
        
        return cleaned_data


class ApplicationDownloadForm(forms.Form):
    """Form for downloading application forms by reference number"""
    reference_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Enter reference number'
        })
    )
    
    def clean_reference_number(self):
        reference_number = self.cleaned_data['reference_number']
        
        # Check if application with this reference number exists
        try:
            Application.objects.get(reference_number=reference_number)
        except Application.DoesNotExist:
            raise ValidationError("No application found with this reference number.")
            
        return reference_number