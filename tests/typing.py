from typing import Literal, TypedDict


class OAuth2TokenEndpointAuthMethodOptions(TypedDict):
    oauth2_token_endpoint_auth_method: Literal["request_header", "request_body"]
