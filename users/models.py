from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from users.managers import UserManager


class User(AbstractBaseUser):
    """ Authorization User Model """

    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    email = models.EmailField(unique=True)
    image_s3_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices, default='user')
    title = models.CharField(max_length=80, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True
        return False

    def has_module_perms(self, *args):
        if self.is_admin:
            return True
        return False

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_admin(self):
        return True if self.role == 'admin' else False
