from django.http import HttpRequest

NOTSET = object()


class cache_on_request:
    def __init__(self, request: HttpRequest, key: str, callback: callable):
        self.request = request
        self.key = key
        self.callback = callback

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def value(self):
        # check if it's cached on the request
        cached_value = getattr(self.request, self.key, NOTSET)
        if cached_value is NOTSET:
            value = self.callback()
            setattr(self.request, self.key, value)
            cached_value = value
        return cached_value
