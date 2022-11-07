import uuid as uuid
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.UUIDField(auto_created=True,
                            unique=True,
                            default=uuid.uuid4()
                            )
    description = models.TextField()
    tags = models.ManyToManyField('core.Tag', related_name='pages')
    owner = models.ForeignKey('users.User',
                              on_delete=models.CASCADE,
                              related_name='pages'
                              )
    followers = models.ManyToManyField('users.User', related_name='follows')
    image = models.URLField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('users.User',
                                             related_name='requests',
                                             default=[]
                                             )
    unblock_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    page = models.ForeignKey(Page,
                             on_delete=models.CASCADE,
                             related_name='posts'
                             )
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey('core.Post',
                                 on_delete=models.SET_NULL, null=True,
                                 blank=True, related_name='replies'
                                 )
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post on page {self.page} {self.pk}'
