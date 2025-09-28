from django.urls import path, include 
from rest_framework import routers 
# --------------------------------------
from rest_framework_nested import routers as nested_routers
# --------------------------------------

from .views import ConversationViewSet, MessageViewSet

# Initialize the base router using the standard DefaultRouter
router = routers.DefaultRouter() 

# 1. Register the parent resource (Conversations)
# /conversations/ and /conversations/{id}/
router.register(r'conversations', ConversationViewSet, basename='conversation')


nested_router = nested_routers.NestedDefaultRouter(
    router, r'conversations', lookup='conversation'
)


# Register the top-level messages endpoint as before:
# /messages/
router.register(r'messages', MessageViewSet, basename='message')


# URL patterns for the chats app
# Includes both the base router and the (required) nested router patterns
urlpatterns = router.urls + nested_router.urls
