import logging
from typing import List

import botocore.errorfactory
from celery import shared_task
from django.core.mail import EmailMessage
from innotter import settings

from core.models import Post


def get_recipient_list(post: Post) -> List[str]:
    """Gets recipient email list from followers list of the page"""
    return [user.email for user in post.page.followers.all()]


def get_message(post: Post, recipient: str) -> EmailMessage:
    """Gets EmailMessage instance to be sent to users"""
    return EmailMessage(
        f"New Post!!! Subject: {post.subject}",
        f"Check out new post on {post.page} by {post.page.owner.username}",
        settings.FROM_EMAIL,
        [recipient],
    )


@shared_task
def send_new_post_notification_email(post_id: int) -> None:
    """Sends email newsletter"""
    post = Post.objects.get(pk=post_id)
    for recipient in get_recipient_list(post):
        message = get_message(post, recipient)
        try:
            message.send(fail_silently=True)
        except (botocore.errorfactory.ClientError, Exception):
            logging.error(f"Email {recipient} wasn't validated")
