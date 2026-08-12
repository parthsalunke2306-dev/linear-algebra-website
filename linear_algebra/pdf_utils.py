import io
import base64
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse
from xhtml2pdf import pisa

def latex_matrix_to_html(latex_str):
    r"""
    Parses LaTeX matrix strings (bmatrix, matrix, array) into clean, styled HTML tables for PDF generation.
    Handles augmented matrices with '|' or '\mid'.
    """

    if not latex_str or not isinstance(latex_str, str):
        return str(latex_str or '')

    clean_str = latex_str.strip()
    if clean_str.startswith("$$") and clean_str.endswith("$$"):
        clean_str = clean_str[2:-2].strip()

    # Match \begin{bmatrix}... \end{bmatrix}, \begin{matrix}...\end{matrix}, or \begin{array}{...}...\end{array}
    matrix_match = re.search(r'\\begin\{(?:bmatrix|matrix|array)\}(?:\{.*?\})?(.*?)\\end\{(?:bmatrix|matrix|array)\}', clean_str, re.DOTALL)
    if not matrix_match:
        return None

    content = matrix_match.group(1).strip()
    rows = [r.strip() for r in content.split(r'\\') if r.strip()]
    
    table_rows = []
    for row in rows:
        cells = [c.strip() for c in row.split('&')]
        td_htmls = []
        for c in cells:
            if c == '|' or c == r'\mid':
                td_htmls.append('<td style="border-right: 1.5px solid #475569; padding: 0 4px;"></td>')
            else:
                td_htmls.append(f'<td style="padding: 5px 12px; text-align: center; font-weight: bold; font-family: monospace; font-size: 13px; color: #0f172a;">{c}</td>')
        table_rows.append(f'<tr>{"".join(td_htmls)}</tr>')

    html_table = f'''
    <table style="display: inline-table; vertical-align: middle; border-left: 2.5px solid #1e293b; border-right: 2.5px solid #1e293b; border-collapse: collapse; margin: 6px auto; background-color: #f8fafc; border-radius: 4px;">
        {"".join(table_rows)}
    </table>
    '''
    return html_table

def render_latex_to_base64_png(latex_str, fontsize=13, color='#0f172a', dpi=200):
    """
    Converts a LaTeX math string into a Base64-encoded PNG Data URI.
    Uses Matplotlib's pure-Python mathtext engine (serverless safe).
    """
    if not latex_str or not str(latex_str).strip():
        return ""

    clean_latex = str(latex_str).strip()
    if clean_latex.startswith("$$") and clean_latex.endswith("$$"):
        clean_latex = clean_latex[2:-2].strip()
    elif clean_latex.startswith("$") and clean_latex.endswith("$"):
        clean_latex = clean_latex[1:-1].strip()

    # Clean up matrix tags if any slipped through
    clean_latex = re.sub(r'\\left\[|\\right\]', '', clean_latex)
    clean_latex = re.sub(r'\\begin\{(?:bmatrix|matrix|array)\}(?:\{.*?\})?', '', clean_latex)
    clean_latex = re.sub(r'\\end\{(?:bmatrix|matrix|array)\}', '', clean_latex)

    formatted_latex = f"${clean_latex}$"

    try:
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0.0)
        
        plt.text(
            0.5, 0.5, formatted_latex,
            fontsize=fontsize,
            color=color,
            ha='center',
            va='center'
        )
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.06, transparent=True, dpi=dpi)
        plt.close(fig)
        
        buf.seek(0)
        b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{b64_str}"
    except Exception as e:
        print(f"[Matplotlib LaTeX render note]: {e}")
        return ""

def prepare_latex_for_pdf(latex_str, default_color='#0f172a'):
    """
    Intelligently converts a LaTeX string into an HTML table (if matrix)
    or a Base64 PNG image tag (if equation).
    """
    if not latex_str:
        return ""

    # 1. Try HTML matrix table conversion first
    html_matrix = latex_matrix_to_html(latex_str)
    if html_matrix:
        return html_matrix

    # 2. Convert to Base64 PNG Image
    b64_img = render_latex_to_base64_png(latex_str, color=default_color)
    if b64_img:
        return f'<img src="{b64_img}" style="vertical-align: middle; max-height: 48px;" />'
    
    # Fallback to plain text if rendering failed
    return f'<span style="font-family: monospace;">{latex_str}</span>'

def generate_pdf_response(rendered_html, filename="Linear_Algebra_Solution.pdf"):
    """
    Converts HTML into a downloadable PDF response using xhtml2pdf.
    """
    pdf_out = io.BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_out)
    
    if pisa_status.err:
        return HttpResponse(f"Error generating PDF document: {pisa_status.err}", status=500)
    
    pdf_out.seek(0)
    response = HttpResponse(pdf_out.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
