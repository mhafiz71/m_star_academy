# Morning Star Academy - Online Application Platform

Web application for managing student applications with automated email notifications and administrative tools.

## Features

- Online application form with validation
- Email notifications for confirmations and status updates
- Administrative portal for staff
- Responsive design with Tailwind CSS

## Quick Start

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
   python manage.py runserver
   ```

## Configuration

### Environment Variables
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SCHOOL_NAME=Morning Star Academy
SCHOOL_EMAIL=info@morningstaracademy.edu.gh
```

## Contact

**Morning Star Academy**
- Address: Tamale, Gbanyamli, Northern Region, Ghana
- Phone: +233 XX XXX XXXX
- Email: info@morningstaracademy.edu.gh