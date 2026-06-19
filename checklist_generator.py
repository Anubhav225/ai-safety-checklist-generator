"""checklist_generator.py — Checklist management and multi-format export."""

import io, json, logging
from datetime import datetime
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)

CATEGORY_ICONS = {
    "Design Safety": "📐", "Operational Safety": "⚙️", "Electrical Safety": "⚡",
    "Mechanical Safety": "🔩", "Software Safety": "💻", "Human Factors": "👷",
    "Environmental Safety": "🌿", "Maintenance Safety": "🔧", "General Safety": "🛡️",
}
PRIORITY_COLORS = {"Critical":"#dc2626","High":"#f97316","Medium":"#f59e0b","Low":"#16a34a"}


class ChecklistGenerator:
    def organize_by_category(self, items: list) -> dict:
        out = {}
        for item in items:
            c = item.get("category","General Safety")
            out.setdefault(c, []).append(item)
        return out

    def get_category_stats(self, items: list) -> dict:
        org = self.organize_by_category(items)
        return {
            cat: {
                "total": len(its),
                "critical": sum(1 for i in its if i.get("priority")=="Critical"),
                "high":     sum(1 for i in its if i.get("priority")=="High"),
                "completed":sum(1 for i in its if i.get("status")=="Completed"),
                "expert":   sum(1 for i in its if i.get("requires_expert_review")),
                "icon":     CATEGORY_ICONS.get(cat,"🛡️"),
            }
            for cat, its in org.items()
        }

    # ── Markdown ───────────────────────────────────────────────────────────────
    def export_to_markdown(self, analysis: dict, project_name: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# Safety Analysis Report — {project_name}",
            f"**Generated:** {now}  |  **Overall Risk:** {analysis.get('overall_risk_assessment','N/A')}  |  **Safety Score:** {analysis.get('safety_readiness_score','N/A')}/100",
            "",
            "> ⚠️ **DISCLAIMER:** AI-generated guidance only. Not a substitute for certified professional engineering review.",
            "", "---", "",
            "## Executive Summary",
            analysis.get("summary","No summary available."),
            "", "---", "", "## Identified Hazards", "",
            "| ID | Category | Description | Likelihood | Severity | Score |",
            "|----|----------|-------------|------------|----------|-------|",
        ]
        for h in analysis.get("identified_hazards",[]):
            lines.append(f"| {h.get('hazard_id','')} | {h.get('category','')} | {h.get('description','')[:60]} | {h.get('likelihood','')} | {h.get('severity','')} | {h.get('risk_score','')} |")

        lines += ["", "---", "", "## Safety Checklist", ""]
        for cat, items in self.organize_by_category(analysis.get("safety_checklist",[])).items():
            lines.append(f"### {CATEGORY_ICONS.get(cat,'🛡️')} {cat}")
            for item in items:
                ex = " ⚠️ *Expert review required*" if item.get("requires_expert_review") else ""
                lines.append(f"- **[{item.get('priority','Med')}]** {item.get('item','')}{ex}")
                if item.get("description"): lines.append(f"  > {item['description']}")
            lines.append("")

        lines += ["---", "", "## Applicable Standards", ""]
        for s in analysis.get("applicable_standards",[]):
            lines.append(f"### {s.get('standard_id','')} — {s.get('name','')}")
            lines.append(f"**Org:** {s.get('organization','')} | **Relevance:** {s.get('relevance','')}")
            lines.append("")
        lines += ["---", f"*{analysis.get('disclaimer','')}*"]
        return "\n".join(lines)

    def export_to_json(self, analysis: dict) -> str:
        return json.dumps(analysis, indent=2, default=str)

    def export_checklist_csv(self, items: list) -> bytes:
        rows = [{
            "ID": i.get("id",""), "Category": i.get("category",""),
            "Item": i.get("item",""), "Description": i.get("description",""),
            "Priority": i.get("priority",""), "Status": i.get("status","Pending"),
            "Expert Review": "Yes" if i.get("requires_expert_review") else "No",
            "Standard": i.get("applicable_standard",""),
        } for i in items]
        return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")

    def export_risk_register_excel(self, analysis: dict, project_name: str) -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            hazards = analysis.get("identified_hazards",[])
            if hazards:
                pd.DataFrame([{
                    "Hazard ID": h.get("hazard_id",""), "Category": h.get("category",""),
                    "Description": h.get("description",""), "Location": h.get("location",""),
                    "Likelihood": h.get("likelihood",""), "Severity": h.get("severity",""),
                    "Risk Score": h.get("risk_score",0), "Confidence": h.get("confidence",""),
                    "Consequences": h.get("potential_consequences",""),
                } for h in hazards]).to_excel(w, sheet_name="Risk Register", index=False)

            cl = analysis.get("safety_checklist",[])
            if cl:
                pd.DataFrame([{
                    "ID": i.get("id",""), "Category": i.get("category",""),
                    "Item": i.get("item",""), "Description": i.get("description",""),
                    "Priority": i.get("priority",""), "Status": i.get("status","Pending"),
                    "Expert Review": "Yes" if i.get("requires_expert_review") else "No",
                    "Standard": i.get("applicable_standard",""),
                } for i in cl]).to_excel(w, sheet_name="Safety Checklist", index=False)

            controls = analysis.get("recommended_controls",[])
            if controls:
                pd.DataFrame([{
                    "Hazard Ref": c.get("hazard_ref",""), "Control Type": c.get("control_type",""),
                    "Description": c.get("description",""), "Implementation": c.get("implementation",""),
                    "Effectiveness": c.get("effectiveness",""), "Cost": c.get("cost_estimate",""),
                    "Priority": c.get("priority",""),
                } for c in controls]).to_excel(w, sheet_name="Controls", index=False)

            stds = analysis.get("applicable_standards",[])
            if stds:
                pd.DataFrame([{
                    "Standard ID": s.get("standard_id",""), "Name": s.get("name",""),
                    "Organization": s.get("organization",""), "Relevance": s.get("relevance",""),
                } for s in stds]).to_excel(w, sheet_name="Standards", index=False)

            pd.DataFrame({
                "Field": ["Project","Overall Risk","Safety Score","Total Hazards","Checklist Items","Generated","Disclaimer"],
                "Value": [project_name, analysis.get("overall_risk_assessment",""),
                          f"{analysis.get('safety_readiness_score','')}/100",
                          len(hazards), len(cl), datetime.now().strftime("%Y-%m-%d %H:%M"),
                          analysis.get("disclaimer","AI-generated guidance only.")],
            }).to_excel(w, sheet_name="Summary", index=False)
        return buf.getvalue()

    def export_pdf_report(self, analysis: dict, project_name: str) -> Optional[bytes]:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            Table, TableStyle, HRFlowable, PageBreak)
            from reportlab.lib.enums import TA_CENTER

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter,
                                    rightMargin=0.75*inch, leftMargin=0.75*inch,
                                    topMargin=1*inch, bottomMargin=0.75*inch)
            styles = getSampleStyleSheet()

            title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=20,
                                     textColor=colors.HexColor("#1e293b"), spaceAfter=6)
            h1_s = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13,
                                  textColor=colors.HexColor("#1d4ed8"), spaceBefore=10, spaceAfter=4)
            h2_s = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11,
                                  textColor=colors.HexColor("#374151"), spaceBefore=6, spaceAfter=3)
            body_s = ParagraphStyle("B", parent=styles["Normal"], fontSize=9,
                                    leading=13, textColor=colors.HexColor("#374151"), spaceAfter=3)
            disc_s = ParagraphStyle("D", parent=styles["Normal"], fontSize=8,
                                    textColor=colors.HexColor("#dc2626"),
                                    backColor=colors.HexColor("#fef2f2"),
                                    borderColor=colors.HexColor("#dc2626"),
                                    borderWidth=1, borderPad=5, leading=12, spaceAfter=8)
            story = []
            story.append(Paragraph("Safety Analysis Report", title_s))
            story.append(Paragraph(
                f"<b>Project:</b> {project_name} &nbsp;|&nbsp; "
                f"<b>Risk:</b> {analysis.get('overall_risk_assessment','N/A')} &nbsp;|&nbsp; "
                f"<b>Score:</b> {analysis.get('safety_readiness_score','N/A')}/100 &nbsp;|&nbsp; "
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_s))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1d4ed8")))
            story.append(Spacer(1,6))
            story.append(Paragraph(
                "⚠️ DISCLAIMER: AI-generated guidance only. Does not constitute certified "
                "professional engineering review. All recommendations must be validated by "
                "qualified safety professionals before implementation.", disc_s))

            story.append(Paragraph("Executive Summary", h1_s))
            story.append(Paragraph(analysis.get("summary","No summary."), body_s))
            story.append(Spacer(1,8))

            story.append(Paragraph("Identified Hazards", h1_s))
            hazards = analysis.get("identified_hazards",[])
            if hazards:
                td = [["ID","Category","Description","Likelihood","Severity","Score"]]
                for h in hazards:
                    d = h.get("description","")[:55] + ("…" if len(h.get("description",""))>55 else "")
                    td.append([h.get("hazard_id",""), h.get("category",""), d,
                                h.get("likelihood",""), h.get("severity",""), str(h.get("risk_score",""))])
                t = Table(td, colWidths=[0.6*inch,1.1*inch,2.8*inch,0.9*inch,0.85*inch,0.55*inch], repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                    ("FONTSIZE",(0,0),(-1,-1),8),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.white]),
                    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#e2e8f0")),
                    ("PADDING",(0,0),(-1,-1),4),
                ]))
                story.append(t)
            story.append(Spacer(1,10))

            story.append(Paragraph("Safety Checklist", h1_s))
            for cat, items in self.organize_by_category(analysis.get("safety_checklist",[])).items():
                story.append(Paragraph(f"{CATEGORY_ICONS.get(cat,'🛡️')} {cat}", h2_s))
                for item in items:
                    ex = " [EXPERT REVIEW REQUIRED]" if item.get("requires_expert_review") else ""
                    story.append(Paragraph(
                        f"<b>[{item.get('priority','Med')}]</b> {item.get('item','')}{ex}", body_s))
                story.append(Spacer(1,4))

            story.append(PageBreak())
            story.append(Paragraph("Applicable Standards", h1_s))
            for s in analysis.get("applicable_standards",[]):
                story.append(Paragraph(f"<b>{s.get('standard_id','')}:</b> {s.get('name','')}", body_s))

            story.append(Spacer(1,10))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
            story.append(Paragraph(
                f"Report generated by AI Safety Checklist Generator — {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
                "AI-generated guidance only.",
                ParagraphStyle("Foot", parent=body_s, fontSize=7, textColor=colors.HexColor("#9ca3af"))))

            doc.build(story)
            return buf.getvalue()
        except ImportError:
            logger.warning("reportlab not installed")
            return None
        except Exception as e:
            logger.error(f"PDF error: {e}")
            return None
