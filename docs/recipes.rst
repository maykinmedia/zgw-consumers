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

Using OAuth2 for authorization (client credentials flow)
********************************************************

You can set up a Service in order to use the OAuth2 client credentials flow by selecting
this in the ``Authorization type`` field (`OAuth2 client credentials flow`). This requires
the following:

1. The library must have been installed with the necessary packages

    .. code-block::

        (uv) pip install zgw-consumers[oauth2]
        
2. Provide the required fields in the service:

  - ``Client id``
  - ``Secret``
  - ``OAuth2 token url``
  - ``OAuth2 scope`` (`optional`)

When selecting this specific authorization flow, by default, the user credentials will be
part of the request headers when accessing the token endpoint (`Authorization Basic ...`).
The library gives you the opportunity to change that and include this data in the body 
instead. This can be done via the ``OAuth2 token method`` field.
