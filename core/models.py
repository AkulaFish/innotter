from django.utils import timezone
from django.db import models

import uuid


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.UUIDField(auto_created=True, unique=True, default=uuid.uuid4)
    description = models.TextField()
    tags = models.ManyToManyField("core.Tag", related_name="pages", blank=True)
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="pages"
    )
    followers = models.ManyToManyField("users.User", related_name="follows", blank=True)
    image = models.ImageField(
        blank=True,
        default=None,
        null=True,
        upload_to="media/",
    )
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField(
        "users.User", related_name="requests", blank=True
    )
    permanent_block = models.BooleanField(default=False)
    unblock_date = models.DateTimeField(default=None, null=True, blank=True)

    @property
    def is_blocked(self):
        """
        This property defines whether page is still blocked if we set temporary blocking by using
        unblock_date field or whether page must stay blocked because of permanent block
        """
        if self.permanent_block:
            return True
        elif self.unblock_date and (self.owner.is_blocked or self.unblock_date > timezone.now()):
            return True
        else:
            self.unblock_date = None
            self.save()
            return False

    def __str__(self):
        return self.name


class Post(models.Model):
    subject = models.CharField(default="Post", null=False, max_length=200)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey(
        "core.Post",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )
    likes = models.ManyToManyField(
        "users.User", related_name="liked_posts", blank=True, default=[]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.pk} on page {self.page}"
