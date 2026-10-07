from curses.panel import panel
from pathlib import Path
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from data.users import USERS

Path("documents/certificates").mkdir(parents=True, exist_ok=True)
Path("documents/travel").mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.textColor = colors.HexColor("#D9DEE3")
title_style.alignment = TA_CENTER

heading_style = styles["Heading2"]
heading_style.textColor = colors.HexColor("#1F2933")

body_style = styles["BodyText"]
body_style.textColor = colors.HexColor("#B8C1CA")
body_style.leading = 18

panel_style = styles["BodyText"]
panel_style.textColor = colors.white    
panel_style.leading = 18

meta_style = styles["BodyText"]
meta_style.textColor = colors.HexColor("#697581")
meta_style.leading = 15


def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#E6E8EB"))
    canvas.rect(0, 0, doc.width + doc.leftMargin + doc.rightMargin, doc.height + doc.topMargin + doc.bottomMargin, fill=1, stroke=0)
    canvas.restoreState()


def pdf(path, title, officer, role, authority, lines, document_id, numbered=True, section_title="Qualification Objectives", certification_status="Current", closing_note="This qualification remains valid while operational readiness requirements remain current."):

    doc = SimpleDocTemplate(path, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)

    story = []

    banner = Table([[Paragraph("<b>AEROSPACE DEPLOYMENT COMMAND</b>", title_style)]], colWidths=[170 * mm])

    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#05070A")),
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#252C33")),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10)
    ]))

    story.append(banner)

    story.append(Paragraph(f"<b>{title}</b>", heading_style))

    meta = Table([["Document ID", document_id], ["Classification", "Restricted"], ["Issue Date", "24 Sep 2026"], ["Issuing Authority", authority]], colWidths=[55*mm, 115*mm])

    meta.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#DDE1E6")),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#A0A9B3")),
        ("TEXTCOLOR",(0,0),(-1,-1),colors.HexColor("#2A3138")),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),8)
    ]))

    story.append(meta)

    story.append(Paragraph("<br/>", body_style))

    content = [f"<b>Officer:</b> {officer}", f"<b>Assignment:</b> {role}", ""]

    if certification_status:content.extend([f"<b>Certification Status:</b> {certification_status}"])

    if section_title:content.extend(["", f"<b>{section_title}</b>"])


    if numbered:
        for i, item in enumerate(lines, start=1):
            content.append(f"{i}. {item}")
    else:
        content.extend(lines)

    if closing_note:
        content.extend(["", closing_note])

    panel = Table([[Paragraph("<br/>".join(content), panel_style)]], colWidths=[170 * mm])

    panel.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#05070A")),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#252C33")),
        ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14),
        ("TOPPADDING",(0,0),(-1,-1),14),
        ("BOTTOMPADDING",(0,0),(-1,-1),14)
    ]))
    

    story.append(panel)

    story.append(Paragraph("<br/><font color='#697581'>ADC Information Assurance Standard IA-17</font>", meta_style))

    doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)


COURSES = {
    "airfield_safety": {
        "title": "Airfield Safety Qualification",
        "authority": "ADC Air Operations School",
        "id": "ADC-TRN-26-101",
        "content": [
            "Flight line hazard awareness",
            "Aircraft exclusion zones",
            "Ground movement procedures",
            "Foreign object debris prevention"
        ]
    },
    "emergency_response": {
        "title": "Emergency Response Certification",
        "authority": "ADC Emergency Services Directorate",
        "id": "ADC-TRN-26-102",
        "content": [
            "Aircraft incident response",
            "Emergency communications",
            "Personnel evacuation procedures",
            "Critical casualty coordination"
        ]
    },
    "cbrn_response": {
        "title": "CBRN Response Qualification",
        "authority": "ADC Defence Preparedness Command",
        "id": "ADC-TRN-26-103",
        "content": [
            "Chemical hazard recognition",
            "Protective equipment procedures",
            "Contamination control measures",
            "Operational reporting requirements"
        ]
    },
    "flight_line_ops": {
        "title": "Flight Line Operations Qualification",
        "authority": "ADC Flight Operations Command",
        "id": "ADC-TRN-26-104",
        "content": [
            "Ground support coordination",
            "Aircraft marshalling procedures",
            "Secure communications protocol",
            "Pre-departure readiness verification"
        ]
    }
}


for username, user in USERS.items():

    for filename, course in COURSES.items():

        pdf(
            f"documents/certificates/{username}_{filename}.pdf",
            course["title"],
            user["name"],
            user["role"],
            course["authority"],
            course["content"],
            course["id"]
        )


pdf(
    "documents/travel/sentinel_orders.pdf",
    "ADC Air Mobility Tasking Order",
    "Operation Sentinel Personnel Manifest",
    "Air Mobility Deployment",
    "ADC Air Mobility Command",
    [
        "<b>Operation Overview</b>",
        "",
        "• Operation: Operation Sentinel",
        "• Mission Type: Forward Air Mobility Deployment",
        "• Movement Reference: FL-7800-SNT",
        "• Classification: Restricted",
        "",
        "<b>Flight Details</b>",
        "",
        "• Departure Air Base: Eagle Air Base",
        "• Destination: Forward Operating Airfield Kilo",
        "• Departure Window: 0700–0900 UTC",
        "• Aircraft Allocation: C-130J Hercules",
        "",
        "<b>Personnel Manifest</b>",
        "",
        "• Alex Carter — Flight Readiness Officer",
        "• Riley Hayes — Flight Readiness Officer",
        "• Emma Foster — Flight Readiness Officer",
        "• Lucas Chen — Mission Operations Officer",
        "",
        "<b>Authorization</b>",
        "",
        "• Command Approval: Granted",
        "• Manifest Status: Locked"
    ],
    "ADC-AMTO-26-201", numbered=False, section_title=None, certification_status=None, closing_note=None)