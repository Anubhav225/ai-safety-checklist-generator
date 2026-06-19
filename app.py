"""
app.py — AI-Powered Safety Checklist Generator (Groq + Streamlit, light theme).
Run: streamlit run app.py
"""

import os, logging
import streamlit as st
from dotenv import load_dotenv

from safety_analyzer import SafetyAnalyzer
from risk_assessor import RiskAssessor, RISK_COLORS
from checklist_generator import ChecklistGenerator, CATEGORY_ICONS, PRIORITY_COLORS
from standards_mapper import StandardsMapper
from utils import process_uploaded_file, get_domain_icon, get_risk_emoji

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Safety Checklist Generator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Light-theme CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
    background-color: #f8fafc;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * { color: #1e293b !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #475569 !important; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 60%, #2563eb 100%);
    border-radius: 14px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(29,78,216,0.15);
}
.hero-title {
    font-size: 2rem; font-weight: 700; color: #ffffff;
    margin-bottom: 0.3rem; letter-spacing: -0.02em;
}
.hero-subtitle { color: #bfdbfe; font-size: 0.95rem; line-height: 1.5; }

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metric-value { font-size: 2.2rem; font-weight: 700; line-height: 1; }
.metric-label { font-size: 0.72rem; color: #64748b; margin-top: 0.25rem;
                text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Section header ── */
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #1e293b;
    padding: 0.4rem 0 0.3rem;
    border-bottom: 2px solid #2563eb;
    margin-bottom: 1rem;
}

/* ── Risk badges ── */
.badge-critical { background:#fee2e2; color:#dc2626; padding:2px 9px; border-radius:5px;
                  font-size:0.72rem; font-weight:700; border:1px solid #fca5a5; }
.badge-high     { background:#ffedd5; color:#ea580c; padding:2px 9px; border-radius:5px;
                  font-size:0.72rem; font-weight:700; border:1px solid #fdba74; }
.badge-medium   { background:#fef9c3; color:#a16207; padding:2px 9px; border-radius:5px;
                  font-size:0.72rem; font-weight:700; border:1px solid #fde047; }
.badge-low      { background:#dcfce7; color:#15803d; padding:2px 9px; border-radius:5px;
                  font-size:0.72rem; font-weight:700; border:1px solid #86efac; }

/* ── Disclaimer box ── */
.disclaimer-box {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-left: 4px solid #dc2626;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    font-size: 0.82rem;
    color: #b91c1c;
    margin: 0.8rem 0;
}

/* ── Info box ── */
.info-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    font-size: 0.85rem;
    color: #1d4ed8;
    margin: 0.6rem 0;
}

/* ── Checklist item ── */
.cl-item {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.45rem;
    border-left: 3px solid #2563eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Chat bubbles ── */
.chat-user {
    background: #2563eb;
    border-radius: 12px 12px 2px 12px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0 0.4rem 20%;
    color: #ffffff; font-size: 0.9rem;
}
.chat-assistant {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px 12px 12px 2px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 20% 0.4rem 0;
    color: #1e293b; font-size: 0.9rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white !important;
    border: none; border-radius: 8px;
    padding: 0.5rem 1.2rem; font-weight: 600;
    transition: all 0.2s; width: 100%;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}
.stButton > button:hover {
    opacity: 0.92; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,0.35);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #f1f5f9;
    border-radius: 10px; padding: 4px;
    border: 1px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: 6px 14px;
    color: #475569; font-weight: 500; font-size: 0.88rem;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    color: #1e293b !important;
    font-weight: 500;
}
.streamlit-expanderContent {
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    background: #ffffff !important;
    padding: 0.8rem 1rem !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #1e293b !important;
    font-size: 0.9rem;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #2563eb !important; border-radius: 4px; }

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }

/* ── Hide streamlit menu & footer ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "analysis_result": None, "project_name": "My Project",
        "selected_domain": "Mechanical Engineering",
        "chat_history": [], "checklist_status": {}, "analysis_done": False,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Cached services ───────────────────────────────────────────────────────────
@st.cache_resource
def get_services(api_key: str):
    return {
        "analyzer":  SafetyAnalyzer(api_key),
        "assessor":  RiskAssessor(),
        "checklist": ChecklistGenerator(),
        "standards": StandardsMapper(),
    }

def _get_api_key() -> str:
    """Load API key from environment / .env only."""
    return os.getenv("GROQ_API_KEY", "").strip()

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ Safety Generator")
        st.markdown("---")

        # API key status — read from env, never shown
        api_key = _get_api_key()
        if api_key:
            st.markdown(
                "<div style='background:#f0fdf4;border:1px solid #86efac;border-radius:8px;"
                "padding:8px 12px;font-size:0.82rem;color:#15803d;margin-bottom:0.5rem'>"
                "✅ <b>Groq API key loaded</b></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;"
                "padding:8px 12px;font-size:0.82rem;color:#b91c1c;margin-bottom:0.5rem'>"
                "⚠️ <b>No API key found.</b><br>Add <code>GROQ_API_KEY</code> to your "
                "<code>.env</code> file.<br>"
                "<a href='https://console.groq.com/keys' target='_blank' "
                "style='color:#b91c1c'>Get a free key →</a></div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### 📁 Project Setup")

        pname = st.text_input("Project Name", value=st.session_state.project_name,
                               placeholder="e.g. Conveyor Belt System v2")
        st.session_state.project_name = pname

        domains = StandardsMapper().get_all_domains()
        icons   = [f"{get_domain_icon(d)} {d}" for d in domains]
        idx = domains.index(st.session_state.selected_domain) \
              if st.session_state.selected_domain in domains else 0
        sel = st.selectbox("Engineering Domain", range(len(domains)),
                           format_func=lambda i: icons[i], index=idx)
        st.session_state.selected_domain = domains[sel]

        st.markdown("---")

        if st.button("🎯 Load Demo (No API Key)", use_container_width=True):
            demo_analyzer = SafetyAnalyzer.__new__(SafetyAnalyzer)
            st.session_state.analysis_result = demo_analyzer.get_demo_analysis()
            st.session_state.analysis_done   = True
            st.session_state.chat_history    = []
            st.session_state.checklist_status = {}
            st.success("Demo analysis loaded!")
            st.rerun()

        if st.session_state.analysis_done and st.session_state.analysis_result:
            st.markdown("---")
            st.markdown("### 📊 Current Analysis")
            a = st.session_state.analysis_result
            risk  = a.get("overall_risk_assessment","N/A")
            score = a.get("safety_readiness_score", 0)
            st.markdown(f"**Risk:** {get_risk_emoji(risk)} {risk}")
            st.progress(score / 100)
            st.caption(f"Safety Score: {score}/100")
            st.markdown(f"🔍 Hazards: **{len(a.get('identified_hazards',[]))}**")
            st.markdown(f"✅ Checklist: **{len(a.get('safety_checklist',[]))}** items")

            if st.button("🔄 New Analysis", use_container_width=True):
                for k in ["analysis_result","analysis_done","chat_history","checklist_status"]:
                    st.session_state[k] = None if k == "analysis_result" else (False if k == "analysis_done" else {})
                st.rerun()

        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.72rem;color:#94a3b8;text-align:center'>"
            "Powered by Groq · LLaMA 3.3 70B<br>"
            "⚠️ AI guidance only — not a substitute<br>for certified professional review"
            "</div>",
            unsafe_allow_html=True,
        )

    return api_key


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_input_page(api_key: str):
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🛡️ AI Safety Checklist Generator</div>
        <div class="hero-subtitle">
            Upload engineering documents or describe your project to receive an AI-powered
            safety analysis with hazard identification, risk assessment, and compliance checklists.
            Powered by Groq · LLaMA 3.3 70B — fast and free.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
    ⚠️ <b>Disclaimer:</b> This tool generates AI-assisted safety guidance only.
    Results do <b>not</b> constitute certified professional engineering review, regulatory
    approval, or legal compliance. Always validate with qualified safety professionals.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">📄 Project Input</div>', unsafe_allow_html=True)
        method = st.radio("Input Method", ["📝 Text Description", "📁 Upload Document"],
                          horizontal=True, label_visibility="collapsed")
        project_content = ""

        if method == "📝 Text Description":
            project_content = st.text_area(
                "Describe your project:",
                height=310,
                placeholder=(
                    "Example:\n\nWe are designing a 6-axis industrial robot arm for automotive "
                    "assembly. The system includes:\n"
                    "- 6 servo-driven joints (max torque 500 Nm)\n"
                    "- Payload: 150 kg, Reach: 2.8 m\n"
                    "- 480V AC 3-phase power supply\n"
                    "- PLC-based motion control with safety relays\n"
                    "- Shared human-robot workspace\n\n"
                    "Describe your project here..."
                ),
                label_visibility="collapsed",
            )
        else:
            uploaded = st.file_uploader("Upload document",
                                        type=["pdf","docx","doc","txt","md"],
                                        help="PDF, DOCX, TXT or Markdown",
                                        label_visibility="collapsed")
            if uploaded:
                with st.spinner("Extracting text…"):
                    project_content, ftype = process_uploaded_file(uploaded)
                st.success(f"✅ Extracted {len(project_content):,} characters from {ftype}")
                with st.expander("Preview extracted text"):
                    st.text(project_content[:1500] + ("…" if len(project_content) > 1500 else ""))

        with st.expander("➕ Additional context (optional)"):
            extra = st.text_area("Extra context or specific concerns:", height=90,
                                 placeholder="e.g. Operating outdoors −20°C to 50°C. Key concern: personnel nearby during operation.",
                                 label_visibility="collapsed")
            if extra.strip():
                project_content = project_content + "\n\nADDITIONAL CONTEXT:\n" + extra

    with col2:
        st.markdown('<div class="section-header">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
        domain = st.session_state.selected_domain
        st.markdown(
            f"<div class='info-box'>{get_domain_icon(domain)} <b>Domain:</b> {domain}</div>",
            unsafe_allow_html=True,
        )
        mapper = StandardsMapper()
        stds = mapper.get_mandatory_standards(domain)[:4]
        st.markdown("**Key mandatory standards:**")
        for s in stds:
            st.markdown(f"<span style='font-size:0.82rem;color:#475569'>• <code>{s['id']}</code> {s['name'][:42]}…</span>",
                        unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**What will be generated:**")
        items = ["Hazard Identification","Risk Assessment Matrix","Safety Checklist",
                 "Standards Mapping","Emergency Procedures","Maintenance Safety","Training Recommendations"]
        for item in items:
            st.markdown(f"<span style='font-size:0.83rem;color:#374151'>✓ {item}</span>",
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        disabled = not api_key or not project_content.strip()
        clicked  = st.button("🔍 Generate Safety Analysis", use_container_width=True,
                             type="primary", disabled=disabled)

    if not api_key:
        st.warning("⚠️ Groq API key not found. Add `GROQ_API_KEY` to your `.env` file.")
    elif not project_content.strip():
        st.info("💡 Enter a project description or upload a document to begin.")

    if clicked and api_key and project_content.strip():
        _run_analysis(api_key, project_content, domain)


def _run_analysis(api_key: str, content: str, domain: str):
    svc = get_services(api_key)
    bar  = st.progress(0)
    msg  = st.empty()
    steps = [
        (0.1, "🔍 Parsing project content…"),
        (0.3, "🤖 Sending to Groq AI for analysis…"),
        (0.65,"📊 Identifying hazards and risks…"),
        (0.85,"✅ Building safety checklist…"),
        (0.95,"📋 Mapping standards…"),
    ]
    import time
    for pct, txt in steps:
        bar.progress(pct); msg.info(txt); time.sleep(0.25)

    analysis, error = svc["analyzer"].analyze_project(
        content, domain, st.session_state.project_name)

    bar.progress(1.0); msg.empty(); bar.empty()

    if error:
        st.error(f"❌ {error}")
        return

    st.session_state.analysis_result  = analysis
    st.session_state.analysis_done    = True
    st.session_state.chat_history     = []
    st.session_state.checklist_status = {}
    st.success("✅ Safety analysis complete!")
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def render_results(api_key: str):
    analysis = st.session_state.analysis_result
    assessor = RiskAssessor()
    cl_gen   = ChecklistGenerator()
    pname    = st.session_state.project_name or "Project"
    stats    = assessor.get_risk_summary_stats(analysis)
    overall  = analysis.get("overall_risk_assessment","N/A")
    score    = analysis.get("safety_readiness_score", 0)

    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">🛡️ {pname} — Safety Report</div>
        <div class="hero-subtitle">
            {analysis.get('project_type','N/A')} &nbsp;·&nbsp;
            {st.session_state.selected_domain} &nbsp;·&nbsp;
            Overall Risk: <b>{get_risk_emoji(overall)} {overall}</b> &nbsp;·&nbsp;
            Safety Score: <b>{score}/100</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    kpis = [
        (stats["total_hazards"],           "Total Hazards",           "#f97316"),
        (stats["risk_counts"]["Critical"], "Critical Risks",          "#dc2626"),
        (stats["risk_counts"]["High"],     "High Risks",              "#f97316"),
        (stats["total_checklist_items"],   "Checklist Items",         "#2563eb"),
        (stats["total_standards"],         "Standards Referenced",    "#7c3aed"),
        (stats["expert_review_count"],     "Need Expert Review",      "#f59e0b"),
    ]
    cols = st.columns(6)
    for col, (val, lbl, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tabs = st.tabs(["📊 Dashboard","⚠️ Hazards","✅ Checklist","📋 Standards",
                    "🔧 Controls","🚨 Emergency","💬 AI Chat","📥 Export"])

    with tabs[0]: _tab_dashboard(analysis, assessor)
    with tabs[1]: _tab_hazards(analysis, assessor)
    with tabs[2]: _tab_checklist(analysis, cl_gen)
    with tabs[3]: _tab_standards(analysis)
    with tabs[4]: _tab_controls(analysis)
    with tabs[5]: _tab_emergency(analysis)
    with tabs[6]: _tab_chat(api_key, analysis)
    with tabs[7]: _tab_export(analysis, cl_gen, pname)


# ── TAB: Dashboard ─────────────────────────────────────────────────────────
def _tab_dashboard(analysis, assessor):
    st.markdown('<div class="section-header">📝 Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;"
        f"padding:1rem 1.2rem;color:#1e40af;font-size:0.9rem;line-height:1.6'>"
        f"{analysis.get('summary','No summary.')}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='disclaimer-box' style='margin-top:0.6rem'>"
        f"⚠️ {analysis.get('disclaimer','AI-generated guidance only.')}</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.markdown('<div class="section-header">🎯 Risk Matrix</div>', unsafe_allow_html=True)
        st.plotly_chart(assessor.create_risk_matrix_chart(
            analysis.get("identified_hazards",[])), use_container_width=True)
    with c2:
        st.markdown('<div class="section-header">📈 Safety Readiness</div>', unsafe_allow_html=True)
        st.plotly_chart(assessor.create_risk_severity_gauge(
            analysis.get("safety_readiness_score",50)), use_container_width=True)
        st.markdown('<div class="section-header">📊 Compliance Overview</div>', unsafe_allow_html=True)
        st.plotly_chart(assessor.create_compliance_overview_chart(
            analysis.get("compliance_requirements",[])), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-header">📦 Hazard Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(assessor.create_hazard_distribution_chart(
            analysis.get("identified_hazards",[])), use_container_width=True)
    with c4:
        st.markdown('<div class="section-header">🏆 Risk Priority</div>', unsafe_allow_html=True)
        st.plotly_chart(assessor.create_risk_priority_chart(
            analysis.get("identified_hazards",[])), use_container_width=True)

    areas = analysis.get("areas_requiring_expert_validation",[])
    if areas:
        st.markdown('<div class="section-header">👨‍🔬 Requires Expert Validation</div>',
                    unsafe_allow_html=True)
        for a in areas:
            st.warning(f"⚠️ {a}")


# ── TAB: Hazards ────────────────────────────────────────────────────────────
def _tab_hazards(analysis, assessor):
    st.markdown('<div class="section-header">⚠️ Identified Hazards</div>', unsafe_allow_html=True)
    hazards = analysis.get("identified_hazards",[])
    if not hazards:
        st.info("No hazards identified.")
        return

    c1, c2, c3 = st.columns(3)
    cats  = ["All"] + sorted({h.get("category","?") for h in hazards})
    sevs  = ["All","Critical","High","Medium","Low"]
    sorts = ["Risk Score ↓","Risk Score ↑","Category"]
    cat_f = c1.selectbox("Category", cats)
    sev_f = c2.selectbox("Severity", sevs)
    srt   = c3.selectbox("Sort", sorts)

    filt = [h for h in hazards
            if (cat_f == "All" or h.get("category") == cat_f)
            and (sev_f == "All" or h.get("severity") == sev_f)]
    if srt == "Risk Score ↓": filt.sort(key=lambda h: h.get("risk_score",0), reverse=True)
    elif srt == "Risk Score ↑": filt.sort(key=lambda h: h.get("risk_score",0))
    else: filt.sort(key=lambda h: h.get("category",""))

    st.caption(f"Showing {len(filt)} / {len(hazards)} hazards")

    for h in filt:
        lv    = assessor.get_risk_level(h.get("risk_score",0))
        color = RISK_COLORS[lv]
        badge = f"<span class='badge-{lv.lower()}'>{lv}</span>"
        with st.expander(
            f"{get_risk_emoji(lv)} {h.get('hazard_id','?')} — {h.get('description','')[:65]}  [Score: {h.get('risk_score','?')}]"
        ):
            k1,k2,k3,k4 = st.columns(4)
            k1.metric("Risk Score",  h.get("risk_score","?"))
            k2.metric("Likelihood",  h.get("likelihood","?"))
            k3.metric("Severity",    h.get("severity","?"))
            k4.metric("Confidence",  h.get("confidence","?"))
            st.markdown(f"**Category:** {h.get('category','?')}  |  **Location:** {h.get('location','?')}")
            st.markdown(f"**Potential Consequences:** {h.get('potential_consequences','?')}")

    st.markdown("---")
    st.markdown('<div class="section-header">📊 Risk Register</div>', unsafe_allow_html=True)
    df = assessor.prepare_risk_dataframe(analysis)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── TAB: Checklist ──────────────────────────────────────────────────────────
def _tab_checklist(analysis, cl_gen):
    st.markdown('<div class="section-header">✅ Safety Checklist</div>', unsafe_allow_html=True)
    checklist = analysis.get("safety_checklist",[])
    if not checklist:
        st.info("No checklist items generated.")
        return

    total     = len(checklist)
    completed = sum(1 for i in checklist
                    if st.session_state.checklist_status.get(i.get("id","")) == "Completed")
    pct       = completed / total if total else 0

    c1, c2, c3 = st.columns([3,1,1])
    c1.progress(pct, text=f"Progress: {completed}/{total} items completed")
    c2.metric("Completed", f"{completed}/{total}")
    c3.metric("Done", f"{pct*100:.0f}%")

    cats = list({i.get("category","General") for i in checklist})
    sel_cats = st.multiselect("Filter Categories", cats, default=cats)
    pri_f    = st.selectbox("Filter Priority", ["All","Critical","High","Medium","Low"])

    for cat, items in cl_gen.organize_by_category(checklist).items():
        if cat not in sel_cats:
            continue
        icon  = CATEGORY_ICONS.get(cat,"🛡️")
        crit  = sum(1 for i in items if i.get("priority")=="Critical")
        highs = sum(1 for i in items if i.get("priority")=="High")

        with st.expander(f"{icon} **{cat}** — {len(items)} items | {crit} Critical | {highs} High",
                         expanded=(crit > 0)):
            for item in items:
                if pri_f != "All" and item.get("priority") != pri_f:
                    continue
                iid  = item.get("id", f"i_{hash(item.get('item',''))}")
                curr = st.session_state.checklist_status.get(iid,"Pending")
                col1, col2 = st.columns([4,1])
                with col1:
                    pri   = item.get("priority","Medium")
                    color = PRIORITY_COLORS.get(pri,"#64748b")
                    tc    = "black" if pri == "Medium" else "white"
                    ex    = " 🔬" if item.get("requires_expert_review") else ""
                    std   = f" `{item.get('applicable_standard','')}`" if item.get("applicable_standard") else ""
                    st.markdown(
                        f"<span style='background:{color};color:{tc};"
                        f"padding:1px 7px;border-radius:4px;font-size:0.71rem;font-weight:700'>"
                        f"{pri}</span> **{item.get('item','')}**{ex}{std}",
                        unsafe_allow_html=True,
                    )
                    if item.get("description"):
                        st.caption(item["description"])
                    if item.get("requires_expert_review"):
                        st.caption("⚠️ *Requires expert human validation*")
                with col2:
                    new = st.selectbox(
                        "Status", ["Pending","In Progress","Completed","N/A"],
                        index=["Pending","In Progress","Completed","N/A"].index(curr),
                        key=f"cl_{iid}", label_visibility="collapsed",
                    )
                    st.session_state.checklist_status[iid] = new
                st.markdown("<hr style='margin:5px 0;opacity:0.08'>", unsafe_allow_html=True)


# ── TAB: Standards ──────────────────────────────────────────────────────────
def _tab_standards(analysis):
    st.markdown('<div class="section-header">📋 Compliance & Standards</div>',
                unsafe_allow_html=True)
    reqs = analysis.get("compliance_requirements",[])
    if reqs:
        st.markdown("### 📜 Compliance Requirements")
        for r in reqs:
            lv = r.get("compliance_level","Recommended")
            lc = {"Mandatory":"#dc2626","Recommended":"#f97316","Optional":"#16a34a"}.get(lv,"#64748b")
            with st.expander(f"**{r.get('standard','?')}** — {lv}"):
                st.markdown(f"**Requirement:** {r.get('requirement','?')}")
                st.markdown(f"**Applicability:** {r.get('applicability','?')}")
                st.markdown(f"**Notes:** {r.get('notes','?')}")
                st.markdown(
                    f"<span style='background:{lc};color:white;"
                    f"padding:2px 8px;border-radius:4px;font-size:0.72rem'>{lv}</span>",
                    unsafe_allow_html=True,
                )

    stds = analysis.get("applicable_standards",[])
    if stds:
        st.markdown("---")
        st.markdown("### 🏛️ Referenced Standards")
        for s in stds:
            with st.expander(f"**{s.get('standard_id','?')}** — {s.get('name','?')}"):
                c1, c2 = st.columns(2)
                c1.markdown(f"**Organization:** {s.get('organization','?')}")
                c1.markdown(f"**Relevance:** {s.get('relevance','?')}")
                c2.markdown(f"**Reference:** {s.get('url_reference','?')}")
                reqs2 = s.get("key_requirements",[])
                if reqs2:
                    st.markdown("**Key Requirements:** " + " · ".join(reqs2))

    import pandas as pd
    domain = st.session_state.selected_domain
    mapper = StandardsMapper()
    st.markdown("---")
    st.markdown(f"### 📚 All Standards for {get_domain_icon(domain)} {domain}")
    df = pd.DataFrame(mapper.get_standards_summary_table(domain))
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── TAB: Controls ───────────────────────────────────────────────────────────
def _tab_controls(analysis):
    st.markdown('<div class="section-header">🔧 Controls & Preventive Measures</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🛡️ Recommended Controls")
        for ctrl in analysis.get("recommended_controls",[]):
            pri   = ctrl.get("priority","Short-term")
            pcolor = {"Immediate":"#dc2626","Short-term":"#f97316","Long-term":"#16a34a"}.get(pri,"#64748b")
            with st.expander(f"**{ctrl.get('hazard_ref','?')}** — {ctrl.get('control_type','?')} [{pri}]"):
                st.markdown(f"**Description:** {ctrl.get('description','?')}")
                st.markdown(f"**Implementation:** {ctrl.get('implementation','?')}")
                k1,k2,k3 = st.columns(3)
                k1.metric("Effectiveness", ctrl.get("effectiveness","?"))
                k2.metric("Cost",          ctrl.get("cost_estimate","?"))
                k3.metric("Priority",      pri)

    with c2:
        st.markdown("### 🔄 Preventive Measures")
        for m in analysis.get("preventive_measures",[]):
            with st.expander(f"**{m.get('category','?')}** — {m.get('measure','?')[:50]}…"):
                st.markdown(f"**Measure:** {m.get('measure','?')}")
                st.markdown(f"**Frequency:** {m.get('frequency','?')}  |  **Responsible:** {m.get('responsible_party','?')}")
                doc = "✅ Yes" if m.get("documentation_required") else "❌ No"
                st.markdown(f"**Documentation Required:** {doc}")

    maint = analysis.get("maintenance_safety",[])
    if maint:
        st.markdown("---")
        st.markdown("### 🔩 Maintenance Safety")
        for m in maint:
            with st.expander(f"**{m.get('component','?')}** — {m.get('maintenance_type','?')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Frequency:** {m.get('frequency','?')}")
                    loto = "✅ Required" if m.get("lockout_tagout_required") else "❌ Not required"
                    st.markdown(f"**Lockout/Tagout:** {loto}")
                    for p in m.get("safety_precautions",[]):
                        st.markdown(f"• {p}")
                with c2:
                    for t in m.get("special_tools_ppe",[]):
                        st.markdown(f"• {t}")

    training = analysis.get("safety_training_recommendations",[])
    if training:
        import pandas as pd
        st.markdown("---")
        st.markdown("### 🎓 Training Recommendations")
        df = pd.DataFrame([{
            "Topic": t.get("training_topic",""), "Audience": t.get("target_audience",""),
            "Frequency": t.get("frequency",""), "Method": t.get("method",""),
            "Hours": t.get("duration_hours",0),
        } for t in training])
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── TAB: Emergency ──────────────────────────────────────────────────────────
def _tab_emergency(analysis):
    st.markdown('<div class="section-header">🚨 Emergency Procedures</div>',
                unsafe_allow_html=True)
    procs = analysis.get("emergency_procedures",[])
    if not procs:
        st.info("No emergency procedures generated.")
        return

    for i, p in enumerate(procs):
        st.markdown(f"### 🚨 Scenario {i+1}: {p.get('scenario','?')}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**⚡ Immediate Actions:**")
            for j, act in enumerate(p.get("immediate_actions",[]), 1):
                st.markdown(
                    f"<div style='background:#fef2f2;border-left:3px solid #dc2626;"
                    f"padding:6px 10px;margin:4px 0;border-radius:4px;font-size:0.88rem'>"
                    f"<b>{j}.</b> {act}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("**📞 Notify:**")
            for n in p.get("notification_required",[]):
                st.markdown(f"• {n}")
        with c2:
            st.markdown("**🧰 Equipment Needed:**")
            for eq in p.get("equipment_needed",[]):
                st.markdown(f"• {eq}")
            st.markdown("**🔄 Recovery Steps:**")
            for k, s in enumerate(p.get("recovery_steps",[]),1):
                st.markdown(f"{k}. {s}")
        st.markdown("---")


# ── TAB: Chat ───────────────────────────────────────────────────────────────
def _tab_chat(api_key: str, analysis: dict):
    st.markdown('<div class="section-header">💬 AI Safety Chatbot</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='info-box'>Ask follow-up questions about this safety analysis, "
        "request clarifications, or explore specific hazards and standards.</div>",
        unsafe_allow_html=True,
    )

    for msg in st.session_state.chat_history:
        css = "chat-user" if msg["role"] == "user" else "chat-assistant"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"<div class='{css}'>{icon} {msg['content']}</div>",
                    unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("**Suggested questions:**")
        suggestions = [
            "What is the most critical hazard I should fix first?",
            "Which standards are mandatory for this project?",
            "What PPE is required for maintenance?",
            "How do I implement lockout/tagout?",
            "What training is required for operators?",
        ]
        for i in range(0, len(suggestions), 2):
            row = st.columns(2)
            for j, col in enumerate(row):
                if i+j < len(suggestions):
                    with col:
                        if st.button(f"💬 {suggestions[i+j]}", key=f"sug_{i+j}"):
                            _do_chat(api_key, suggestions[i+j], analysis)

    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5,1])
        with c1:
            user_msg = st.text_input("Your question…", label_visibility="collapsed",
                                     placeholder="Ask anything about this safety analysis…")
        with c2:
            send = st.form_submit_button("Send ➤", use_container_width=True)
    if send and user_msg.strip():
        _do_chat(api_key, user_msg, analysis)

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


def _do_chat(api_key: str, message: str, analysis: dict):
    if not api_key:
        st.error("API key required for chat.")
        return
    svc = get_services(api_key)
    with st.spinner("🤖 Thinking…"):
        reply, history = svc["analyzer"].chat_with_analysis(
            message, analysis, st.session_state.chat_history)
    st.session_state.chat_history = history
    st.rerun()


# ── TAB: Export ─────────────────────────────────────────────────────────────
def _tab_export(analysis, cl_gen, pname):
    st.markdown('<div class="section-header">📥 Export Reports</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='disclaimer-box'>⚠️ All exports include the AI-generated disclaimer. "
        "These reports are for guidance only.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 📄 Document Formats")
        md = cl_gen.export_to_markdown(analysis, pname)
        st.download_button("📝 Markdown Report", md.encode(),
            f"safety_report_{pname.replace(' ','_')}.md", "text/markdown",
            use_container_width=True)

        js = cl_gen.export_to_json(analysis)
        st.download_button("🗂️ JSON Export", js.encode(),
            f"safety_analysis_{pname.replace(' ','_')}.json", "application/json",
            use_container_width=True)

        csv = cl_gen.export_checklist_csv(analysis.get("safety_checklist",[]))
        st.download_button("📊 Checklist CSV", csv,
            f"checklist_{pname.replace(' ','_')}.csv", "text/csv",
            use_container_width=True)

    with c2:
        st.markdown("### 📊 Spreadsheet & PDF")
        try:
            xl = cl_gen.export_risk_register_excel(analysis, pname)
            st.download_button("📈 Excel Risk Register", xl,
                f"risk_register_{pname.replace(' ','_')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except Exception as e:
            st.error(f"Excel export error: {e}")

        pdf = cl_gen.export_pdf_report(analysis, pname)
        if pdf:
            st.download_button("📄 PDF Safety Report", pdf,
                f"safety_report_{pname.replace(' ','_')}.pdf", "application/pdf",
                use_container_width=True)
        else:
            st.info("PDF export requires `reportlab`. Install with: `pip install reportlab`")

    st.markdown("---")
    st.markdown("### 👁️ Report Preview")
    with st.expander("Click to expand Markdown preview"):
        md_prev = cl_gen.export_to_markdown(analysis, pname)
        st.markdown(md_prev)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    api_key = render_sidebar()
    if not st.session_state.analysis_done or not st.session_state.analysis_result:
        render_input_page(api_key)
    else:
        render_results(api_key)


if __name__ == "__main__":
    main()
