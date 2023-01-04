from rest_framework.response import Response

from users.models import User


def change_block_state(user: User, if_block: User.BlockState) -> Response:
    """Service that changes user is_blocked state and returns response"""
    if if_block == User.BlockState.BLOCK:
        user.is_blocked = True
        user.save()
        return Response({"response": "User successfully blocked"})
    else:
        user.is_blocked = False
        user.save()
        return Response({"response": "User unblocked"})
