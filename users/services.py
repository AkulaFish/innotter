from rest_framework.response import Response

from users.models import User


def block_unblock(user: User) -> Response:
    """Service that changes user is_blocked state and returns response"""
    if not user.is_blocked:
        user.is_blocked = True
        user.save()
        return Response({"response": "User successfully blocked"})
    else:
        user.is_blocked = False
        user.save()
        return Response({"response": "User unblocked"})
