# Gmail Email Configuration Guide

## Current Issue
The application is failing to send emails with error:
```
ERROR: (535, b'5.7.8 Username and Password not accepted. For more information, go to 5.7.8 https://support.google.com/mail/?p=BadCredentials')
```

## 🔧 Quick Fix Options

### Option 1: Use Console Backend for Development (Immediate Fix)
For development and testing, switch to console backend to see emails in the terminal:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Option 2: Fix Gmail Configuration

#### Step 1: Verify Gmail Account Settings
1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Security → 2-Step Verification
   - Turn on 2-Step Verification

#### Step 2: Generate New App Password
1. Go to Google Account → Security
2. Under "2-Step Verification" → App passwords
3. Select "Mail" and "Other (Custom name)"
4. Enter "Morning Star Academy" as the name
5. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)

#### Step 3: Update .env File
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-new-app-password
DEFAULT_FROM_EMAIL=Morning Star Academy <your-email@gmail.com>
```

## 🚀 Alternative Email Providers

### Option 3: Use SendGrid (Recommended for Production)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=Morning Star Academy <noreply@morningstaracademy.edu.gh>
```

### Option 4: Use Mailgun
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailgun-username
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=Morning Star Academy <noreply@morningstaracademy.edu.gh>
```

## 🧪 Testing Email Configuration

### Test with Management Command
```bash
python manage.py test_email --to test@example.com --type simple
python manage.py test_email --to test@example.com --type template
```

### Test in Django Shell
```python
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

# Test simple email
send_mail(
    'Test Email',
    'This is a test message.',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

## 🔍 Troubleshooting Steps

### 1. Check Gmail Security Settings
- Ensure 2FA is enabled
- Generate fresh app password
- Check if "Less secure app access" is disabled (should be)

### 2. Verify Network/Firewall
- Ensure port 587 is not blocked
- Check if your ISP blocks SMTP

### 3. Test Different Ports
Try these Gmail configurations:

**TLS (Port 587):**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

**SSL (Port 465):**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

### 4. Check Django Settings
Ensure these are in your settings:
```python
EMAIL_TIMEOUT = 30
EMAIL_USE_LOCALTIME = False
```

## 📋 Current Configuration Analysis

Your current .env shows:
```env
EMAIL_HOST_USER=abdulnasirmhafiz567@gmail.com
EMAIL_HOST_PASSWORD=yrrh mvix zbkm czrp 
```

**Potential Issues:**
1. App password might be expired or invalid
2. Extra space at end of password
3. Gmail account security settings changed

## ✅ Recommended Actions

### Immediate (Development):
1. Switch to console backend for testing
2. Verify form functionality works
3. Test email templates in console

### Production Setup:
1. Use SendGrid or Mailgun for reliability
2. Set up proper domain authentication
3. Configure SPF, DKIM, and DMARC records
4. Monitor email delivery rates

## 🔒 Security Best Practices

1. **Never commit real credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate passwords regularly**
4. **Monitor email logs** for suspicious activity
5. **Use dedicated email service** for production

## 📞 Support Resources

- **Gmail Help**: https://support.google.com/mail/answer/185833
- **SendGrid Docs**: https://docs.sendgrid.com/
- **Django Email Docs**: https://docs.djangoproject.com/en/stable/topics/email/