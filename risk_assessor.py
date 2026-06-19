"""risk_assessor.py — Risk scoring, matrix generation, and Plotly visualisations (light theme)."""

import logging
import pandas as pd
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

RISK_COLORS = {"Critical": "#dc2626", "High": "#f97316", "Medium": "#f59e0b", "Low": "#16a34a"}
RISK_BG = {"Critical": "#fef2f2", "High": "#fff7ed", "Medium": "#fffbeb", "Low": "#f0fdf4"}


def _risk_level(score: int) -> str:
    if score >= 15: return "Critical"
    if score >= 10: return "High"
    if score >= 5:  return "Medium"
    return "Low"


class RiskAssessor:
    def get_risk_level(self, score: int) -> str:
        return _risk_level(score)

    # ── Risk Matrix ───────────────────────────────────────────────────────────
    def create_risk_matrix_chart(self, hazards: list) -> go.Figure:
        fig = go.Figure()
        sev_labels  = ["Negligible", "Low", "Medium", "High", "Critical"]
        lik_labels  = ["Very Low",   "Low", "Medium", "High", "Very High"]
        zone_colors = [
            ["#bbf7d0","#bbf7d0","#fef08a","#fed7aa","#fca5a5"],
            ["#bbf7d0","#fef08a","#fef08a","#fed7aa","#fca5a5"],
            ["#bbf7d0","#fef08a","#fef08a","#fef08a","#fed7aa"],
            ["#e5e7eb","#bbf7d0","#bbf7d0","#fef08a","#fef08a"],
            ["#e5e7eb","#e5e7eb","#bbf7d0","#bbf7d0","#fef08a"],
        ]
        for si in range(5):
            for li in range(5):
                fig.add_shape(type="rect",
                    x0=li+0.5, x1=li+1.5, y0=si+0.5, y1=si+1.5,
                    fillcolor=zone_colors[4-si][li], opacity=0.8,
                    line=dict(color="white", width=1.5))

        if hazards:
            lik_map = {"Very Low":1,"Low":2,"Medium":3,"High":4,"Very High":5}
            sev_map = {"Negligible":1,"Low":2,"Medium":3,"High":4,"Critical":5}
            xs, ys, labels, colors, hovers = [], [], [], [], []
            for h in hazards:
                x = lik_map.get(h.get("likelihood","Medium"), 3)
                y = sev_map.get(h.get("severity","Medium"), 3)
                xs.append(x); ys.append(y)
                labels.append(h.get("hazard_id","?"))
                lv = _risk_level(h.get("risk_score", x*y))
                colors.append(RISK_COLORS[lv])
                hovers.append(
                    f"<b>{h.get('hazard_id','?')}</b><br>"
                    f"{h.get('description','')[:60]}<br>"
                    f"Likelihood: {h.get('likelihood','?')} | Severity: {h.get('severity','?')}<br>"
                    f"Risk Score: {h.get('risk_score','?')}"
                )
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers+text",
                text=labels, textposition="top center",
                textfont=dict(size=10, color="#1e293b", family="Inter"),
                marker=dict(size=28, color=colors,
                            line=dict(color="white", width=2), opacity=0.9),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hovers, name="Hazards"
            ))

        fig.update_layout(
            title=dict(text="Risk Matrix", font=dict(size=14, color="#1e293b", family="Inter"), x=0.5),
            xaxis=dict(title=dict(text="Likelihood →", font=dict(color="#475569")),
                       tickmode="array", tickvals=list(range(1,6)), ticktext=lik_labels,
                       range=[0.5,5.5], showgrid=False, tickfont=dict(color="#475569", size=10)),
            yaxis=dict(title=dict(text="↑ Severity", font=dict(color="#475569")),
                       tickmode="array", tickvals=list(range(1,6)), ticktext=sev_labels,
                       range=[0.5,5.5], showgrid=False, tickfont=dict(color="#475569", size=10)),
            plot_bgcolor="white", paper_bgcolor="white",
            height=420, showlegend=False,
            margin=dict(l=90, r=20, t=50, b=70),
        )
        return fig

    # ── Hazard Distribution ───────────────────────────────────────────────────
    def create_hazard_distribution_chart(self, hazards: list) -> go.Figure:
        if not hazards:
            return go.Figure()
        cats = {}
        for h in hazards:
            c = h.get("category","Unknown")
            lv = _risk_level(h.get("risk_score",5))
            cats.setdefault(c, {"Critical":0,"High":0,"Medium":0,"Low":0})
            cats[c][lv] += 1

        fig = go.Figure()
        for lv, col in RISK_COLORS.items():
            fig.add_trace(go.Bar(
                name=lv, x=list(cats.keys()),
                y=[cats[c][lv] for c in cats],
                marker_color=col,
                marker_line=dict(color="white", width=1),
            ))
        fig.update_layout(
            title=dict(text="Hazards by Category", font=dict(size=14, color="#1e293b", family="Inter"), x=0.5),
            barmode="stack",
            xaxis=dict(tickangle=-25, tickfont=dict(color="#475569", size=10),
                       title=dict(text="Category", font=dict(color="#475569"))),
            yaxis=dict(tickfont=dict(color="#475569"),
                       title=dict(text="Count", font=dict(color="#475569")),
                       gridcolor="#f1f5f9"),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(font=dict(color="#1e293b", size=11)),
            height=380, margin=dict(l=50, r=20, t=50, b=90),
        )
        return fig

    # ── Safety Gauge ──────────────────────────────────────────────────────────
    def create_risk_severity_gauge(self, score: int) -> go.Figure:
        if score >= 75:   col, lbl = "#16a34a", "Good"
        elif score >= 50: col, lbl = "#f59e0b", "Fair"
        elif score >= 25: col, lbl = "#f97316", "Poor"
        else:             col, lbl = "#dc2626", "Critical"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x":[0,1],"y":[0,1]},
            title={"text": f"Safety Readiness<br><span style='font-size:0.85em;color:{col}'>{lbl}</span>",
                   "font": {"size":14, "color":"#1e293b", "family":"Inter"}},
            number={"font":{"color":col,"size":38,"family":"Inter"}, "suffix":"/100"},
            gauge={
                "axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#94a3b8",
                        "tickfont":{"color":"#475569"}},
                "bar":{"color":col,"thickness":0.22},
                "bgcolor":"white",
                "borderwidth":1,"bordercolor":"#e2e8f0",
                "steps":[
                    {"range":[0,25],"color":"#fee2e2"},
                    {"range":[25,50],"color":"#ffedd5"},
                    {"range":[50,75],"color":"#fef9c3"},
                    {"range":[75,100],"color":"#dcfce7"},
                ],
            }
        ))
        fig.update_layout(paper_bgcolor="white", height=260,
                          margin=dict(l=20,r=20,t=30,b=10))
        return fig

    # ── Compliance Donut ──────────────────────────────────────────────────────
    def create_compliance_overview_chart(self, reqs: list) -> go.Figure:
        if not reqs:
            return go.Figure()
        counts = {"Mandatory":0,"Recommended":0,"Optional":0}
        for r in reqs:
            lv = r.get("compliance_level","Recommended")
            counts[lv] = counts.get(lv, 0) + 1
        labels = [k for k,v in counts.items() if v]
        values = [v for v in counts.values() if v]
        cols   = ["#dc2626","#f97316","#16a34a"][:len(labels)]

        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.58,
            marker=dict(colors=cols, line=dict(color="white", width=2)),
            textfont=dict(color="#1e293b", size=11),
            hovertemplate="%{label}: %{value}<br>%{percent}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="Compliance Overview", font=dict(size=14, color="#1e293b", family="Inter"), x=0.5),
            legend=dict(font=dict(color="#1e293b", size=11)),
            paper_bgcolor="white", height=300,
            margin=dict(l=20,r=20,t=50,b=20),
            annotations=[dict(text=f"<b>{len(reqs)}</b><br>Standards",
                              x=0.5,y=0.5, font_size=14, font_color="#1e293b", showarrow=False)],
        )
        return fig

    # ── Priority Chart ────────────────────────────────────────────────────────
    def create_risk_priority_chart(self, hazards: list) -> go.Figure:
        if not hazards:
            return go.Figure()
        top = sorted(hazards, key=lambda h: h.get("risk_score",0), reverse=True)[:10]
        labels = [f"{h.get('hazard_id','?')}: {h.get('description','')[:38]}…" for h in top]
        scores = [h.get("risk_score",0) for h in top]
        colors = [RISK_COLORS[_risk_level(s)] for s in scores]

        fig = go.Figure(go.Bar(
            y=labels, x=scores, orientation="h",
            marker=dict(color=colors, line=dict(color="white", width=1)),
            text=[str(s) for s in scores], textposition="outside",
            textfont=dict(color="#1e293b", size=10),
            hovertemplate="<b>%{y}</b><br>Risk Score: %{x}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="Risk Priority (Top 10)", font=dict(size=14, color="#1e293b", family="Inter"), x=0.5),
            xaxis=dict(title=dict(text="Risk Score (1–25)", font=dict(color="#475569")),
                       range=[0,30], tickfont=dict(color="#475569"),
                       gridcolor="#f1f5f9", showgrid=True),
            yaxis=dict(tickfont=dict(color="#475569", size=9), autorange="reversed"),
            plot_bgcolor="white", paper_bgcolor="white",
            height=max(300, len(top)*42+80),
            margin=dict(l=320, r=60, t=50, b=40),
        )
        return fig

    # ── Risk Register DataFrame ───────────────────────────────────────────────
    def prepare_risk_dataframe(self, analysis: dict) -> pd.DataFrame:
        rows = []
        for h in analysis.get("identified_hazards", []):
            rows.append({
                "ID": h.get("hazard_id",""),
                "Category": h.get("category",""),
                "Description": h.get("description",""),
                "Location": h.get("location",""),
                "Likelihood": h.get("likelihood",""),
                "Severity": h.get("severity",""),
                "Risk Score": h.get("risk_score",0),
                "Risk Level": _risk_level(h.get("risk_score",0)),
                "Confidence": h.get("confidence",""),
            })
        df = pd.DataFrame(rows)
        if "Risk Score" in df.columns:
            df = df.sort_values("Risk Score", ascending=False)
        return df

    # ── Stats ──────────────────────────────────────────────────────────────────
    def get_risk_summary_stats(self, analysis: dict) -> dict:
        hazards   = analysis.get("identified_hazards", [])
        checklist = analysis.get("safety_checklist", [])
        risk_counts = {"Critical":0,"High":0,"Medium":0,"Low":0}
        for h in hazards:
            risk_counts[_risk_level(h.get("risk_score",0))] += 1
        return {
            "total_hazards": len(hazards),
            "risk_counts": risk_counts,
            "total_checklist_items": len(checklist),
            "expert_review_count": sum(1 for i in checklist if i.get("requires_expert_review")),
            "total_standards": len(analysis.get("applicable_standards",[])),
            "total_controls": len(analysis.get("recommended_controls",[])),
            "overall_risk": analysis.get("overall_risk_assessment","Unknown"),
            "safety_score": analysis.get("safety_readiness_score",0),
        }
