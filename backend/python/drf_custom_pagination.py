"""
Custom cursor-based pagination for Django REST Framework.

Encodes the pagination cursor (ordering field value + row offset for ties)
as an opaque, URL-safe base64 token instead of exposing raw field values.
Clients receive `next`/`previous` links containing the encoded token and
never need to know the internal ordering field or its representation.
"""
import base64
import json

from rest_framework.pagination import CursorPagination


class OpaqueCursorPagination(CursorPagination):
    """Cursor pagination whose `cursor` query param is an opaque token."""

    page_size = 25
    max_page_size = 200
    page_size_query_param = "page_size"
    ordering = "-created_at"  # default ordering field, override per-view
    cursor_query_param = "cursor"

    def encode_cursor(self, cursor):
        """Serialize the internal Cursor namedtuple into an opaque token."""
        tokens = {
            "offset": cursor.offset,
            "reverse": cursor.reverse,
            "position": cursor.position,
        }
        encoded = base64.urlsafe_b64encode(
            json.dumps(tokens).encode("ascii")
        ).decode("ascii")

        # Build the URL exactly like the base class, but with our token.
        querystring = self._replace_query_param_or_remove(
            self.cursor_query_param, encoded
        )
        return querystring

    def _replace_query_param_or_remove(self, key, value):
        # Delegate to base helpers to keep other query params/ordering intact.
        request = self.request
        url = request.build_absolute_uri()
        from rest_framework.utils.urls import replace_query_param

        return replace_query_param(url, key, value)

    def decode_cursor(self, request):
        """Reverse of encode_cursor: turn the opaque token back into a Cursor."""
        encoded = request.query_params.get(self.cursor_query_param)
        if encoded is None:
            return None

        try:
            raw = base64.urlsafe_b64decode(encoded.encode("ascii"))
            tokens = json.loads(raw.decode("ascii"))
            offset = int(tokens["offset"])
            reverse = bool(tokens["reverse"])
            position = tokens["position"]
        except (TypeError, ValueError, KeyError):
            return None

        from rest_framework.pagination import Cursor

        return Cursor(offset=offset, reverse=reverse, position=position)
