from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

CORRECTED = [
    ("A", "South Africa", "Czechia", "Jun 25 18:00", "Jun 12 18:00"),
    ("A", "Mexico", "South Africa", "Jun 12 18:00", "Jun 17 15:00"),
    ("A", "South Korea", "Czechia", "Jun 25 15:00", "Jun 17 18:00"),
    ("A", "Mexico", "Czechia", "Jun 17 15:00", "Jun 25 15:00"),
    ("A", "South Korea", "South Africa", "Jun 17 18:00", "Jun 25 18:00"),
    ("B", "Qatar", "Bosnia & Herzegovina", "Jun 26 18:00", "Jun 13 18:00"),
    ("B", "Canada", "Qatar", "Jun 13 18:00", "Jun 18 15:00"),
    ("B", "Switzerland", "Bosnia & Herzegovina", "Jun 26 15:00", "Jun 18 18:00"),
    ("B", "Canada", "Bosnia & Herzegovina", "Jun 18 15:00", "Jun 26 15:00"),
    ("B", "Switzerland", "Qatar", "Jun 18 18:00", "Jun 26 18:00"),
    ("C", "Scotland", "Haiti", "Jun 27 18:00", "Jun 14 18:00"),
    ("C", "Brazil", "Scotland", "Jun 14 18:00", "Jun 19 15:00"),
    ("C", "Morocco", "Haiti", "Jun 27 15:00", "Jun 19 18:00"),
    ("C", "Brazil", "Haiti", "Jun 19 15:00", "Jun 27 15:00"),
    ("C", "Morocco", "Scotland", "Jun 19 18:00", "Jun 27 18:00"),
    ("D", "Australia", "Turkiye", "Jun 25 18:00", "Jun 12 18:00"),
    ("D", "USA", "Australia", "Jun 12 18:00", "Jun 17 15:00"),
    ("D", "Paraguay", "Turkiye", "Jun 25 15:00", "Jun 17 18:00"),
    ("D", "USA", "Turkiye", "Jun 17 15:00", "Jun 25 15:00"),
    ("D", "Paraguay", "Australia", "Jun 17 18:00", "Jun 25 18:00"),
    ("E", "Cote d'Ivoire", "Curacao", "Jun 26 18:00", "Jun 13 18:00"),
    ("E", "Germany", "Cote d'Ivoire", "Jun 13 18:00", "Jun 18 15:00"),
    ("E", "Ecuador", "Curacao", "Jun 26 15:00", "Jun 18 18:00"),
    ("E", "Germany", "Curacao", "Jun 18 15:00", "Jun 26 15:00"),
    ("E", "Ecuador", "Cote d'Ivoire", "Jun 18 18:00", "Jun 26 18:00"),
    ("F", "Tunisia", "Sweden", "Jun 27 18:00", "Jun 14 18:00"),
    ("F", "Netherlands", "Tunisia", "Jun 14 18:00", "Jun 19 15:00"),
    ("F", "Japan", "Sweden", "Jun 27 15:00", "Jun 19 18:00"),
    ("F", "Netherlands", "Sweden", "Jun 19 15:00", "Jun 27 15:00"),
    ("F", "Japan", "Tunisia", "Jun 19 18:00", "Jun 27 18:00"),
    ("G", "Egypt", "New Zealand", "Jun 25 18:00", "Jun 12 18:00"),
    ("G", "Belgium", "Egypt", "Jun 12 18:00", "Jun 17 15:00"),
    ("G", "Iran", "New Zealand", "Jun 25 15:00", "Jun 17 18:00"),
    ("G", "Belgium", "New Zealand", "Jun 17 15:00", "Jun 25 15:00"),
    ("G", "Iran", "Egypt", "Jun 17 18:00", "Jun 25 18:00"),
    ("H", "Saudi Arabia", "Cape Verde", "Jun 26 18:00", "Jun 13 18:00"),
    ("H", "Spain", "Saudi Arabia", "Jun 13 18:00", "Jun 18 15:00"),
    ("H", "Uruguay", "Cape Verde", "Jun 26 15:00", "Jun 18 18:00"),
    ("H", "Spain", "Cape Verde", "Jun 18 15:00", "Jun 26 15:00"),
    ("H", "Uruguay", "Saudi Arabia", "Jun 18 18:00", "Jun 26 18:00"),
    ("I", "Norway", "Iraq", "Jun 27 18:00", "Jun 14 18:00"),
    ("I", "France", "Norway", "Jun 14 18:00", "Jun 19 15:00"),
    ("I", "Senegal", "Iraq", "Jun 27 15:00", "Jun 19 18:00"),
    ("I", "France", "Iraq", "Jun 19 15:00", "Jun 27 15:00"),
    ("I", "Senegal", "Norway", "Jun 19 18:00", "Jun 27 18:00"),
    ("J", "Algeria", "Jordan", "Jun 25 18:00", "Jun 12 18:00"),
    ("J", "Argentina", "Algeria", "Jun 12 18:00", "Jun 17 15:00"),
    ("J", "Austria", "Jordan", "Jun 25 15:00", "Jun 17 18:00"),
    ("J", "Argentina", "Jordan", "Jun 17 15:00", "Jun 25 15:00"),
    ("J", "Austria", "Algeria", "Jun 17 18:00", "Jun 25 18:00"),
    ("K", "Uzbekistan", "DR Congo", "Jun 26 18:00", "Jun 13 18:00"),
    ("K", "Portugal", "Uzbekistan", "Jun 13 18:00", "Jun 18 15:00"),
    ("K", "Colombia", "DR Congo", "Jun 26 15:00", "Jun 18 18:00"),
    ("K", "Portugal", "DR Congo", "Jun 18 15:00", "Jun 26 15:00"),
    ("K", "Colombia", "Uzbekistan", "Jun 18 18:00", "Jun 26 18:00"),
    ("L", "Panama", "Ghana", "Jun 27 18:00", "Jun 14 18:00"),
    ("L", "England", "Panama", "Jun 14 18:00", "Jun 19 15:00"),
    ("L", "Croatia", "Ghana", "Jun 27 15:00", "Jun 19 18:00"),
    ("L", "England", "Ghana", "Jun 19 15:00", "Jun 27 15:00"),
    ("L", "Croatia", "Panama", "Jun 19 18:00", "Jun 27 18:00"),
]

GROUP_COLORS = {
    "A": colors.HexColor("#FFF3CD"),
    "B": colors.HexColor("#D1ECF1"),
    "C": colors.HexColor("#D4EDDA"),
    "D": colors.HexColor("#F8D7DA"),
    "E": colors.HexColor("#E2D9F3"),
    "F": colors.HexColor("#FDEBD0"),
    "G": colors.HexColor("#D6EAF8"),
    "H": colors.HexColor("#FDEDEC"),
    "I": colors.HexColor("#E8F8F5"),
    "J": colors.HexColor("#FEF9E7"),
    "K": colors.HexColor("#F9EBEA"),
    "L": colors.HexColor("#EBF5FB"),
}

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "title", parent=styles["Title"], fontSize=16, spaceAfter=6
)
sub_style = ParagraphStyle(
    "sub",
    parent=styles["Normal"],
    fontSize=9,
    textColor=colors.HexColor("#555555"),
    spaceAfter=14,
    alignment=TA_CENTER,
)

doc = SimpleDocTemplate(
    "corrected_match_dates.pdf",
    pagesize=A4,
    leftMargin=1.5 * cm,
    rightMargin=1.5 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)

header = ["Group", "Home", "Away", "Old Date", "New Date"]
table_data = [header] + [list(r) for r in CORRECTED]
col_widths = [1.4 * cm, 4.8 * cm, 4.8 * cm, 3.5 * cm, 3.5 * cm]

style_cmds = [
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#212529")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 1), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
    ("ROWHEIGHT", (0, 0), (-1, -1), 18),
    ("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor("#CC0000")),
    ("TEXTCOLOR", (4, 1), (4, -1), colors.HexColor("#006600")),
]

for i, row in enumerate(CORRECTED, start=1):
    bg = GROUP_COLORS.get(row[0], colors.white)
    style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

t = Table(table_data, colWidths=col_widths, repeatRows=1)
t.setStyle(TableStyle(style_cmds))

story = [
    Paragraph("Corrected Match Dates — FIFA World Cup 2026", title_style),
    Paragraph(
        "60 group-stage matches had wrong dates due to a scheduling bug. "
        "Old date in red, corrected date in green.",
        sub_style,
    ),
    t,
]
doc.build(story)
print("PDF saved: corrected_match_dates.pdf")
