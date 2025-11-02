from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText


class Command(BaseCommand):
    help = 'Check email configuration and diagnose issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-smtp',
            action='store_true',
            help='Test SMTP connection directly',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Checking Email Configuration...')
        )

        # Display current settings
        self.stdout.write(f'📧 Email Backend: {settings.EMAIL_BACKEND}')
        
        if hasattr(settings, 'EMAIL_HOST'):
            self.stdout.write(f'🌐 Email Host: {settings.EMAIL_HOST}')
            self.stdout.write(f'🔌 Email Port: {settings.EMAIL_PORT}')
            self.stdout.write(f'🔒 Use TLS: {settings.EMAIL_USE_TLS}')
            self.stdout.write(f'🔐 Use SSL: {settings.EMAIL_USE_SSL}')
            self.stdout.write(f'👤 Email User: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'📨 Default From: {settings.DEFAULT_FROM_EMAIL}')

        # Test based on backend
        if 'console' in settings.EMAIL_BACKEND.lower():
            self.stdout.write(
                self.style.SUCCESS('✅ Console backend detected - emails will appear in terminal')
            )
            
            # Test console email
            try:
                send_mail(
                    'Test Email - Morning Star Academy',
                    'This is a test email to verify console backend is working.',
                    settings.DEFAULT_FROM_EMAIL,
                    ['test@example.com'],
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Console email test successful!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Console email test failed: {e}')
                )

        elif 'smtp' in settings.EMAIL_BACKEND.lower():
            self.stdout.write(
                self.style.WARNING('⚠️  SMTP backend detected - testing connection...')
            )
            
            if options['test_smtp']:
                self.test_smtp_connection()
            else:
                self.stdout.write(
                    self.style.WARNING('💡 Use --test-smtp to test SMTP connection')
                )

        else:
            self.stdout.write(
                self.style.WARNING(f'❓ Unknown backend: {settings.EMAIL_BACKEND}')
            )

    def test_smtp_connection(self):
        """Test SMTP connection directly"""
        try:
            self.stdout.write('🔌 Testing SMTP connection...')
            
            if settings.EMAIL_USE_SSL:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                if settings.EMAIL_USE_TLS:
                    server.starttls()
            
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                self.stdout.write(
                    self.style.SUCCESS('✅ SMTP authentication successful!')
                )
            
            server.quit()
            self.stdout.write(
                self.style.SUCCESS('✅ SMTP connection test passed!')
            )
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ SMTP Authentication failed: {e}')
            )
            self.stdout.write(
                self.style.WARNING('💡 Check your email credentials and app password')
            )
        except smtplib.SMTPException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ SMTP Error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Connection failed: {e}')
            )