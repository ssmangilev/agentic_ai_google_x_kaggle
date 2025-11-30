import os


def get_postgres_conn_string() -> str:
    """
    Retrieves the PostgreSQL connection string from the POSTGRES_CONN_STRING
    environment variable. This string is necessary for connecting to the
    PostgreSQL database.

    :return: The PostgreSQL connection string as a string.
    :raises EnvironmentError: If the POSTGRES_CONN_STRING environment variable
    is not set.
    """
    conn_string = os.getenv("POSTGRES_CONN_STRING")

    if not conn_string:
        # Raise a specific error if the environment variable is missing
        raise EnvironmentError(
            "POSTGRES_CONN_STRING environment variable not found. "
            "Cannot connect to the database."
        )

    return conn_string
