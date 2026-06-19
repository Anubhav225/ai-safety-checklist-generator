# 🛡️ AI Safety Checklist Generator

AI-powered safety analysis using **Groq** (free API) + **LLaMA 3.3 70B**.

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Add your free API key**
```bash
cp .env.example .env
# Edit .env and add your key from https://console.groq.com/keys
```

**3. Run**
```bash
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Push to GitHub (`.env` is in `.gitignore` — never committed)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. In **Settings → Secrets**, add:
```toml
GROQ_API_KEY = "your_key_here"
```
4. Deploy

## Features
- Upload PDF, DOCX, TXT project documents or paste text
- AI hazard identification, risk assessment & safety checklists
- Interactive risk matrix, readiness gauge & priority charts
- Standards mapping: ISO, OSHA, IEC, IEEE across 10 engineering domains
- Export: PDF, Excel (4 sheets), CSV, Markdown, JSON
- AI safety chatbot for follow-up questions
- Demo mode — no API key needed to explore the UI

> ⚠️ AI-generated guidance only — not a substitute for certified professional safety review.
