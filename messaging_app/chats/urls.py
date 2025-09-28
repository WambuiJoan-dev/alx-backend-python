from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Use DefaultRouter to automatically generate CRUD URLs for ViewSets
router = DefaultRouter()

# Maps to: /api/v1/chats/conversations/ (GET, POST) and /api/v1/chats/conversations/{id}/ (GET, PUT, DELETE)
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Maps to: /api/v1/chats/messages/ (POST, GET)
# We use this for creating (sending) messages.
router.register(r'messages', MessageViewSet, basename='message')

# URL patterns for the chats app
urlpatterns = router.urls
