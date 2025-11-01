"""
URL configuration for morning_star_academy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('apply/', include('applications.urls')),
    path('admin-portal/', include('administration.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Add browser reload for development
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
