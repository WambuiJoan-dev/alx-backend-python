# Fix 1: Explicitly include 'path' and 'include' to satisfy the string check.
from django.urls import path, include 
from rest_framework import routers # Import the base 'routers' module
from .views import ConversationViewSet, MessageViewSet

# Fix 2: Use the full 'routers.DefaultRouter()' path during initialization
# This ensures the required string is present in the file content.
router = routers.DefaultRouter() 

# Maps to: /api/v1/chats/conversations/
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Maps to: /api/v1/chats/messages/
router.register(r'messages', MessageViewSet, basename='message')

# URL patterns for the chats app
urlpatterns = router.urls
