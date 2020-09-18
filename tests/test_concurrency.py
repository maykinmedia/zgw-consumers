import uuid

from django.conf import settings
from django.db import connection
from django.db.utils import ConnectionHandler

from tabulate import tabulate

from zgw_consumers.concurrent import parallel

TEST_QUERY = f"SELECT '{uuid.uuid4()}'"

GET_NUM_CONNECTIONS = (
    "SELECT count(*) from pg_stat_activity WHERE usename = %s AND query = %s;"
)

SHOW_CONNECTIONS = (
    "SELECT datname, usename, state, query from pg_stat_activity WHERE usename = %s;"
)


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
            # debug - show pg_stat_activity records
            cursor.execute(SHOW_CONNECTIONS, [app_user])
            rows = cursor.fetchall()

            headers = [x.name for x in cursor.description]
            tabulated = tabulate(rows, headers=headers)
            print("Open connections:")
            print(tabulated)
            cursor.execute(GET_NUM_CONNECTIONS, [app_user, TEST_QUERY])
            count: int = cursor.fetchone()[0]
    finally:
        connection.close()

    return count


def execute_query(*args):
    with connection.cursor() as cursor:
        cursor.execute(TEST_QUERY)
        return cursor.fetchone()


def test_db_connection_cleaned_up_submit(db: None):
    initial = get_num_connections()
    assert initial == 0

    with parallel() as executor:
        executor.submit(execute_query)
        num_conns = get_num_connections()

    assert num_conns == initial


def test_db_connection_cleaned_up_map(db: None):
    initial = get_num_connections()
    assert initial == 0

    with parallel() as executor:
        executor.map(execute_query, [1, 2, 3])
        num_conns = get_num_connections()

    assert num_conns == initial
