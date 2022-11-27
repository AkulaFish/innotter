import os
import threading
from typing import List

import botocore.errorfactory
from django.core.mail import EmailMessage

from core.models import Post


def get_recipient_list(post: Post) -> List[str]:
    """Gets recipient email list from followers list of the page"""
    return [user.email for user in post.page.followers.all()]


def get_message(post: Post, recipient: str) -> EmailMessage:
    """Gets EmailMessage instance to be sent to users"""
    return EmailMessage(
        f"New Post!!! Subject: {post.subject}",
        f"Check out new post on {post.page} by {post.page.owner.get_full_name()}",
        os.getenv("FROM_EMAIL"),
        [recipient],
    )


def send_new_post_notification_email(post: Post) -> None:
    """Sends email newsletter"""
    for recipient in get_recipient_list(post):
        message = get_message(post, recipient)
        try:
            message.send(fail_silently=True)
        except botocore.errorfactory.ClientError:
            print(f"Email {recipient} wasn't validated")


def create_daemon_thread_for_email(post: Post) -> None:
    """Creates background thread to send notification email"""
    t = threading.Thread(
        target=send_new_post_notification_email, args=(post,), daemon=True
    )
    t.start()
