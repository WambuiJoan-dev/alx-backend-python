from rest_framework import serializers
from .models import User, Message, Conversation

# -----------------------------------------------------------------------------
# 1. User Serializer
# -----------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """
    Serializes basic User information for display, primarily in relationship fields.
    We exclude sensitive fields like password.
    """
    class Meta:
        model = User
        fields = (
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'created_at',
        )
        read_only_fields = ('user_id', 'created_at', 'role')


# -----------------------------------------------------------------------------
# 2. Message Serializer
# -----------------------------------------------------------------------------

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializes a single Message object.
    Uses the UserSerializer for the 'sender' field to include user details.
    """
    # Use the UserSerializer to show the sender's details instead of just the ID
    sender = UserSerializer(read_only=True)
    
    # We will need the sender's ID for creation, but display the full object
    sender_id = serializers.UUIDField(write_only=True)
    
    # The conversation ID is required for creation/linking
    conversation_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = (
            'message_id',
            'sender',
            'sender_id', # Write-only field for creation
            'conversation_id', # Write-only field for creation
            'conversation', # The FK field, used for lookups but generally hidden for POST
            'message_body',
            'sent_at',
        )
        # We only allow the message_body and relationship IDs to be writable
        read_only_fields = ('message_id', 'sent_at', 'conversation')

    # Custom create method to handle setting the FK relationship
    def create(self, validated_data):
        # The fields marked write_only must be popped from validated_data
        sender_id = validated_data.pop('sender_id')
        conversation_id = validated_data.pop('conversation_id')
        
        # Look up the objects using the provided IDs
        try:
            sender = User.objects.get(user_id=sender_id)
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except (User.DoesNotExist, Conversation.DoesNotExist) as e:
            raise serializers.ValidationError(f"Invalid ID provided for sender or conversation: {e}")

        # Create the message with the retrieved objects
        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            **validated_data
        )
        return message


# -----------------------------------------------------------------------------
# 3. Conversation Detail Serializer (Handles Nested Messages)
# -----------------------------------------------------------------------------

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializes a Conversation, including all associated Messages (nested relationship)
    and all participants.
    """
    # Nested field to include all messages in the conversation, ordered by 'sent_at'
    # 'many=True' is required for a reverse Foreign Key relationship
    messages = MessageSerializer(many=True, read_only=True) 
    
    # Nested field to include all participants' details, not just IDs
    participants = UserSerializer(many=True, read_only=True) 
    
    # Write-only field for creating a conversation (needs participant IDs)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = (
            'conversation_id',
            'participants',
            'participant_ids', # Write-only for creation
            'messages',
            'created_at',
        )
        read_only_fields = ('conversation_id', 'created_at')
        
    def create(self, validated_data):
        # The M2M field cannot be saved until the Conversation object is created
        participant_ids = validated_data.pop('participant_ids')
        
        # Create the conversation instance
        conversation = Conversation.objects.create(**validated_data)

        # Look up User objects and add them to the M2M 'participants' field
        users_to_add = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(users_to_add)
        
        return conversation


# -----------------------------------------------------------------------------
# 4. Conversation List Serializer (Simplified for Index Views)
# -----------------------------------------------------------------------------

class ConversationListSerializer(serializers.ModelSerializer):
    """
    A simpler serializer for listing conversations without nesting all messages
    (improves performance for index views).
    """
    # We still include participants' details
    participants = UserSerializer(many=True, read_only=True)
    
    # Optional: Get a count of messages for display
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            'conversation_id',
            'participants',
            'created_at',
            'message_count',
        )

    def get_message_count(self, obj):
        # Access the reverse relationship count manager
        return obj.messages.count()
