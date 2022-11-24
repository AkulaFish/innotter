import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.email_services import send_new_post_notification_email
from core.services import get_tag_set_for_page
from users.serializers import UserSerializer
from core.models import Page, Tag, Post


class TagSerializer(serializers.ModelSerializer):
    """Tag model serializer"""

    name = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = Tag
        fields = "__all__"


class PageSerializer(serializers.ModelSerializer):
    """Page model serializer"""

    name = serializers.CharField(max_length=80, required=True)
    uuid = serializers.UUIDField(read_only=True, allow_null=True)
    description = serializers.CharField(allow_null=True)
    tags = TagSerializer(many=True, required=False)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    followers = UserSerializer(many=True, read_only=True)
    image = serializers.ImageField(
        allow_null=True, required=False, allow_empty_file=True
    )
    is_private = serializers.BooleanField(required=True)
    follow_requests = UserSerializer(read_only=True, many=True)
    permanent_block = serializers.BooleanField(read_only=True)
    unblock_date = serializers.DateTimeField(read_only=True, required=False)

    class Meta:
        model = Page
        fields = "__all__"

    def create(self, validated_data):
        """
        Overriding create method for Tag nested serializer
        implemented in page serializer tags field
        """
        tags = [dict(tag) for tag in validated_data.pop("tags")]
        instance = Page.objects.create(**validated_data)
        instance.tags.set(get_tag_set_for_page(tags=tags))
        return instance

    def update(self, instance, validated_data):
        """
        Overriding update method for Tag nested serializer
        implemented in page serializer tags field
        """
        tags = validated_data.pop("tags", [])
        instance = super().update(instance, validated_data)
        instance.tags.set(get_tag_set_for_page(tags=tags))
        return instance

    def validate(self, attrs):
        image = attrs.get("image")
        if not image:
            return attrs
        elif not image.endswith(".jpg"):
            raise ValidationError({"detail": "Incorrect picture format."})
        return attrs


class BlockPageSerializer(serializers.ModelSerializer):
    """Serializer for block"""

    permanent_block = serializers.BooleanField(required=False, default=True)
    unblock_date = serializers.DateTimeField(
        required=False, default=None, allow_null=True
    )

    class Meta:
        model = Page
        fields = ("permanent_block", "unblock_date")

    def validate(self, attrs):
        unblock_date = attrs.get("unblock_date")
        if not unblock_date:
            return attrs
        elif unblock_date < timezone.now():
            raise ValidationError({"detail": "Incorrect unblock date"})
        return attrs


class PostSerializer(serializers.ModelSerializer):
    """Post model serializer"""

    subject = serializers.CharField(required=True, max_length=200)
    page = serializers.PrimaryKeyRelatedField(queryset=Page.objects.all())
    content = serializers.CharField(max_length=180)
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(), required=False, allow_empty=True
    )
    likes = UserSerializer(read_only=True, many=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"
        partial = True

    def validate(self, attrs):
        """Validating if user has access to chosen page"""
        request = self.context.get("request")
        user = request.user
        if attrs.get("page") not in user.pages.all():
            raise serializers.ValidationError({"detail": "Invalid page"})
        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data=validated_data)
        send_new_post_notification_email(post=instance)
        return instance
