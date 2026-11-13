"""
Custom cursor-based pagination for Django REST Framework.

Encodes the pagination position (an ordering field value + direction) as an
opaque, base64-encoded JSON token instead of exposing raw field values in
the query string. This avoids leaking internal data (e.g. timestamps, IDs)
directly in URLs while still providing stable, efficient cursor pagination
on top of DRF's CursorPagination machinery.
"""

import base64
import json

from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import NotFound


class ObfuscatedCursorPagination(CursorPagination):
    """CursorPagination variant that opaquely encodes the cursor token."""

    page_size = 25
    max_page_size = 100
    ordering = "-created_at"  # must correspond to an indexed, unique-ish field
    cursor_query_param = "cursor"

    def encode_cursor(self, cursor):
        """Serialize the Cursor namedtuple into an opaque base64 token."""
        token = {
            "offset": cursor.offset,
            "reverse": cursor.reverse,
            "position": cursor.position,
        }
        raw = json.dumps(token, separators=(",", ":")).encode("utf-8")
        encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        # Build the URL with our opaque token instead of DRF's default encoding.
        url = self.base_url
        return replace_query_param(url, self.cursor_query_param, encoded)

    def decode_cursor(self, request):
        """Decode the opaque token back into a Cursor namedtuple."""
        encoded = request.query_params.get(self.cursor_query_param)
        if encoded is None:
            return None

        try:
            padding = "=" * (-len(encoded) % 4)
            raw = base64.urlsafe_b64decode(encoded + padding)
            token = json.loads(raw.decode("utf-8"))
            return Cursor(
                offset=int(token["offset"]),
                reverse=bool(token["reverse"]),
                position=token["position"],
            )
        except (TypeError, ValueError, KeyError, UnicodeDecodeError):
            raise NotFound("Invalid cursor")


# Imports placed here to keep the top of the file focused on the public class.
from rest_framework.pagination import Cursor  # noqa: E402
from rest_framework.utils.urls import replace_query_param  # noqa: E402
