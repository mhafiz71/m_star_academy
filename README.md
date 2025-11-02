# Morning Star Academy - Online Application Platform

A comprehensive web application for managing student applications to Morning Star Academy, featuring automated email notifications, PDF generation, and administrative tools.

## 🌟 Features

- **Online Application System**: User-friendly application form with validation
- **Email Notifications**: Automated confirmation and status update emails
- **Administrative Portal**: Staff interface for managing applications
- **PDF Generation**: Downloadable application documents
- **Security Features**: Rate limiting, CSRF protection, and secure authentication
- **Responsive Design**: Mobile-friendly interface using Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher (for Tailwind CSS)
- Redis (for caching and async tasks)
- PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd morning_star_academy
   ```

2. **Create virtual environment**
   ```bash
   python -m venv morning_star_env
   source morning_star_env/bin/activate  # On Windows: morning_star_env\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Install Node.js dependencies (for Tailwind CSS)**
   ```bash
   cd theme/static_src
   npm install
   cd ../..
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

9. **Start development servers**
   ```bash
   # Terminal 1: Django development server
   python manage.py runserver
   
   # Terminal 2: Tailwind CSS watcher
   python manage.py tailwind start
   ```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following key variables:

#### Django Settings
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Database Configuration
```env
# For development (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# For production (PostgreSQL)
DATABASE_URL=postgres://user:password@host:port/database
```

#### Email Configuration
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Morning Star Academy <noreply@morningstaracademy.edu.gh>
```

#### School Information
```env
SCHOOL_NAME=Morning Star Academy
SCHOOL_ADDRESS=Tamale, Gbanyamli, Northern Region, Ghana
SCHOOL_PHONE=+233 XX XXX XXXX
SCHOOL_EMAIL=info@morningstaracademy.edu.gh
```

### Email Setup

#### Gmail Configuration
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password in `EMAIL_HOST_PASSWORD`

#### SendGrid Configuration (Alternative)
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

## 🏗️ Project Structure

```
morning_star_academy/
├── applications/          # Application management app
├── administration/        # Admin portal app
├── core/                 # Core utilities and services
├── templates/            # HTML templates
│   ├── emails/          # Email templates
│   ├── applications/    # Application templates
│   └── administration/ # Admin templates
├── static/              # Static files
├── theme/               # Tailwind CSS theme
├── morning_star_academy/ # Django project settings
│   └── settings/        # Environment-specific settings
├── logs/                # Application logs
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment template
└── requirements.txt     # Python dependencies
```

## 📧 Email System

The application includes a comprehensive email notification system:

### Email Types
- **Application Confirmation**: Sent when application is submitted
- **Status Updates**: Sent when application status changes (approved/rejected/waitlisted)
- **Email Verification**: For verifying guardian email addresses

### Email Templates
All email templates are located in `templates/emails/` and include:
- Professional branding and styling
- Responsive design for mobile devices
- School contact information
- Relevant application details

### Testing Emails
For development, use the console email backend:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## 🔒 Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **Rate Limiting**: Prevents spam and abuse
- **Secure Headers**: XSS protection, content type sniffing prevention
- **Session Security**: Secure cookie settings
- **Input Validation**: Comprehensive form validation
- **SQL Injection Protection**: Django ORM prevents SQL injection

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test applications
python manage.py test core

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📊 Monitoring and Logging

### Logging Configuration
Logs are written to the `logs/` directory:
- `django.log`: General application logs
- `errors.log`: Error-specific logs
- `security.log`: Security-related events
- `applications.log`: Application-specific logs

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages
- **ERROR**: Error conditions
- **CRITICAL**: Critical errors

## 🚀 Deployment

### Production Checklist

1. **Environment Configuration**
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   DATABASE_URL=postgres://user:password@host:port/database
   ```

2. **Security Settings**
   ```env
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Database Migration**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Using Gunicorn
```bash
gunicorn morning_star_academy.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Optional)
```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "morning_star_academy.wsgi:application"]
```

## 🛠️ Development

### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write Tests First**
   ```python
   # tests.py
   def test_new_feature(self):
       # Test implementation
       pass
   ```

3. **Implement Feature**
   ```python
   # views.py, models.py, etc.
   ```

4. **Update Documentation**
   ```markdown
   # Update README.md and docstrings
   ```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write comprehensive tests

### Pre-commit Hooks (Optional)
```bash
pip install pre-commit
pre-commit install
```

## 📞 Support

### School Contact Information
- **Address**: Tamale, Gbanyamli, Northern Region, Ghana
- **Landmark**: Near Kesmi FM Radio Station
- **Phone**: +233 XX XXX XXXX
- **Email**: info@morningstaracademy.edu.gh

### Technical Support
For technical issues or questions about the application:
1. Check the logs in the `logs/` directory
2. Review the Django debug information (if DEBUG=True)
3. Check email delivery status in the admin portal
4. Verify environment variable configuration

## 📄 License

This project is proprietary software developed for Morning Star Academy.

## 🙏 Acknowledgments

- Django framework and community
- Tailwind CSS for styling
- WeasyPrint for PDF generation
- All contributors and testers

---

**Morning Star Academy** - "Quality Education for a Brighter Future"