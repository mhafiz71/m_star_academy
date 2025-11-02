"""
Custom error handlers for Morning Star Academy
"""
import logging
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

logger = logging.getLogger(__name__)


def custom_404_handler(request, exception):
    """
    Custom 404 error handler
    """
    logger.warning(f'404 error: {request.path} - User: {request.user} - IP: {get_client_ip(request)}')
    
    try:
        template = get_template('404.html')
        return HttpResponseNotFound(template.render({
            'request': request,
            'exception': exception,
        }))
    except TemplateDoesNotExist:
        # Fallback to simple 404 response
        return HttpResponseNotFound('<h1>Page Not Found</h1>')


def custom_500_handler(request):
    """
    Custom 500 error handler
    """
    logger.error(f'500 error: {request.path} - User: {request.user} - IP: {get_client_ip(request)}')
    
    try:
        template = get_template('500.html')
        return HttpResponseServerError(template.render({
            'request': request,
        }))
    except TemplateDoesNotExist:
        # Fallback to simple 500 response
        return HttpResponseServerError('<h1>Server Error</h1>')


def custom_403_handler(request, exception):
    """
    Custom 403 error handler
    """
    logger.warning(f'403 error: {request.path} - User: {request.user} - IP: {get_client_ip(request)}')
    
    try:
        template = get_template('403.html')
        return HttpResponseForbidden(template.render({
            'request': request,
            'exception': exception,
            'user': request.user,
        }))
    except TemplateDoesNotExist:
        # Fallback to simple 403 response
        return HttpResponseForbidden('<h1>Access Denied</h1>')


def custom_400_handler(request, exception):
    """
    Custom 400 error handler
    """
    logger.warning(f'400 error: {request.path} - User: {request.user} - IP: {get_client_ip(request)}')
    
    # For 400 errors, we'll use a simple template or redirect to home
    context = {
        'request': request,
        'exception': exception,
        'error_message': 'Bad Request - The request could not be understood by the server.',
    }
    
    try:
        return render(request, '400.html', context, status=400)
    except TemplateDoesNotExist:
        return render(request, '404.html', context, status=400)


def get_client_ip(request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip