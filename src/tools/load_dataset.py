import pandas as pd

from langfuse import observe


@observe
def load_dataset(file_path: str) -> dict[str, any]:
    """
    Loads a CSV dataset and returns a summary of its columns and types.
    Use this to inspect the data structure before analysis.
    """
    try:
        df = pd.read_json(file_path)
        # We don't return the whole DF text, just metadata to save token context
        summary = f"Loaded {len(df)} rows.\nColumns:\n{df.dtypes.to_string()}"
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "message": f"Sorry, I encountered an error: {str(e)}"} # NOQA
