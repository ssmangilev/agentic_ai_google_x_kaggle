import os

from typing import Dict


def save_chart_image(figure_object, file_path: str) -> Dict[str, str]:
    """
    TOOL: Saves a chart figure object (Plotly or Matplotlib/Seaborn)
    as an image.

    Supported:
      - Plotly: fig.write_image("path")
      - Matplotlib: fig.savefig("path")

    :param figure_object: The chart object produced by the Visualization Agent.
    :param file_path: The output file path (e.g., "./exports/chart.png")
    :return: Dict with status and file path.
    """
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Detect Plotly
        if hasattr(figure_object, "write_image"):
            figure_object.write_image(file_path)

        # Detect Matplotlib Figure
        elif hasattr(figure_object, "savefig"):
            figure_object.savefig(file_path, dpi=300, bbox_inches="tight")

        else:
            return {
                "status": "error",
                "message": "Unsupported figure type — cannot save.",
                "file_path": file_path
            }

        return {
            "status": "success",
            "message": f"Chart saved successfully to {file_path}",
            "file_path": file_path
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save chart: {e}",
            "file_path": file_path
        }
