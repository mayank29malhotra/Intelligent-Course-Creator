"""
Markdown to PDF Exporter

Converts Markdown content to professional PDF documents using xhtml2pdf.
This properly handles markdown formatting (**bold**, *italic*, `code`, etc.)
"""

from pathlib import Path
import markdown2
from xhtml2pdf import pisa
from bs4 import BeautifulSoup


def export_markdown_to_pdf(markdown_content: str, output_path: str, add_page_numbers: bool = True) -> bool:
    """
    Export Markdown content to a professionally formatted PDF.
    Uses markdown2 + xhtml2pdf for proper markdown symbol handling.
    
    Args:
        markdown_content: Raw Markdown text
        output_path: Path to save the PDF
        add_page_numbers: Whether to add page numbers (legacy param, ignored)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔄 Converting Markdown to HTML...")
        
        # Convert Markdown to HTML with all formatting extras
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                'fenced-code-blocks',
                'tables',
                'code-friendly',
                'cuddled-lists',
                'header-ids',
                'strike',
                'task_list',
                'break-on-newline'
            ]
        )

        # Post-process HTML to normalize layout for PDF
        html_content = _normalize_html_for_pdf(html_content)
        
        # Professional CSS styling (optimized for xhtml2pdf with better spacing and wrapping)
        css_style = """
        <style>
            @page {
                size: letter;
                margin: 0.75in;
            }
            
            body {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #333;
                word-wrap: break-word;
            }
            
            h1 {
                font-size: 20pt;
                color: #1a1a1a;
                margin-top: 12pt;
                margin-bottom: 10pt;
                font-weight: bold;
                page-break-after: avoid;
            }
            
            h2 {
                font-size: 16pt;
                color: #2c3e50;
                margin-top: 10pt;
                margin-bottom: 8pt;
                font-weight: bold;
                border-bottom: 2px solid #3498db;
                padding-bottom: 3pt;
                page-break-after: avoid;
            }
            
            h3 {
                font-size: 13pt;
                color: #34495e;
                margin-top: 8pt;
                margin-bottom: 6pt;
                font-weight: bold;
                page-break-after: avoid;
            }
            
            h4 {
                font-size: 11pt;
                color: #555;
                margin-top: 6pt;
                margin-bottom: 4pt;
                font-weight: bold;
                page-break-after: avoid;
            }
            
            p {
                margin-top: 0;
                margin-bottom: 6pt;
                text-align: left;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            
            ul, ol {
                margin-left: 15pt;
                margin-bottom: 6pt;
                margin-top: 3pt;
                padding-left: 10pt;
            }
            
            li {
                margin-bottom: 3pt;
                word-wrap: break-word;
            }
            
            code {
                font-family: 'Courier New', Courier, monospace;
                font-size: 8.5pt;
                background-color: #f4f4f4;
                padding: 1pt 3pt;
                color: #c7254e;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            
            pre {
                background-color: #f4f4f4;
                border: 1px solid #ddd;
                padding: 8pt;
                margin-bottom: 8pt;
                margin-top: 4pt;
                font-family: 'Courier New', Courier, monospace;
                font-size: 8pt;
                overflow: hidden;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                color: #333;
                font-size: 8pt;
            }
            
            blockquote {
                border-left: 3pt solid #ddd;
                padding-left: 10pt;
                margin-left: 5pt;
                margin-bottom: 8pt;
                margin-top: 4pt;
                color: #666;
                font-style: italic;
                background-color: #fafafa;
                padding: 8pt;
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 10pt;
                margin-top: 6pt;
                font-size: 9pt;
                table-layout: fixed;
            }
            
            th, td {
                border: 1px solid #ccc;
                padding: 4pt 6pt;
                text-align: left;
                vertical-align: top;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            
            th {
                background-color: #f0f0f0;
                font-weight: bold;
                font-size: 9pt;
            }
            
            td {
                font-size: 9pt;
            }
            
            strong {
                font-weight: bold;
                color: #000;
            }
            
            em {
                font-style: italic;
            }
            
            a {
                color: #0366d6;
                text-decoration: none;
                word-wrap: break-word;
            }
            
            hr {
                border: none;
                border-top: 1px solid #ccc;
                margin: 12pt 0;
            }
        </style>
        """
        
        # Create complete HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {css_style}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        print(f"📄 Generating PDF...")
        
        # Generate PDF using xhtml2pdf
        with open(output_path, "w+b") as output_file:
            pisa_status = pisa.CreatePDF(
                full_html,
                dest=output_file,
                encoding='utf-8'
            )
        
        if pisa_status.err:
            print(f"⚠️  PDF generated with {pisa_status.err} errors")
            return False
        
        print(f"✅ PDF successfully created: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PDF: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def _normalize_html_for_pdf(html: str) -> str:
    """Normalize markdown2 HTML output for more consistent PDF layout.

    - Converts large "markdown fenced as markdown" blocks back to normal text
    - Strips most syntax-highlighting span classes
    - Collapses excessive <br> tags
    """

    try:
        soup = BeautifulSoup(html, "html.parser")

        # 1) Simplify syntax-highlighting spans (keep text, drop classes)
        for span in soup.find_all("span"):
            if span.get("class"):
                # Replace span with its text content
                span.unwrap()

        # 2) Detect <pre><code> blocks that actually contain markdown text
        #    (start with headings or bullet markers) and convert to paragraphs
        for pre in soup.find_all("pre"):
            code = pre.code
            if not code:
                continue

            raw = code.get_text("\n")
            first_line = raw.lstrip().splitlines()[0] if raw.strip() else ""

            looks_like_markdown = (
                first_line.startswith("# ")
                or first_line.startswith("## ")
                or first_line.startswith("### ")
                or first_line.startswith("* ")
                or first_line.startswith("- ")
                or first_line.startswith("1. ")
            )

            if not looks_like_markdown:
                continue

            # Re-run markdown2 on this inner markdown to get proper structure
            inner_html = markdown2.markdown(raw)
            inner_soup = BeautifulSoup(inner_html, "html.parser")

            # Replace <pre> with its converted children
            new_nodes = list(inner_soup.body.children) if inner_soup.body else inner_soup.contents
            for new_node in new_nodes[::-1]:
                pre.insert_after(new_node)
            pre.decompose()

        # 3) Collapse multiple consecutive <br> tags into at most two
        for br in soup.find_all("br"):
            # If previous sibling is also <br>, remove this one
            prev = br.previous_sibling
            if prev and getattr(prev, "name", None) == "br":
                br.decompose()

        return str(soup)
    except Exception:
        # On any failure, fall back to original HTML
        return html


# Legacy function for backward compatibility (deprecated)
def export_course_to_pdf(course, output_path: str):
    """
    Legacy function - exports CourseCompletion object to PDF.
    Now uses full_markdown_content if available.
    
    Args:
        course: CourseCompletion object or dict
        output_path: Path to save PDF
    """
    # Try to get markdown content
    if hasattr(course, 'full_markdown_content'):
        markdown_content = course.full_markdown_content
    elif isinstance(course, dict) and 'full_markdown_content' in course:
        markdown_content = course['full_markdown_content']
    else:
        # Fallback: create basic markdown from course structure
        markdown_content = f"# {getattr(course, 'course_title', 'Course')}\n\nCourse content not available in Markdown format."
    
    return export_markdown_to_pdf(markdown_content, output_path)

