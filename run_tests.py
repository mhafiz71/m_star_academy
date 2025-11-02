#!/usr/bin/env python
"""
Comprehensive test runner for Morning Star Academy project
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'morning_star_academy.settings.development'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules to run
    test_modules = [
        # Model tests
        'applications.tests.ApplicationModelTest',
        'applications.tests.ApplicationFormTest',
        
        # View tests
        'core.tests_views.PublicViewsTest',
        'core.tests_views.ApplicationViewsTest',
        'core.tests_views.AdminViewsTest',
        'core.tests_views.AuthenticationViewsTest',
        
        # Integration tests
        'applications.tests_integration.ApplicationWorkflowIntegrationTest',
        'applications.tests_integration.ErrorHandlingIntegrationTest',
        
        # Security tests
        'core.tests_security.SecurityHeadersTest',
        'core.tests_security.InputValidationTest',
        
        # Responsive design tests
        'core.tests_responsive.ResponsiveDesignTest',
        'core.tests_responsive.MobileFormTest',
        
        # Authentication tests
        'administration.tests.AuthenticationTest',
        'administration.tests.AdminAccessControlTest',
    ]
    
    print("Running Morning Star Academy Test Suite")
    print("=" * 50)
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")
        sys.exit(0)