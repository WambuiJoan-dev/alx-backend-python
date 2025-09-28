# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


# -----------------------------------------------------------------------------
# 1. User Model (Custom Extension)
# -----------------------------------------------------------------------------

class User(AbstractUser, PermissionsMixin):
    """
    Extends Django's built-in AbstractUser to add custom fields like phone_number and role.
    This model serves as the AUTH_USER_MODEL for the entire project.
    """
    
    # Custom Primary Key (UUID as specified in the database spec)
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="User ID"
        
    )
    
    # Redefine username field to use email for login (Django best practice for web apps)
    # The AbstractUser already provides first_name and last_name.
    # We rely on AbstractUser's email field which has unique=True and is NOT NULL if required.

    # Phone Number (VARCHAR, NULL)
    phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        verbose_name="Phone Number"
    )

    # Role (ENUM: 'guest', 'host', 'admin', NOT NULL)
    # We use a choices field for the ENUM type.
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='guest',
        verbose_name="User Role"
    )

    # created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    # Use email for authentication instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name'] # Keep username required for admin page creation

    # Set email as the unique identifier field 
    email = models.EmailField(unique=True) 

    password = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.email
        
    class Meta:
        # We specify the table name as a best practice
        db_table = 'user' 


# -----------------------------------------------------------------------------
# 2. Conversation Model
# -----------------------------------------------------------------------------

class Conversation(models.Model):
    """
    Represents a private conversation between two or more users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Conversation ID"
    )

    # participants_id (Foreign Key, references User(user_id)) - Many-to-Many Relationship
    # A conversation has many participants, and a user can be in many conversations.
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        verbose_name="Participants"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    def __str__(self):
        return f"Conversation {self.conversation_id.hex[:8]}"

    class Meta:
        db_table = 'conversation'
        # Order by most recently created
        ordering = ['-created_at'] 


# -----------------------------------------------------------------------------
# 3. Message Model
# -----------------------------------------------------------------------------

class Message(models.Model):
    """
    Represents an individual message within a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Message ID"
    )

    # sender_id (Foreign Key, references User(user_id))
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Sender"
    )

    # conversation (Foreign Key, references Conversation(conversation_id))
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name="Conversation"
    )

    # message_body (TEXT, NOT NULL)
    message_body = models.TextField(
        verbose_name="Message Body"
    )

    # sent_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sent At"
    )

    def __str__(self):
        return f"Message from {self.sender.first_name} in {self.conversation}"

    class Meta:
        db_table = 'message'
        # Order messages chronologically
        ordering = ['sent_at']
