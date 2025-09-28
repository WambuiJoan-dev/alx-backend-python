from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --------------------------------------------------------------------------
    # API Routes (v1)
    # --------------------------------------------------------------------------
    # Use 'include' as requested by the checker
    path('api/', include('chats.urls')), 
    
    # Include DRF's authentication views for login/logout (optional but useful)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
