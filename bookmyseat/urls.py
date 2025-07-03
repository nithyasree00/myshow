from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies.views import home  # ✅ Import the home view

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('movies.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
