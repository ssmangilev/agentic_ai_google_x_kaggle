import io
import json
from fpdf import FPDF
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool
from google.genai.types import Part, Blob


async def create_pdf_file(
    content_data: str, # This is now the JSON string you provided
    tool_context: ToolContext,
    filename: str = "report.pdf",
):
    breakpoint()
    # Parse the incoming data
    data = json.loads(content_data) if isinstance(content_data, str) else content_data

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 20)

    # --- Title ---
    pdf.cell(0, 10, "Wine Quality Analysis Report", ln=True, align='C')
    pdf.ln(10)

    # --- Summary ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 7, data.get("summary", ""))
    pdf.ln(5)

    # --- Key Metrics Table ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Key Metrics", ln=True)

    # Formatting the markdown table into a PDF table
    # Simple strategy: split by newline and pipe
    pdf.set_font("helvetica", size=9)
    metrics_table = data.get("metrics_table", "").split("\n")
    with pdf.table() as table:
        for row in metrics_table:
            if "|" in row and "---" not in row:
                cols = [c.strip().replace("**", "") for c in row.split("|") if c.strip()]
                if cols:
                    row_cells = table.row()
                    for col in cols:
                        row_cells.cell(col)
    pdf.ln(10)

    # --- Visual Evidence (Images) ---
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Visual Evidence", ln=True)
    charts_artifact = await tool_context.list_artifacts()
    charts_names = data.get("charts", [])
    version_id = 0
    while True:
        try:
            version_data = await tool_context.load_artifact(
                filename=charts_artifact[0],
                version=version_id)
            if not version_data:
                break
            img_bytes = version_data.inline_data.data
            # Write to a temp buffer for FPDF
            img_io = io.BytesIO(img_bytes)
            pdf.image(img_io, w=100)  # Adjust width as needed
            pdf.ln(5)
            pdf.set_font("helvetica", "I", 8)
            pdf.cell(0, 5, f"Figure: {charts_names[version_id]}", ln=True, align='C')
            pdf.ln(5)
            version_id += 1
        except IndexError:
            break
    # --- Insights ---
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Insights & Patterns", ln=True)
    pdf.set_font("helvetica", size=11)

    insights = data.get("insights", {})
    for key, val in insights.items():
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 7, f"{key}:", ln=True)
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 7, val)
        pdf.ln(2)

    # Generate bytes
    pdf_bytes = pdf.output()

    artifact_part = Part(
        inline_data=Blob(
            data=pdf_bytes,
            mime_type="application/pdf"
        )
    )
    # Save artifact
    version = await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    return {"status": "success", "filename": filename, "version": version}


create_pdf_file_tool = FunctionTool(func=create_pdf_file)
