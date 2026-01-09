import os
from google.genai import Client


def upload_local_file_to_cloud(local_path: str) -> str:
    """
    Uploads a local file to the Google File API so it can be accessed
    by agents with Code Execution enabled.
    """
    client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

    if not os.path.exists(local_path):
        return f"Error: File {local_path} not found."

    # Upload the file
    file_object = client.files.upload(file=local_path)

    # Return a structured string that the next agent can understand
    summary = f"FILE_UPLOADED_SUCCESSFULLY: Use filename '{file_object.name}' in your code executor. URI: {file_object.uri}"
    return {"status": "success", "summary": summary}
