"""
URL configuration for creaverse project.

The `urlpatterns` list routes URLs to views. For more information, please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view

urlpatterns = [
    # ✅ Home Route
    path('', home_view, name='home'),
    
    # ✅ Admin Panel
    path('admin/', admin.site.urls),

    # ✅ Include Users & Authentication URLs
    path('feed/', include('feed.urls')),
    path('users/', include('users.urls')),

    # ✅ Home Route (Redirect to Feed)
    path('feed/', include('feed.urls')),
]

# ✅ Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # ✅ Include Debug Toolbar URLs (Only in Development)
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),  
    ]
