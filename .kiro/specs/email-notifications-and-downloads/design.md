# Design Document - Email Notifications and Application Downloads

## Overview

This document outlines the design for implementing email notifications and PDF download functionality for the Morning Star Academy Online Platform. The system will provide automated email communications throughout the application lifecycle and enable PDF generation for record-keeping purposes.

## Architecture

### System Components

```
┌─────────────────────────────────────┐
│           Web Interface             │
│     (Application Forms & Admin)     │
├─────────────────────────────────────┤
│          Email Service              │
│    (Notifications & Verification)   │
├─────────────────────────────────────┤
│          PDF Generator              │
│      (Application Documents)       │
├─────────────────────────────────────┤
│         Queue System                │
│    (Async Email Processing)        │
├─────────────────────────────────────┤
│        Database Layer               │
│   (Email Logs & Verification)      │
└─────────────────────────────────────┘
```

### Technology Stack

- **Email Backend:** Django Email with Celery for async processing
- **PDF Generation:** ReportLab or WeasyPrint for PDF creation
- **Queue System:** Celery with Redis/RabbitMQ
- **Email Provider:** SMTP (configurable for SendGrid, Mailgun, etc.)
- **Templates:** Django email templates with HTML/text versions

## Components and Interfaces

### 1. Email Service Module

#### EmailService Class
```python
class EmailService:
    def send_application_confirmation(self, application)
    def send_status_update(self, application, old_status, new_status)
    def send_verification_email(self, application)
    def send_reminder_email(self, application)
    def verify_email_token(self, token)
```

#### Email Templates
- `emails/application_confirmation.html`
- `emails/status_update.html`
- `emails/verification.html`
- `emails/reminder.html`
- `emails/acceptance.html`
- `emails/rejection.html`
- `emails/waitlist.html`

### 2. PDF Generation Module

#### PDFGenerator Class
```python
class PDFGenerator:
    def generate_application_pdf(self, application, for_admin=False)
    def generate_bulk_applications_pdf(self, applications)
    def get_pdf_response(self, pdf_content, filename)
```

#### PDF Templates
- Application form layout with school branding
- Admin version with additional metadata
- Bulk export format for multiple applications

### 3. Email Verification System

#### EmailVerification Model
```python
class EmailVerification(models.Model):
    application = models.OneToOneField(Application)
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def generate_token(self)
    def is_expired(self)
    def verify(self)
```

### 4. Email Communication Log

#### EmailLog Model
```python
class EmailLog(models.Model):
    application = models.ForeignKey(Application)
    email_type = models.CharField(max_length=50)
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=100)
    error_message = models.TextField(blank=True)
```

### 5. Notification Preferences

#### NotificationPreferences Model
```python
class NotificationPreferences(models.Model):
    application = models.OneToOneField(Application)
    confirmation_emails = models.BooleanField(default=True)
    status_updates = models.BooleanField(default=True)
    reminder_emails = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    unsubscribe_token = models.CharField(max_length=64, unique=True)
```

## Data Models

### Enhanced Application Model
```python
class Application(models.Model):
    # ... existing fields ...
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # PDF generation tracking
    pdf_generated = models.BooleanField(default=False)
    pdf_generated_at = models.DateTimeField(null=True, blank=True)
    
    # Email communication preferences
    email_notifications_enabled = models.BooleanField(default=True)
```

## Email Templates Design

### Template Structure
```
emails/
├── base.html                 # Base template with school branding
├── application_confirmation.html
├── application_confirmation.txt
├── status_update.html
├── status_update.txt
├── verification.html
├── verification.txt
├── acceptance.html
├── acceptance.txt
├── rejection.html
├── rejection.txt
└── waitlist.html
└── waitlist.txt
```

### Email Content Strategy

#### Confirmation Email
- Subject: "Application Received - Morning Star Academy"
- Content: Reference number, next steps, verification link
- Attachments: PDF copy of application

#### Status Update Emails
- **Approved:** Welcome message, enrollment instructions, required documents
- **Rejected:** Polite message, feedback contact, future application encouragement
- **Waitlisted:** Position explanation, timeline, what to expect

#### Verification Email
- Subject: "Please Verify Your Email - Morning Star Academy"
- Content: Simple verification link, expires in 24 hours
- Clear call-to-action button

## PDF Generation Design

### PDF Layout Components
1. **Header:** School logo, name, contact information
2. **Application Details:** Reference number, submission date, status
3. **Student Information:** Personal details, academic background
4. **Guardian Information:** Contact details, relationship
5. **Additional Information:** Medical conditions, special requirements
6. **Footer:** School address, website, disclaimer

### PDF Generation Process
1. Collect application data
2. Render HTML template with data
3. Convert HTML to PDF using WeasyPrint
4. Add school branding and formatting
5. Return PDF response or save to storage

## Security Considerations

### Email Security
- Use TLS encryption for all email communications
- Implement rate limiting for email sending
- Validate email addresses before sending
- Use secure tokens for email verification
- Log all email activities for audit

### PDF Security
- Generate PDFs on-demand to prevent unauthorized access
- Include watermarks or security features if needed
- Limit PDF access to authorized users only
- Log PDF generation and download activities

### Data Protection
- Comply with GDPR and local data protection laws
- Provide opt-out mechanisms for all communications
- Secure storage of email logs and verification data
- Regular cleanup of expired verification tokens

## Performance Considerations

### Async Processing
- Use Celery for background email processing
- Queue PDF generation for large documents
- Implement retry mechanisms for failed operations
- Monitor queue performance and scaling

### Caching Strategy
- Cache rendered email templates
- Cache PDF templates and assets
- Use Redis for session and cache storage
- Implement cache invalidation strategies

### Scalability
- Design for horizontal scaling of email workers
- Use cloud email services for high volume
- Implement circuit breakers for external services
- Monitor and alert on system performance

## Integration Points

### Email Provider Integration
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Morning Star Academy <noreply@morningstaracademy.edu.gh>'
```

### Celery Configuration
```python
# celery.py
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379')
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
```

## API Endpoints

### Email Management
- `POST /api/applications/{id}/send-verification/` - Send verification email
- `GET /api/verify-email/{token}/` - Verify email address
- `POST /api/applications/{id}/resend-notification/` - Resend status notification
- `GET /api/applications/{id}/email-history/` - Get email communication history

### PDF Generation
- `GET /api/applications/{id}/download-pdf/` - Download application PDF
- `POST /api/applications/bulk-pdf/` - Generate bulk PDF export
- `GET /api/applications/{id}/pdf-status/` - Check PDF generation status

### Notification Preferences
- `GET /api/applications/{id}/preferences/` - Get notification preferences
- `PUT /api/applications/{id}/preferences/` - Update notification preferences
- `POST /api/unsubscribe/{token}/` - Unsubscribe from notifications

## Testing Strategy

### Unit Tests
- Email service functionality
- PDF generation accuracy
- Template rendering
- Model validation and methods

### Integration Tests
- End-to-end email workflows
- PDF download functionality
- Email verification process
- Status update notifications

### Performance Tests
- Email queue processing under load
- PDF generation performance
- Concurrent user scenarios
- Email delivery reliability

## Deployment Considerations

### Environment Configuration
- Email provider credentials
- Celery broker configuration
- PDF generation dependencies
- File storage for temporary PDFs

### Monitoring and Alerting
- Email delivery success rates
- Queue processing metrics
- PDF generation performance
- Error rates and failed operations

### Backup and Recovery
- Email log data backup
- Template version control
- Configuration backup
- Disaster recovery procedures