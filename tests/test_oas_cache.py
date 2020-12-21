import threading

from zds_client.oas import schema_fetcher


def test_schema_fetch_twice(oas):
    schema = oas.fetch()

    assert isinstance(schema, dict)
    assert oas.mocker.call_count == 1

    oas.fetch()

    # check that the cache is used
    assert oas.mocker.call_count == 1


def test_clear_caches_in_between(oas):
    schema = oas.fetch()

    assert isinstance(schema, dict)
    assert oas.mocker.call_count == 1

    schema_fetcher.cache.clear()

    oas.fetch()

    assert oas.mocker.call_count == 2


def test_cache_across_threads(oas):
    def _target():
        # disable the local python cache
        schema_fetcher.cache._local_cache = {}
        oas.fetch()

    thread1 = threading.Thread(target=_target)
    thread2 = threading.Thread(target=_target)
    # start thread 1 and let it complete, this ensures the schema is stored in the
    # cache
    thread1.start()
    thread1.join()

    # start thread 2 and let it complete, we can now verify the call count
    thread2.start()
    thread2.join()

    assert oas.mocker.call_count == 1
