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
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Enter student\'s first name',
                'autocomplete': 'given-name',
                'maxlength': '100'
            }),
            'student_last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Enter student\'s last name',
                'autocomplete': 'family-name',
                'maxlength': '100'
            }),
            'student_date_of_birth': forms.DateInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'type': 'date',
                'autocomplete': 'bday'
            }),
            'student_gender': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 cursor-pointer'
            }),
            'student_place_of_birth': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'e.g., Tamale, Northern Region',
                'maxlength': '200'
            }),
            
            # Academic Information
            'previous_school': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Enter previous school name (if applicable)',
                'maxlength': '200'
            }),
            'grade_applying_for': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 cursor-pointer'
            }),
            
            # Guardian Information
            'guardian_first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Enter guardian\'s first name',
                'autocomplete': 'given-name',
                'maxlength': '100'
            }),
            'guardian_last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Enter guardian\'s last name',
                'autocomplete': 'family-name',
                'maxlength': '100'
            }),
            'guardian_relationship': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 cursor-pointer'
            }),
            'guardian_phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': '+233 24 123 4567',
                'type': 'tel',
                'inputmode': 'tel',
                'autocomplete': 'tel',
                'pattern': r'[\+]?[0-9\s\-\(\)]+',
                'maxlength': '20'
            }),
            'guardian_email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'guardian@example.com',
                'inputmode': 'email',
                'autocomplete': 'email',
                'maxlength': '254'
            }),
            'guardian_address': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 resize-y min-h-[80px]',
                'rows': 3,
                'placeholder': 'Enter complete residential address',
                'autocomplete': 'street-address',
                'maxlength': '500'
            }),
            'guardian_occupation': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'e.g., Teacher, Farmer, Business Owner',
                'autocomplete': 'organization-title',
                'maxlength': '100'
            }),
            
            # Emergency Contact
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'Full name of emergency contact',
                'maxlength': '100'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': '+233 24 123 4567',
                'type': 'tel',
                'inputmode': 'tel',
                'pattern': r'[\+]?[0-9\s\-\(\)]+',
                'maxlength': '20'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900',
                'placeholder': 'e.g., Uncle, Aunt, Family Friend',
                'maxlength': '50'
            }),
            
            # Additional Information
            'medical_conditions': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 resize-y min-h-[80px]',
                'rows': 3,
                'placeholder': 'List any medical conditions, allergies, or medications (leave blank if none)',
                'maxlength': '1000'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 resize-y min-h-[80px]',
                'rows': 3,
                'placeholder': 'Any special educational needs or accommodations required (leave blank if none)',
                'maxlength': '1000'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 bg-white text-gray-900 resize-y min-h-[80px]',
                'rows': 3,
                'placeholder': 'Any other information you would like us to know (optional)',
                'maxlength': '1000'
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