"""
Rewrite the URLs in anything that looks like a string, dict or list.
"""

from typing import Any, List, Optional, Union

from zds_client.client import Object

from ..nlx import Rewriter


class NLXClientMixin:
    """
    Enable URL rewriting for zds_client.Client clients.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rewriter = Rewriter()

    # def pre_request(self, method: str, url: str, **kwargs) -> Any:
    #     """
    #     Rewrite NLX urls in the request body and params.

    #     From NLX -> canonical.
    #     """
    #     json = kwargs.get("json")
    #     if json:
    #         self.rewriter.backwards(json)

    #     params = kwargs.get("params")
    #     if params:
    #         self.rewriter.backwards(params)

    #     return super().pre_request(method, url, **kwargs)

    def request(
        self, path: str, operation: str, method="GET", expected_status=200, **kwargs
    ) -> Union[List[Object], Object]:
        """
        Make the actual HTTP request.
        """
        # intercept canonical URLs and rewrite to NLX
        _paths = [path]
        self.rewriter.forwards(_paths)
        path = _paths[0]

        return super().request(
            path, operation, method=method, expected_status=expected_status, **kwargs
        )

    def post_response(
        self, pre_id: Any, response_data: Optional[Union[dict, list]] = None
    ) -> None:
        """
        Rewrite from NLX -> canonical.
        """
        if response_data:
            self.rewriter.backwards(response_data)
        super().post_response(pre_id, response_data)
