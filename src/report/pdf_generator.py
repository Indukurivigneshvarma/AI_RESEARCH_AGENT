from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


def generate_pdf(report_text: str, output_path: str = "report.pdf") -> str:
    """
    PDF GENERATION MODULE
    =====================

    Purpose
    -------
    Converts the structured report text (produced by the LLM writer)
    into a formatted PDF document using ReportLab.

    The report text follows a strict marker-based structure:
        @@TITLE@@
        Title Text
        @@TITLE@@

        @@Section Name@@
        Paragraph text...

    This function interprets those markers and applies
    appropriate visual styles.

    Inputs
    ------
    report_text : str
        Fully formatted report text with structural markers.

    output_path : str
        Output file path for the generated PDF.

    Returns
    -------
    str : Path to the generated PDF file.
    """

    # --------------------------------------------------
    # Style Definitions
    # --------------------------------------------------
    # These styles control typography and layout of the report.

    styles = getSampleStyleSheet()

    # Title style (centered, large, bold)
    styles.add(ParagraphStyle(
        name="TitleStyle",
        fontSize=18,
        leading=22,
        spaceBefore=24,
        spaceAfter=24,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    ))

    # Section heading style
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13,
        leading=16,
        spaceBefore=18,
        spaceAfter=12,
        fontName="Helvetica-Bold",
    ))

    # Body paragraph style
    styles.add(ParagraphStyle(
        name="ReportBody",
        fontSize=11,
        leading=15,
        spaceBefore=6,
        spaceAfter=6,
    ))

    # --------------------------------------------------
    # Document Setup
    # --------------------------------------------------
    # Defines page size and margins.

    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    story = []  # Holds the flowable elements (paragraphs, spacers)

    lines = report_text.splitlines()
    i = 0

    # --------------------------------------------------
    # Parse Structured Report Text
    # --------------------------------------------------
    # The loop walks line-by-line and interprets markers.

    while i < len(lines):
        line = lines[i].strip()

        # Blank line → vertical spacing
        if not line:
            story.append(Spacer(1, 12))
            i += 1
            continue

        # Title block handling
        if line == "@@TITLE@@":
            title_text = lines[i + 1].strip()
            story.append(Paragraph(title_text, styles["TitleStyle"]))
            story.append(Spacer(1, 24))
            i += 3  # Skip closing @@TITLE@@
            continue

        # Section header handling
        if line.startswith("@@") and line.endswith("@@"):
            heading = line.strip("@")
            story.append(Paragraph(heading, styles["SectionHeader"]))
            story.append(Spacer(1, 12))
            i += 1
            continue

        # Normal paragraph text
        story.append(Paragraph(line, styles["ReportBody"]))
        i += 1

    # --------------------------------------------------
    # Build PDF
    # --------------------------------------------------
    doc.build(story)

    return output_path
