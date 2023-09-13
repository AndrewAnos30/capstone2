from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Website.urls')),
    path('', include('users.urls')),
<<<<<<< HEAD

=======
>>>>>>> 90b6c27b87d9b4586b9edce4faefb6a13180780b
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
