from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""

    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=("user", "manager", "admin"), required=True)
    title = serializers.CharField(max_length=255)
    is_blocked = serializers.BooleanField()
    image_s3_path = serializers.URLField(required=False)

    class Meta:
        model = User
        exclude = ("password", "groups", "user_permissions")


class RegisterUserSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(choices=User.Roles.choices, required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(required=True, write_only=True)
    image_s3_path = serializers.ImageField(required=False, allow_empty_file=False)
    user_permissions = serializers.HiddenField(default=[])
    groups = serializers.HiddenField(default=[])

    class Meta:
        model = User
        exclude = ("last_login", "date_joined", "is_blocked")

    def validate(self, attrs):
        """Password validation."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        """
        Overriding create method to not use additional
        password2 field for creating user instance,
        which is used only for password validation.
        """
        user = User.objects.create(
            email=validated_data["email"],
            role=validated_data["role"],
            title=validated_data["title"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["first_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user
