Recipes
=======

Handling pagination in API endpoints
************************************

If an API endpoint implements pagination like this:

.. code-block:: json

    {
        "count": 250,
        "next": "<url that points to the next page>",
        "previous": "<url that points to the previous page>",
        "results": [{"name": "foo"}, {"name": "bar"}]
    }

You can easily retrieve all results by using :func:`zgw_consumers.service.pagination_helper`: this function
keeps fetching the ``next`` page (if it exists) and returns the merged ``results`` when it reaches the
last page.

.. code-block:: python

    from zgw_consumers.client import build_client
    from zgw_consumers.models import Service
    from zgw_consumers.service import pagination_helper

    my_service = Service.objects.get(api_root="https://api.example.com/")
    client = build_client(my_service)

    with client:
        response = client.get("books")
        response.raise_for_status()
        data = response.json()

        all_data = list(pagination_helper(client, data))

The implementation of :func:`zgw_consumers.service.pagination_helper` can be used as
inspiration for other pagination data shapes.
