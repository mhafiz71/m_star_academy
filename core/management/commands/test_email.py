"""
Management command to test email configuration
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from core.email_service import EmailService


class Command(BaseCommand):
    help = 'Test email configuration and send a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            required=True
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['simple', 'template'],
            default='simple',
            help='Type of test email to send'
        )

    def handle(self, *args, **options):
        recipient_email = options['to']
        email_type = options['type']

        self.stdout.write(
            self.style.SUCCESS(f'Testing email configuration...')
        )

        # Display current email settings
        self.stdout.write(f'Email Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'Email Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'Email Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'Email Use TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'Default From Email: {settings.DEFAULT_FROM_EMAIL}')

        try:
            if email_type == 'simple':
                # Send simple test email
                send_mail(
                    subject='Morning Star Academy - Email Test',
                    message='This is a test email from Morning Star Academy platform.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Simple test email sent successfully to {recipient_email}')
                )

            elif email_type == 'template':
                # Create a mock application for template testing
                from applications.models import Application
                from datetime import date

                # Create a temporary application for testing
                test_app = Application(
                    student_first_name='Test',
                    student_last_name='Student',
                    student_date_of_birth=date(2015, 1, 1),
                    student_gender='M',
                    student_place_of_birth='Tamale',
                    grade_applying_for='primary_1',
                    guardian_first_name='Test',
                    guardian_last_name='Guardian',
                    guardian_relationship='parent',
                    guardian_phone='+233241234567',
                    guardian_email=recipient_email,
                    guardian_address='Test Address',
                    guardian_occupation='Test Occupation',
                    emergency_contact_name='Emergency Contact',
                    emergency_contact_phone='+233241234568',
                    emergency_contact_relationship='uncle',
                )
                test_app.reference_number = 'TEST2025001'

                # Send template-based test email
                success = EmailService.send_application_confirmation(test_app)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Template test email sent successfully to {recipient_email}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Failed to send template test email')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Email test failed: {str(e)}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('Email test completed!')
        )