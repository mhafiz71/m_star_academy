from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 
        'student_full_name', 
        'grade_applying_for', 
        'status', 
        'created_at'
    ]
    list_filter = ['status', 'grade_applying_for', 'created_at']
    search_fields = [
        'reference_number', 
        'student_first_name', 
        'student_last_name',
        'guardian_first_name',
        'guardian_last_name',
        'guardian_email'
    ]
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Application Info', {
            'fields': ('reference_number', 'status', 'created_at', 'updated_at')
        }),
        ('Student Information', {
            'fields': (
                'student_first_name', 
                'student_last_name', 
                'student_date_of_birth',
                'student_gender',
                'student_place_of_birth'
            )
        }),
        ('Academic Information', {
            'fields': ('previous_school', 'grade_applying_for')
        }),
        ('Guardian Information', {
            'fields': (
                'guardian_first_name',
                'guardian_last_name', 
                'guardian_relationship',
                'guardian_phone',
                'guardian_email',
                'guardian_address',
                'guardian_occupation'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Additional Information', {
            'fields': ('medical_conditions', 'special_requirements', 'additional_notes'),
            'classes': ('collapse',)
        }),
    )
    
    def student_full_name(self, obj):
        return obj.student_full_name
    student_full_name.short_description = 'Student Name'
