from rest_framework import serializers

from users.serializers import UserSerializer
from core.models import Page, Tag, Post


class TagSerializer(serializers.ModelSerializer):
    """Tag model serializer"""

    name = serializers.CharField(max_length=30)

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
    image = serializers.ImageField(allow_null=True, required=False)
    is_private = serializers.BooleanField(required=True)
    follow_requests = UserSerializer(read_only=True, many=True)
    permanent_block = serializers.BooleanField(read_only=True)
    unblock_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Page
        fields = "__all__"


class BlockPageSerializer(serializers.ModelSerializer):
    """Serializer for block"""

    permanent_block = serializers.BooleanField(default=False)
    unblock_date = serializers.DateTimeField(allow_null=True, default=None)

    class Meta:
        model = Page
        fields = (
            "permanent_block",
            "unblock_date",
        )


class PostSerializer(serializers.ModelSerializer):
    """Post model serializer"""

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

    def validate(self, attrs):
        """Validating if user has access to chosen page"""
        request = self.context.get("request")
        user = request.user
        if attrs["page"] not in user.pages.all():
            raise serializers.ValidationError(
                {"page": "You have no access to this page. " "Create your own page."}
            )
        return attrs
