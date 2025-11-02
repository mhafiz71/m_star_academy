# Design Document

## Overview

The Morning Star Academy Online Platform is a Django-based web application that serves as the school's digital presence and application portal. The system follows a traditional MVC architecture with Django's MVT (Model-View-Template) pattern, enhanced with Tailwind CSS for modern, responsive styling. The platform is designed to be scalable, maintainable, and user-friendly across all devices.

## Architecture

### System Architecture

The application follows a layered architecture approach:

```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│     (Templates + Tailwind CSS)     │
├─────────────────────────────────────┤
│            View Layer               │
│        (Django Views/URLs)          │
├─────────────────────────────────────┤
│           Business Logic            │
│         (Django Models)             │
├─────────────────────────────────────┤
│            Data Layer               │
│          (SQLite/PostgreSQL)        │
└─────────────────────────────────────┘
```

### Technology Stack

- **Backend Framework:** Django 4.2+
- **Frontend Styling:** Tailwind CSS via django-tailwind
- **Database:** SQLite (development), PostgreSQL (production ready)
- **Authentication:** Django's built-in authentication system
- **Static Files:** Django's static file handling
- **Forms:** Django Forms with Tailwind styling

## Components and Interfaces

### Core Applications

#### 1. Core App (`core`)
- **Purpose:** Main website functionality (Home, About pages)
- **Views:** HomeView, AboutView
- **Templates:** base.html, home.html, about.html
- **Static Assets:** Images, CSS overrides

#### 2. Applications App (`applications`)
- **Purpose:** Handle student application submissions
- **Models:** Application, Student, Guardian
- **Views:** ApplicationCreateView, ApplicationSuccessView
- **Forms:** ApplicationForm with validation
- **Templates:** application_form.html, application_success.html

#### 3. Administration App (`administration`)
- **Purpose:** Admin dashboard and application management
- **Views:** DashboardView, ApplicationListView, ApplicationDetailView
- **Decorators:** @login_required, @staff_member_required
- **Templates:** admin_dashboard.html, application_list.html, application_detail.html

### URL Structure

```
/                           # Home page
/about/                     # About page
/apply/                     # Application form
/apply/success/<ref_id>/    # Application success page
/admin-portal/              # Admin dashboard (staff only)
/admin-portal/applications/ # Application management
/admin-portal/applications/<id>/ # Application detail view
/accounts/login/            # Django admin login
/accounts/logout/           # Logout
```

### Navigation Component

The navigation will be implemented as a reusable template component:

```html
<!-- navigation.html -->
<nav class="bg-white shadow-lg">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between items-center py-4">
      <div class="flex items-center">
        <h1 class="text-2xl font-bold text-blue-600">Morning Star Academy</h1>
      </div>
      <div class="hidden md:flex space-x-8">
        <a href="{% url 'home' %}" class="nav-link">Home</a>
        <a href="{% url 'apply' %}" class="nav-link">Apply</a>
        <a href="{% url 'about' %}" class="nav-link">About</a>
        {% if user.is_staff %}
          <a href="{% url 'admin_dashboard' %}" class="nav-link">Admin</a>
        {% endif %}
      </div>
      <!-- Mobile menu button -->
    </div>
  </div>
</nav>
```

## Data Models

### Application Model

```python
class Application(models.Model):
    # Reference and tracking
    reference_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlist', 'Waitlisted'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Student Information
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_date_of_birth = models.DateField()
    student_gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    
    # Academic Information
    previous_school = models.CharField(max_length=200, blank=True)
    grade_applying_for = models.CharField(max_length=50)
    
    # Guardian Information
    guardian_first_name = models.CharField(max_length=100)
    guardian_last_name = models.CharField(max_length=100)
    guardian_relationship = models.CharField(max_length=50)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField()
    guardian_address = models.TextField()
    
    # Additional Information
    medical_conditions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        # Generate unique reference like MSA2024001
        pass
```

### User Profile Extension (Optional)

```python
class SchoolProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrator'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff Member'),
    ])
    department = models.CharField(max_length=100, blank=True)
```

## Error Handling

### Form Validation
- Client-side validation using HTML5 and JavaScript
- Server-side validation using Django Forms
- Custom validators for phone numbers, dates, and email formats
- Graceful error display with Tailwind styling

### Error Pages
- Custom 404 page with school branding
- Custom 500 page with contact information
- Form error handling with field-specific messages

### Exception Handling
```python
# views.py
def application_create_view(request):
    try:
        if request.method == 'POST':
            form = ApplicationForm(request.POST)
            if form.is_valid():
                application = form.save()
                return redirect('application_success', ref_id=application.reference_number)
        else:
            form = ApplicationForm()
    except Exception as e:
        logger.error(f"Application submission error: {e}")
        messages.error(request, "An error occurred. Please try again.")
    
    return render(request, 'applications/application_form.html', {'form': form})
```

## Testing Strategy

### Unit Tests
- Model validation tests
- Form validation tests
- View logic tests
- URL routing tests

### Integration Tests
- Full application submission workflow
- Admin dashboard functionality
- Authentication and authorization
- Navigation and page rendering

### Test Structure
```
tests/
├── test_models.py          # Model validation and methods
├── test_forms.py           # Form validation and processing
├── test_views.py           # View logic and responses
├── test_urls.py            # URL routing and resolution
└── test_integration.py     # End-to-end workflows
```

### Test Data
- Factory classes for creating test applications
- Fixtures for school information and user accounts
- Mock data for form submissions

## Design System and Styling

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'school-blue': '#1e40af',
        'school-gold': '#f59e0b',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### Component Classes
```css
/* Custom component classes */
.nav-link {
  @apply text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors;
}

.form-input {
  @apply mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
}
```

### Responsive Design Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px  
- Desktop: 1024px+

## Security Considerations

### Authentication & Authorization
- Django's built-in authentication system
- Staff-only access to admin areas using `@staff_member_required`
- Session-based authentication with secure cookies

### Data Protection
- CSRF protection on all forms
- SQL injection prevention through Django ORM
- XSS protection through template auto-escaping
- Secure password hashing using Django's default hashers

### Input Validation
- Server-side validation for all user inputs
- File upload restrictions (if implemented)
- Rate limiting for form submissions (optional)

### Environment Configuration
```python
# settings.py security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # Production only
```

## Deployment Considerations

### Environment Setup
- Virtual environment isolation
- Environment-specific settings files
- Static file collection and serving
- Database migrations

### Production Readiness
- PostgreSQL database configuration
- Static file serving via CDN or web server
- Environment variable management
- Logging configuration
- Error monitoring setup