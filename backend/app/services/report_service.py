from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

# Colour palette matching the dark luxury theme (for PDF)
GOLD   = colors.HexColor("#D4AF37")
DARK   = colors.HexColor("#0A0A1E")
DARK2  = colors.HexColor("#181835")
TEAL   = colors.HexColor("#00C2CB")
GREEN  = colors.HexColor("#5DBB63")
MUTED  = colors.HexColor("#7A7A9A")
WHITE  = colors.white

def generate_project_pdf(project: dict, validations: list,
                          selected_layout: dict, layout_image_path: str | None) -> bytes:
    """
    Generate the final approval PDF report using ReportLab.
    Returns raw bytes ready to be uploaded to MinIO.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle("title",  fontSize=22, textColor=GOLD,
                                   fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)
    h2_style     = ParagraphStyle("h2",     fontSize=14, textColor=GOLD,
                                   fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body_style   = ParagraphStyle("body",   fontSize=10, textColor=colors.black,
                                   fontName="Helvetica", spaceAfter=4, leading=15)
    muted_style  = ParagraphStyle("muted",  fontSize=9,  textColor=MUTED,
                                   fontName="Helvetica", spaceAfter=4)
    center_style = ParagraphStyle("center", fontSize=10, alignment=TA_CENTER,
                                   fontName="Helvetica")

    def hr():
        return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=8, spaceBefore=8)

    def section(title):
        return [Spacer(1, 8), Paragraph(title, h2_style), hr()]

    story = []

    # ── Cover ──
    story += [
        Spacer(1, 1.5*cm),
        Paragraph("🏙️  URBAN PLANNER", title_style),
        Paragraph("AI-Powered Land Planning Report", ParagraphStyle(
            "sub", fontSize=13, textColor=TEAL, fontName="Helvetica",
            alignment=TA_CENTER, spaceAfter=4)),
        Paragraph(f"SDG 11 – Sustainable Cities & Communities",
                  ParagraphStyle("sdg", fontSize=9, textColor=MUTED,
                                  alignment=TA_CENTER, fontName="Helvetica", spaceAfter=20)),
        hr(),
        Paragraph(f"Project: <b>{project.get('name','—')}</b>", body_style),
        Paragraph(f"Prepared for: {project.get('owner_name','—')}", body_style),
        Paragraph(f"City: {project.get('city','—')} | State: {project.get('state','—')}", body_style),
        Paragraph(f"Date Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p IST')}", muted_style),
        Spacer(1, 1*cm),
    ]

    # ── Section 1: Project Details ──
    story += section("1.  Project Details")
    details = [
        ["Field", "Value"],
        ["Project Name",  project.get("name","—")],
        ["Use Type",      project.get("use_type","—").replace("_"," ").title()],
        ["Status",        project.get("status","—").replace("_"," ").upper()],
        ["City",          project.get("city","—")],
        ["State",         project.get("state","—")],
    ]
    t = Table(details, colWidths=[6*cm, 11*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), DARK2),
        ("TEXTCOLOR",   (0,0), (-1,0), GOLD),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F8FC")]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("PADDING",     (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    # ── Section 2: Land Analysis ──
    story += section("2.  Land Analysis (Sentinel-2 Satellite Data)")
    li = project.get("land_info", {}) or {}
    land_data = [
        ["Parameter",          "Value"],
        ["Area",               f"{li.get('area_sqm',0):.0f} m²"],
        ["NDVI Score",         f"{li.get('ndvi',0):.3f}"],
        ["NDBI Score",         f"{li.get('ndbi',0):.3f}"],
        ["Elevation",          f"{li.get('elevation_m',0):.0f} m"],
        ["Slope",              f"{li.get('slope_deg',0):.1f}°"],
        ["Groundwater Depth",  f"{li.get('groundwater_depth',0):.1f} m"],
        ["Flood Risk",         "Yes ⚠" if li.get("flood_risk") else "No ✓"],
        ["Heritage Zone",      "Yes ⚠" if li.get("is_heritage") else "No ✓"],
        ["Centroid",           li.get("centroid","—")],
    ]
    t2 = Table(land_data, colWidths=[6*cm, 11*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), DARK2),
        ("TEXTCOLOR",   (0,0), (-1,0), GOLD),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F8FC")]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("PADDING",     (0,0), (-1,-1), 6),
    ]))
    story.append(t2)

    # ── Section 3: Selected Layout ──
    if selected_layout:
        story += section("3.  AI-Selected Land Layout")
        sl = selected_layout
        layout_data = [
            ["Parameter",       "Value"],
            ["Strategy",        sl.get("strategy","—").replace("_"," ").title()],
            ["Feasibility Score",    f"{sl.get('feasibility',0)*100:.1f}%"],
            ["NBC Compliance",       f"{sl.get('nbc_compliance',0)*100:.1f}%"],
            ["Combined Score",       f"{sl.get('combined_score',0)*100:.1f}%"],
        ]
        t3 = Table(layout_data, colWidths=[6*cm, 11*cm])
        t3.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), DARK2),
            ("TEXTCOLOR",   (0,0), (-1,0), GOLD),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F8FC")]),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
            ("PADDING",     (0,0), (-1,-1), 6),
        ]))
        story.append(t3)
        story.append(Spacer(1, 0.5*cm))

        if layout_image_path:
            try:
                img = Image(layout_image_path, width=16*cm, height=10*cm,
                            kind="proportional")
                story.append(img)
            except Exception:
                story.append(Paragraph("[Layout image unavailable]", muted_style))

    # ── Section 4: Validation Timeline ──
    story += section("4.  HITL Validation Summary")
    STAGE_LABELS = {
        1: "Land & Input Verification",
        2: "Construction Feasibility Review",
        3: "Final Expert Sign-off",
    }
    for vd in validations:
        stage  = vd.get("stage")
        dec    = vd.get("decision","pending")
        vname  = vd.get("validator_name","—")
        fb     = vd.get("feedback","")
        ts     = vd.get("created_at","")
        dec_color = GREEN if dec == "approved" else colors.HexColor("#E05C5C")
        story.append(Paragraph(
            f"<b>Stage {stage}: {STAGE_LABELS.get(stage,'—')}</b>", body_style))
        story.append(Paragraph(
            f"Validator: {vname} | Decision: <font color='#{dec_color.hexval()}'>"
            f"{dec.upper()}</font> | {ts}", muted_style))
        if fb:
            story.append(Paragraph(f"Feedback: {fb}", muted_style))
        story.append(Spacer(1, 6))

    # ── Section 5: NBC Compliance Checklist ──
    story += section("5.  NBC 2016 Compliance Checklist")
    nbc_items = [
        ("Minimum setback from road boundary", "✓"),
        ("FAR within permissible limits",       "✓"),
        ("Mandatory green space (min 15%)",     "✓"),
        ("Parking provision as per use type",   "✓"),
        ("Fire access lane (min 6m width)",     "✓"),
        ("Rainwater harvesting provision",      "✓"),
        ("Accessibility (ramp/lift) provision", "✓"),
    ]
    nbc_data = [["NBC Requirement", "Status"]] + [[n, s] for n, s in nbc_items]
    t4 = Table(nbc_data, colWidths=[13*cm, 4*cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), DARK2),
        ("TEXTCOLOR",   (0,0), (-1,0), GOLD),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (1,1), (1,-1), "CENTER"),
        ("TEXTCOLOR",   (1,1), (1,-1), GREEN),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F8FC")]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("PADDING",     (0,0), (-1,-1), 6),
    ]))
    story.append(t4)

    # ── Footer: Validator Signatures ──
    story += [Spacer(1, 1*cm), hr()]
    story.append(Paragraph("Approved & Validated By:", ParagraphStyle(
        "sig_hdr", fontSize=10, fontName="Helvetica-Bold", textColor=DARK, spaceAfter=8)))
    sigs = [[
        f"Validator {v.get('stage',i+1)}\n{v.get('validator_name','—')}\n"
        f"{v.get('role','—').replace('_',' ').title()}"
        for i, v in enumerate(validations)
    ]]
    sig_table = Table(sigs, colWidths=[5.5*cm]*3)
    sig_table.setStyle(TableStyle([
        ("ALIGN",    (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR",(0,0), (-1,-1), DARK),
        ("GRID",     (0,0), (-1,-1), 0.3, GOLD),
        ("PADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "This report was generated by the Urban Planner AI Platform | "
        "SDG 11 – Sustainable Cities & Communities | "
        f"Generated: {datetime.now().strftime('%d %B %Y')}",
        ParagraphStyle("footer", fontSize=7, textColor=MUTED, alignment=TA_CENTER)))

    doc.build(story)
    return buf.getvalue()
