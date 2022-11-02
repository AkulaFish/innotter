from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    role = serializers.CharField(max_length=7)
    title = serializers.CharField(max_length=255)
    is_blocked = serializers.BooleanField()
    image_s3_path = serializers.URLField()

    class Meta:
        model = User
        exclude = ('password',)


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(choices=('user', 'manager', 'admin'), required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        exclude = ('last_login',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            role=validated_data['role'],
            title=validated_data['title'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
