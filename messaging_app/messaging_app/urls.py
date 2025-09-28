from django.contrib import admin
from django.urls import path, include

# We are using versioning as a best practice, routing all API calls through api/v1/
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --------------------------------------------------------------------------
    # API Routes (v1)
    # --------------------------------------------------------------------------
    path('api/v1/chats/', include('chats.urls')), 
    
    # Include DRF's authentication views for login/logout (optional but useful)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
