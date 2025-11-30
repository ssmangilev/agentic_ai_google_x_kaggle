import pandas as pd


def load_dataset(file_path: str) -> str:
    """
    Loads a CSV dataset and returns a summary of its columns and types.
    Use this to inspect the data structure before analysis.
    """
    try:
        df = pd.read_csv(file_path)
        # We don't return the whole DF text, just metadata to save token context
        summary = f"Loaded {len(df)} rows.\nColumns:\n{df.dtypes.to_string()}"
        return summary
    except Exception as e:
        return f"Error loading file: {str(e)}"
