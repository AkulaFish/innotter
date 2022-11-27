from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Authorization User Model."""

    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    image_s3_path = models.ImageField(
        blank=True,
        default=None,
        null=True,
        upload_to="media/",
    )
    role = models.CharField(max_length=9, choices=Roles.choices, default=Roles.USER)
    title = models.CharField(max_length=80, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        """Overriding default is_active, so it depends on is_blocked."""
        return not self.is_blocked

    @property
    def is_staff(self):
        """Shortcut to determine user with any privileges(admin or moderator)."""
        return self.is_admin or self.is_moderator

    @property
    def is_admin(self):
        """
        Shortcut to define if user is admin.
        (Also overriding default is_admin role provided by Django)
        """
        return self.role == self.Roles.ADMIN

    @property
    def is_moderator(self):
        """Shortcut to define if user is moderator"""
        return self.role == self.Roles.MODERATOR

    @property
    def is_superuser(self):
        """
        Overriding default is_admin to associate
        it with new custom role of Admin
        """
        return self.is_admin
