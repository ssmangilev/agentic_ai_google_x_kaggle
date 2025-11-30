import datetime
import uuid
from typing import Dict
from markdown import markdown
from weasyprint import HTML
import os


def render_final_pdf(
        markdown_content: str, charts_map: Dict[str, str]) -> Dict[str, str]:
    """
    Converts markdown + embedded chart placeholders into a real PDF with images.
    Saves the PDF to disk.
    """

    print("--- Starting PDF Rendering Process ---")

    # 1. Replace chart placeholders with HTML <img> tags
    html_content = markdown_content
    for placeholder, path in charts_map.items():
        if os.path.exists(path):
            html_tag = f'<img src="{path}" style="width:100%; margin:20px 0;" />' # NOQA
        else:
            html_tag = f'<p><b>Missing chart:</b> {placeholder}</p>'
        html_content = html_content.replace(f"[{placeholder}]", html_tag)

    # 2. Convert final Markdown → HTML
    html_content = markdown(html_content, output_format="html5")

    # 3. Generate filename
    first_line = markdown_content.split("\n")[0]
    title = first_line.strip("# ").replace(":", "")
    title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).replace(
        " ", "_")
    if not title:
        title = "BI_Report"

    date = datetime.date.today().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8]

    file_name = f"{title}_{date}_{uid}.pdf"
    file_path = f"/reports/final/{file_name}"

    # Ensure directory exists
    os.makedirs("/reports/final", exist_ok=True)

    # 4. Generate PDF from HTML, write to disk
    HTML(string=html_content).write_pdf(file_path)

    print(f"File successfully created: {file_path}")
    print("--- PDF Rendering Complete ---")

    return {
        "status": "success",
        "message": "PDF report generated successfully and ready for user download.", # NOQA
        "file_path": file_path
    }
