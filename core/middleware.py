"""
Security middleware for Morning Star Academy
"""
import logging
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger('django.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add additional security headers to responses
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Add CSP header for development (basic)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data:;"
            )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for form submissions
    """
    
    def process_request(self, request):
        # Only apply rate limiting to POST requests
        if request.method != 'POST':
            return None
        
        # Skip rate limiting for authenticated staff users
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Rate limit key
        cache_key = f'rate_limit_{ip}'
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        # Rate limit: 10 requests per minute
        if current_count >= 10:
            logger.warning(f'Rate limit exceeded for IP: {ip}')
            return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 60 seconds
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Log security-related events
    """
    
    def process_request(self, request):
        # Log suspicious requests
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Log requests with suspicious user agents
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            logger.warning(
                f'Suspicious user agent detected: {user_agent} from IP: {self.get_client_ip(request)}'
            )
        
        # Log admin access attempts
        if request.path.startswith('/admin-portal/') and request.method == 'POST':
            user = getattr(request, 'user', AnonymousUser())
            if isinstance(user, AnonymousUser):
                logger.warning(
                    f'Unauthenticated admin access attempt from IP: {self.get_client_ip(request)}'
                )
        
        return None
    
    def process_response(self, request, response):
        # Log failed login attempts
        if (request.path == '/accounts/login/' and 
            request.method == 'POST' and 
            response.status_code == 200 and 
            'Please enter a correct username' in str(response.content)):
            
            logger.warning(
                f'Failed login attempt from IP: {self.get_client_ip(request)}'
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip