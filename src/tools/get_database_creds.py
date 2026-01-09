import os

from langfuse import observe


@observe
def get_postgres_conn_string() -> dict[str, any]:
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
        return {"status": "error", "message": "POSTGRES_CONN_STRING environment variable not found. Cannot connect to the database."}

    return {"status": "success", "conn_string": conn_string}
