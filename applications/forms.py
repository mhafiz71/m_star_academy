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
                'placeholder': 'Enter student\'s first name'
            }),
            'student_last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter student\'s last name'
            }),
            'student_date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'student_gender': forms.Select(attrs={
                'class': 'form-input'
            }),
            'student_place_of_birth': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter place of birth'
            }),
            
            # Academic Information
            'previous_school': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter previous school (if any)'
            }),
            'grade_applying_for': forms.Select(attrs={
                'class': 'form-input'
            }),
            
            # Guardian Information
            'guardian_first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter guardian\'s first name'
            }),
            'guardian_last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter guardian\'s last name'
            }),
            'guardian_relationship': forms.Select(attrs={
                'class': 'form-input'
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+233 XX XXX XXXX',
                'type': 'tel',
                'inputmode': 'tel'
            }),
            'guardian_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'guardian@example.com',
                'inputmode': 'email',
                'autocomplete': 'email'
            }),
            'guardian_address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
            'guardian_occupation': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter occupation'
            }),
            
            # Emergency Contact
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+233 XX XXX XXXX',
                'type': 'tel',
                'inputmode': 'tel'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Relationship to student'
            }),
            
            # Additional Information
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'List any medical conditions or allergies (optional)'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Any special educational requirements (optional)'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Any additional information (optional)'
            }),
        }
    
    def clean_student_date_of_birth(self):
        """Validate student's date of birth"""
        dob = self.cleaned_data.get('student_date_of_birth')
        
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check if date is in the future
            if dob > today:
                raise ValidationError("Date of birth cannot be in the future.")
            
            # Check age limits
            if age < 3:
                raise ValidationError("Student must be at least 3 years old to apply.")
            
            if age > 18:
                raise ValidationError("Student cannot be older than 18 years for basic education.")
        
        return dob
    
    def clean_guardian_phone(self):
        """Validate guardian phone number"""
        phone = self.cleaned_data.get('guardian_phone')
        
        if phone:
            # Remove spaces, hyphens, and plus signs for validation
            cleaned_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
            
            if not cleaned_phone.isdigit():
                raise ValidationError("Phone number must contain only digits, spaces, hyphens, and plus sign.")
            
            if len(cleaned_phone) < 10:
                raise ValidationError("Phone number must be at least 10 digits long.")
        
        return phone
    
    def clean_emergency_contact_phone(self):
        """Validate emergency contact phone number"""
        phone = self.cleaned_data.get('emergency_contact_phone')
        
        if phone:
            # Remove spaces, hyphens, and plus signs for validation
            cleaned_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
            
            if not cleaned_phone.isdigit():
                raise ValidationError("Phone number must contain only digits, spaces, hyphens, and plus sign.")
            
            if len(cleaned_phone) < 10:
                raise ValidationError("Phone number must be at least 10 digits long.")
        
        return phone
    
    def clean(self):
        """Cross-field validation and input sanitization"""
        cleaned_data = super().clean()
        
        # Sanitize text fields to prevent XSS
        text_fields = [
            'student_first_name', 'student_last_name', 'student_place_of_birth',
            'previous_school', 'guardian_first_name', 'guardian_last_name',
            'guardian_occupation', 'emergency_contact_name', 'emergency_contact_relationship',
            'medical_conditions', 'special_requirements', 'additional_notes'
        ]
        
        for field_name in text_fields:
            if field_name in cleaned_data and cleaned_data[field_name]:
                # Strip HTML tags and limit length
                cleaned_value = strip_tags(cleaned_data[field_name])
                # Remove potentially dangerous characters
                cleaned_value = re.sub(r'[<>"\']', '', cleaned_value)
                cleaned_data[field_name] = cleaned_value
        
        # Validate guardian address separately (allow more characters but sanitize)
        if 'guardian_address' in cleaned_data and cleaned_data['guardian_address']:
            address = strip_tags(cleaned_data['guardian_address'])
            address = re.sub(r'[<>"\']', '', address)
            cleaned_data['guardian_address'] = address
        
        guardian_phone = cleaned_data.get('guardian_phone')
        emergency_phone = cleaned_data.get('emergency_contact_phone')
        
        # Ensure emergency contact is different from guardian
        if guardian_phone and emergency_phone:
            if guardian_phone == emergency_phone:
                raise ValidationError("Emergency contact phone must be different from guardian phone.")
        
        return cleaned_data