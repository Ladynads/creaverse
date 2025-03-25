"""
URL configuration for creaverse project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import home_view


urlpatterns = [
    # Home Route 
    path('', home_view, name='home'),
    
    # Admin Panel 
    path('admin/', admin.site.urls),

    # Users App 
    path('users/', include('users.urls')),

    # Feed App 
    path('feed/', include('feed.urls')),
]

# Media files in development 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar 
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
