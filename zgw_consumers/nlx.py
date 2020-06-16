"""
Rewrite the URLs in anything that looks like a string, dict or list.
"""
from typing import Any, Iterable, List, Optional, Union

from zds_client.client import Object

from .models import Service


def _rewrite_url(value: str, rewrites: Iterable) -> Optional[str]:
    for start, replacement in rewrites:
        if not value.startswith(start):
            continue

        return value.replace(start, replacement, 1)

    return None


class Rewriter:
    def __init__(self):
        self.rewrites = Service.objects.exclude(nlx="").values_list("api_root", "nlx")

    @property
    def reverse_rewrites(self):
        return [(to_value, from_value) for from_value, to_value in self.rewrites]

    def forwards(self, data: Union[list, dict]):
        """
        Rewrite URLs from from_value to to_value.
        """
        self._rewrite(data, self.rewrites)

    def backwards(self, data: Union[list, dict]):
        """
        Rewrite URLs from to_value to from_value.
        """
        self._rewrite(data, self.reverse_rewrites)

    def _rewrite(self, data: Union[list, dict], rewrites: Iterable) -> None:
        if isinstance(data, list):
            new_items = []
            for item in data:
                if isinstance(item, str):
                    new_value = _rewrite_url(item, rewrites)
                    if new_value:
                        new_items.append(new_value)
                    else:
                        new_items.append(item)
                else:
                    self._rewrite(item, rewrites=rewrites)
                    new_items.append(item)

            # replace list elements
            assert len(new_items) == len(data)
            for i in range(len(data)):
                data[i] = new_items[i]
            return

        if not isinstance(data, dict):
            return

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                self._rewrite(value, rewrites=rewrites)
                continue

            elif not isinstance(value, str):
                continue

            assert isinstance(value, str)

            rewritten = _rewrite_url(value, rewrites)
            if rewritten is not None:
                data[key] = rewritten


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
