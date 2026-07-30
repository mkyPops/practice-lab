"""
JWT authentication middleware for Django.

Validates a Bearer JWT from the Authorization header on each request,
looks up the corresponding user, and attaches it to `request.user`.
Requests without a valid token fall back to Django's AnonymousUser,
allowing downstream views/permissions to decide how to handle access.
"""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

JWT_SECRET = getattr(settings, "JWT_SECRET", settings.SECRET_KEY)
JWT_ALGORITHMS = getattr(settings, "JWT_ALGORITHMS", ["HS256"])
JWT_USER_ID_CLAIM = getattr(settings, "JWT_USER_ID_CLAIM", "user_id")


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Authenticates requests using a Bearer JWT in the Authorization header."""

    def process_request(self, request):
        request.user = AnonymousUser()

        auth_header = request.headers.get("Authorization", "")
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            # No usable credentials supplied; leave request anonymous.
            return None

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHMS)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

        user_id = payload.get(JWT_USER_ID_CLAIM)
        if user_id is None:
            return None

        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None

        request.user = user
        # Stash the decoded payload in case views need extra claims.
        request.jwt_payload = payload
        return None
