import time
import uuid

from django.conf import settings
from django.db import connection
from django.db.utils import ConnectionHandler

from tabulate import tabulate

from zgw_consumers.concurrent import parallel

TEST_QUERY = f"SELECT '{uuid.uuid4()}'"

SHOW_CONNECTIONS = (
    "SELECT datname, usename, state, query from pg_stat_activity WHERE usename = %s;"
)


def get_num_connections() -> int:
    """
    Connect to the "postgres" database to see pg_stat_activity data.

    We need raw psycopg2 cursor access here, because the test-runner creates a separate
    test database otherwise.
    """
    handler = ConnectionHandler({"default": settings.POSTGRES_CONN_PARAMS})
    connection = handler["default"]

    app_user = settings.DATABASES["default"]["USER"]

    # seems like the connections need some time to close on the backend?
    time.sleep(1)

    try:
        with connection.cursor() as cursor:
            # debug - show pg_stat_activity records
            cursor.execute(SHOW_CONNECTIONS, [app_user])
            rows = cursor.fetchall()

            headers = [x.name for x in cursor.description]
            tabulated = tabulate(rows, headers=headers)
            print("Open connections:")
            print(tabulated)

            # filter on the test query
            unexpected = [row for row in rows if row[-1] == TEST_QUERY]
            count = len(unexpected)
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
