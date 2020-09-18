from django.conf import settings
from django.db import connection
from django.db.utils import ConnectionHandler

from zgw_consumers.concurrent import parallel

GET_NUM_CONNECTIONS = "SELECT count(*) from pg_stat_activity WHERE usename = %s;"


def get_num_connections() -> int:
    """
    Connect to the "postgres" database to see pg_stat_activity data.

    We need raw psycopg2 cursor access here, because the test-runner creates a separate
    test database otherwise.
    """
    handler = ConnectionHandler(databases={"default": settings.POSTGRES_CONN_PARAMS})
    handler.ensure_defaults("default")
    connection = handler["default"]

    app_user = settings.DATABASES["default"]["USER"]

    try:
        with connection.cursor() as cursor:
            cursor.execute(GET_NUM_CONNECTIONS, [app_user])
            count: int = cursor.fetchone()[0]
        return count
    finally:
        connection.close()

    return count


def execute_query(*args):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")


def test_db_connection_cleaned_up_submit(db: None):
    initial = get_num_connections()
    assert initial >= 1

    with parallel() as executor:
        executor.submit(execute_query)
        num_conns = get_num_connections()

    assert num_conns == initial


def test_db_connection_cleaned_up_map(db: None):
    initial = get_num_connections()
    assert initial >= 1

    with parallel() as executor:
        executor.map(execute_query, [1, 2, 3])
        num_conns = get_num_connections()

    assert num_conns == initial
