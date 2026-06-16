from typing import TYPE_CHECKING

from requests import Response

if TYPE_CHECKING:
    from ape_pie import APIClient

    Protocol = APIClient
else:
    Protocol = object


class RefreshTokenMixin(Protocol):
    def request(
        self, method: str | bytes, url: str | bytes, *args, **kwargs
    ) -> Response:
        from .client import ZGWAuth  # circular import

        response = super().request(method, url, *args, **kwargs)

        if response.status_code != 403 or not isinstance(self.auth, ZGWAuth):
            return response

        self.auth.refresh_token()

        # Retry with the fresh credentials
        return super().request(method, url, *args, **kwargs)
