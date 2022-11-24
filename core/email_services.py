from typing import List

from django.core.mail import EmailMessage

from core.models import Post


def get_recipient_list(post: Post) -> List[str]:
    """Gets recipient email list from followers list of the page"""
    return [user.email for user in post.page.followers.all()]


def get_message(post: Post) -> EmailMessage:
    """Gets EmailMessage instance to be sent to users"""
    return EmailMessage(
        f"New Post!!! Subject: {post.subject}",
        f"Check out new post on {post.page} by {post.page.owner.get_full_name()}",
        "denisvoytehovich3@gmail.com",
        get_recipient_list(post),
    )


def send_new_post_notification_email(post: Post) -> None:
    """Sends email newsletter"""
    message = get_message(post)
    message.send(fail_silently=True)