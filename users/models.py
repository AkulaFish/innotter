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
    image_s3_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices, default=Roles.USER)
    title = models.CharField(max_length=80, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username

    @property
    def is_active(self):
        return not self.is_blocked

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR

    @property
    def is_superuser(self):
        return self.is_admin
