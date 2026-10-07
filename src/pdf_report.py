
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def export_audit_pdf(result, path):
    path=Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    styles=getSampleStyleSheet()
    title=ParagraphStyle("TitleX",parent=styles["Title"],fontSize=16,leading=19,spaceAfter=8)
    h2=ParagraphStyle("H2X",parent=styles["Heading2"],fontSize=11,leading=13,spaceBefore=7,spaceAfter=5)
    body=ParagraphStyle("BodyX",parent=styles["BodyText"],fontSize=8.5,leading=11)
    small=ParagraphStyle("SmallX",parent=styles["BodyText"],fontSize=7,leading=9)

    doc=SimpleDocTemplate(str(path),pagesize=letter,
                          leftMargin=.45*inch,rightMargin=.45*inch,
                          topMargin=.45*inch,bottomMargin=.45*inch)
    story=[
        Paragraph("AwanSolveAi",title),
        Paragraph("Heavy-Equipment Warranty Claim Evidence Audit Report",h2),
        Paragraph(f"Profile: {result.profile}",body),
        Paragraph(f"Overall status: {result.overall_status}",body),
        Spacer(1,8),
    ]

    summary=[
        ["Metric","Value"],
        ["Documents",str(len(result.claim.files))],
        ["Checks",str(len(result.rules))],
        ["Passed",str(sum(r.status=="PASS" for r in result.rules))],
        ["Issues",str(sum(r.status!="PASS" for r in result.rules))],
    ]
    t=Table(summary,colWidths=[2.0*inch,4.8*inch])
    t.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.35,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    story += [t,Spacer(1,10),Paragraph("Audit checks",h2)]

    rows=[["Rule","Status","Check","Reason","Source / Page"]]
    for r in result.rules:
        rows.append([
            r.rule_id,
            r.status,
            Paragraph(r.name,small),
            Paragraph(r.reason,small),
            Paragraph("; ".join(r.citations),small)
        ])
    table=Table(rows,colWidths=[.48*inch,1.05*inch,1.45*inch,2.65*inch,1.55*inch],repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),7),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3),
        ("RIGHTPADDING",(0,0),(-1,-1),3),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story += [table,Spacer(1,12),
              Paragraph("Documentation pre-audit only. This report evaluates the completeness and internal consistency of supplied evidence. It does not approve warranty coverage, determine OEM liability, authorize repairs, or replace manufacturer warranty policy or warranty-administrator review.",small)]
    doc.build(story)
    return path
