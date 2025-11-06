# Morning Star Academy - Online Application Platform

Web application for managing student applications with automated email notifications and administrative tools.

## 🌟 Features

- Online application form with validation
- Email notifications for confirmations and status updates
- Administrative portal for staff
- Responsive design with Tailwind CSS
- Security features and rate limiting

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (for Tailwind CSS)

### Installation

1. **Setup Environment**
   ```bash
   git clone <repository-url>
   cd morning_star_academy
   python -m venv morning_star_env
   source morning_star_env/bin/activate  # Windows: morning_star_env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Setup Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start Development**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver
   
   # Terminal 2: Tailwind CSS (optional)
   cd theme/static_src && npm install && npm run dev
   ```

## ⚙️ Configuration

### Key Environment Variables
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# School Info
SCHOOL_NAME=Morning Star Academy
SCHOOL_EMAIL=info@morningstaracademy.edu.gh
```

### Email Setup
For Gmail: Enable 2FA → Generate App Password → Use in `EMAIL_HOST_PASSWORD`

## 🧪 Testing
```bash
python manage.py test                    # Run all tests
python manage.py test applications       # Run specific app tests
```

## 🚀 Production Deployment
```bash
# Set production environment
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Collect static files and migrate
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser

# Run with Gunicorn
gunicorn morning_star_academy.wsgi:application
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