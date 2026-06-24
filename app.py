"""
TruthLens -- AI Fake News Detector for Students
Powered by Google Gemini API (FREE)
====================================================
Developed by: [YOUR NAME]
College: [YOUR COLLEGE NAME]
Internship Project Submission

SETUP (one time only):
    pip install streamlit google-generativeai plotly fpdf2

RUN:
    streamlit run app.py

Get FREE Gemini API key: https://aistudio.google.com/apikey
====================================================
"""

import os, re, json
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
from fpdf import FPDF

GEMINI_MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are a media-literacy assistant helping students evaluate
the credibility of a news article.

Analyze the article and respond with ONLY a single valid JSON object:
{
  "credibility_score": <integer 0-100>,
  "verdict": "<one of: Likely Reliable | Mixed / Needs Verification | Likely Unreliable>",
  "confidence": "<one of: Low | Moderate | High>",
  "summary": "<neutral 2-3 sentence plain-language summary>",
  "red_flags": ["<short phrase>"],
  "green_flags": ["<short phrase>"],
  "key_claims_to_verify": ["<specific claim worth checking>"],
  "reasoning": "<2-4 sentences explaining the score simply>"
}
Output ONLY valid JSON. No markdown. No text outside the JSON."""

SAMPLE_CALM = """City Council Approves Revised Water Budget After Public Review

The city council voted 6-2 on Tuesday to approve a revised water infrastructure
budget following a three-month public comment period. According to the finance
department's published report, the plan allocates funding for pipe replacement in
older neighborhoods over the next four years.

"We adjusted the original proposal after residents raised concerns," said the
council's infrastructure committee chair. Independent estimates from a regional
engineering association were cited alongside the city's own figures."""

SAMPLE_FAKE = """THEY DON'T WANT YOU TO KNOW THIS ABOUT YOUR TAP WATER!!!

Shocking new info that the city REFUSES to tell you. Sources (who wish to remain
hidden) say the water supply has been secretly changed and officials are covering
it up RIGHT NOW. Share this before it gets taken down!!! Mainstream media won't
touch this story. Wake up before it's too late -- your family's health depends on
you sharing this immediately, no questions asked."""

SAMPLES = {
    "-- Select a sample to try --": None,
    "Sample A · Calm, sourced news report": SAMPLE_CALM,
    "Sample B · Sensational, unsourced claim": SAMPLE_FAKE,
}

def parse_json(raw):
    raw = raw.strip().replace("```json","").replace("```","").strip()
    try: return json.loads(raw)
    except:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m: return json.loads(m.group(0))
        raise ValueError("Could not parse model response.")

def analyze(api_key, text, title=""):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)
    prompt = f"ARTICLE TITLE: {title or '(no title)'}\n\nARTICLE TEXT:\n{text}"
    resp = model.generate_content(prompt)
    data = parse_json(resp.text)
    data["credibility_score"] = int(max(0, min(100, data.get("credibility_score", 50))))
    for k in ["red_flags","green_flags","key_claims_to_verify"]:
        data.setdefault(k, [])
    for k in ["verdict","confidence","summary","reasoning"]:
        data.setdefault(k, "")
    return data

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica","B",14)
        self.set_text_color(29,53,87)
        self.cell(0,10,"TruthLens — Credibility Report",ln=True)
        self.set_draw_color(29,53,87)
        self.set_line_width(0.6)
        self.line(10,18,200,18)
        self.ln(6)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica","I",8)
        self.set_text_color(120,120,120)
        self.cell(0,10,f"TruthLens | Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",align="C")

def build_pdf(title, report):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Helvetica","",10)
    pdf.set_font("Helvetica","B",12); pdf.multi_cell(0,7,title or "(Untitled Article)")
    pdf.ln(2)
    pdf.set_font("Helvetica","B",11); pdf.set_text_color(29,53,87)
    pdf.cell(0,8,f"Verdict: {report['verdict']} ({report['credibility_score']}/100)",ln=True)
    pdf.set_font("Helvetica","",9); pdf.set_text_color(80,80,80)
    pdf.cell(0,6,f"Confidence: {report.get('confidence','')}",ln=True)
    pdf.set_text_color(30,30,30); pdf.ln(2)
    for section, key in [("Summary","summary"),("AI Reasoning","reasoning")]:
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(29,53,87)
        pdf.cell(0,7,section,ln=True)
        pdf.set_font("Helvetica","",10); pdf.set_text_color(30,30,30)
        pdf.multi_cell(0,6,report.get(key,""))
        pdf.ln(1)
    for section, key, empty in [("Red Flags","red_flags","None identified."),
                                  ("Green Flags","green_flags","None identified."),
                                  ("Claims to Verify","key_claims_to_verify","None flagged.")]:
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(29,53,87)
        pdf.cell(0,7,section,ln=True)
        pdf.set_font("Helvetica","",10); pdf.set_text_color(30,30,30)
        items = report.get(key,[]) or [empty]
        for item in items: pdf.multi_cell(0,6,f"  • {item}")
        pdf.ln(1)
    pdf.set_font("Helvetica","I",8); pdf.set_text_color(130,130,130)
    pdf.multi_cell(0,5,"Disclaimer: This is a critical-thinking aid based on writing style "
                   "and structure, not a verified fact-check. Always cross-check with trusted sources.")
    return bytes(pdf.output(dest="S"))

# ── UI ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="TruthLens | Fake News Detector",
                   page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{
  background:#FAFAF8!important;color:#1B2430!important;font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:#F1F0EC!important;}
.masthead{text-align:center;padding:.4rem 0 .7rem;}
.masthead h1{font-family:'Source Serif 4',serif;font-size:2.4rem;letter-spacing:.07em;color:#1D3557;margin:0 0 .2rem;}
.masthead p{font-size:.93rem;color:#5b6472;margin:0;}
.hairline{border-top:2px solid #1D3557;border-bottom:1px solid #D8D6CE;margin:.4rem 0 1.3rem;}
.lbl{font-family:'IBM Plex Mono',monospace;font-size:.73rem;color:#1D3557;letter-spacing:.06em;}
.card{background:#F4F3EF;border:1px solid #D8D6CE;border-radius:8px;padding:.9rem 1.1rem;margin:.5rem 0 1rem;}
.flag-r{color:#9B2C2C;background:rgba(155,44,44,.07);border-radius:6px;padding:.35rem .6rem;margin-bottom:.35rem;font-size:.84rem;display:block;}
.flag-g{color:#2A6F4D;background:rgba(42,111,77,.07);border-radius:6px;padding:.35rem .6rem;margin-bottom:.35rem;font-size:.84rem;display:block;}
.verdict-tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.82rem;padding:.3rem .85rem;border-radius:5px;color:#fff;letter-spacing:.03em;}
.muted{color:#8a8f99;font-size:.84rem;}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("history", [])
st.session_state.setdefault("article_text", "")

st.markdown("""
<div class="masthead">
  <h1>🔍 TRUTHLENS</h1>
  <p>AI-powered Fake News Detector &nbsp;·&nbsp; Internship Project by <b>[YOUR NAME]</b></p>
</div>
<div class="hairline"></div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API Setup")
    api_key = st.text_input("Google Gemini API Key", type="password",
                            value=os.getenv("GEMINI_API_KEY",""),
                            help="Free key from aistudio.google.com/apikey")
    st.caption("Free • No credit card needed • Not stored")
    st.markdown("[🔗 Get FREE Gemini Key](https://aistudio.google.com/apikey)")

    st.divider()
    st.markdown("## 📋 How to Spot Fake News")
    st.markdown("""
1. **Source** — Is it a known outlet?
2. **Author** — Is a real person credited?
3. **Date** — Is old news re-shared as new?
4. **Emotion** — Does it outrage or scare first?
5. **Cross-check** — Do other outlets report it?
""")

    st.divider()
    st.markdown("## 📊 Session History")
    if st.session_state["history"]:
        for h in reversed(st.session_state["history"][-6:]):
            color = "🟢" if h["score"]>=70 else "🟡" if h["score"]>=40 else "🔴"
            st.markdown(f"{color} **{h['score']}/100** — {h['title'][:30]}")
        if len(st.session_state["history"]) > 1:
            scores = [h["score"] for h in st.session_state["history"]]
            fig = go.Figure(go.Scatter(y=scores, mode="lines+markers",
                            line=dict(color="#1D3557", width=2)))
            fig.update_layout(height=120, margin=dict(l=0,r=0,t=5,b=0),
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              xaxis=dict(visible=False),
                              yaxis=dict(range=[0,100],visible=False))
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar":False})
    else:
        st.caption("Your checked articles will appear here.")

    st.divider()
    if st.button("🔄 Reset Everything", use_container_width=True):
        for k in ["article_text","fetched_title","last_report",
                  "last_title","history","_last_sample"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────
col_in, col_out = st.columns([1, 1.3], gap="large")

with col_in:
    st.markdown("<span class='lbl'>01 / INPUT</span>", unsafe_allow_html=True)

    choice = st.selectbox("Try a sample article", list(SAMPLES.keys()))
    if SAMPLES[choice] and st.session_state.get("_last_sample") != choice:
        st.session_state["article_text"] = SAMPLES[choice]
        st.session_state["_last_sample"] = choice
        st.rerun()

    title_in = st.text_input("📰 Headline (optional)",
                             placeholder="e.g. City approves new water budget")
    st.text_area("📄 Article Text", height=260,
                 placeholder="Paste the full article text here...",
                 key="article_text")
    article_text = st.session_state["article_text"]

    st.markdown("<span class='lbl'>02 / ANALYZE</span>", unsafe_allow_html=True)
    go_btn = st.button("🔍 Check Credibility", type="primary",
                       use_container_width=True)
    if st.button("↺ Clear & Start New", use_container_width=True):
        st.session_state["article_text"] = ""
        st.session_state.pop("last_report", None)
        st.session_state.pop("fetched_title", None)
        st.session_state.pop("_last_sample", None)
        st.rerun()

with col_out:
    st.markdown("<span class='lbl'>03 / REVIEW RESULTS</span>",
                unsafe_allow_html=True)

    if go_btn:
        if not api_key:
            st.error("⚠️ Please add your Gemini API key in the sidebar first.")
        elif not article_text or len(article_text.split()) < 20:
            st.error("⚠️ Please paste at least a few sentences of article text.")
        else:
            try:
                with st.spinner("🤖 AI is analyzing the article..."):
                    report = analyze(api_key, article_text[:5000], title_in)
                st.session_state["last_report"] = report
                st.session_state["last_title"]  = title_in or "Untitled"
                st.session_state["history"].append({
                    "title": title_in or "Untitled",
                    "score": report["credibility_score"]
                })
                st.rerun()
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

    report = st.session_state.get("last_report")
    if report:
        score   = report["credibility_score"]
        verdict = report["verdict"]
        color   = "#2A6F4D" if score>=70 else "#B45309" if score>=40 else "#9B2C2C"
        emoji   = "✅" if score>=70 else "⚠️" if score>=40 else "❌"

        # Gauge
        angle = (score - 50) * 1.8
        st.markdown(f"""
        <div style="text-align:center;">
        <svg width="220" height="125" viewBox="0 0 200 115">
          <path d="M10,100 A90,90 0 0,1 72,14" stroke="#F4E1E1" stroke-width="14" fill="none" stroke-linecap="round"/>
          <path d="M72,14 A90,90 0 0,1 153,27" stroke="#F6E8D6" stroke-width="14" fill="none" stroke-linecap="round"/>
          <path d="M153,27 A90,90 0 0,1 190,100" stroke="#DEEBE3" stroke-width="14" fill="none" stroke-linecap="round"/>
          <g style="transform:rotate({angle}deg);transform-origin:100px 100px">
            <line x1="100" y1="100" x2="100" y2="26" stroke="{color}" stroke-width="3.5" stroke-linecap="round"/>
          </g>
          <circle cx="100" cy="100" r="6" fill="{color}"/>
        </svg>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1.6rem;font-weight:700;color:{color};margin-top:-.5rem;">{score}/100</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin:.6rem 0 1rem;">
          <span class="verdict-tag" style="background:{color};">{emoji} {verdict}</span>
          <div style="font-size:.82rem;color:#5b6472;margin-top:.4rem;">Model confidence: {report.get('confidence','Moderate')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div class='card'><b>📝 Summary</b><br><br>{report['summary']}</div>",
                    unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            st.markdown("**🚩 Red Flags**")
            if report["red_flags"]:
                for f in report["red_flags"]:
                    st.markdown(f"<span class='flag-r'>⚠ {f}</span>",
                                unsafe_allow_html=True)
            else:
                st.markdown("<span class='muted'>None identified.</span>",
                            unsafe_allow_html=True)
        with fc2:
            st.markdown("**✅ Green Flags**")
            if report["green_flags"]:
                for f in report["green_flags"]:
                    st.markdown(f"<span class='flag-g'>✓ {f}</span>",
                                unsafe_allow_html=True)
            else:
                st.markdown("<span class='muted'>None identified.</span>",
                            unsafe_allow_html=True)

        with st.expander("💡 Why this score + Claims to verify yourself"):
            st.markdown(report.get("reasoning",""))
            if report["key_claims_to_verify"]:
                st.markdown("**Cross-check these claims:**")
                for c in report["key_claims_to_verify"]:
                    st.markdown(f"- {c}")

        pdf_bytes = build_pdf(st.session_state.get("last_title",""), report)
        st.download_button("⬇️ Download PDF Report", data=pdf_bytes,
                           file_name="truthlens_report.pdf",
                           mime="application/pdf",
                           use_container_width=True)

        st.caption("⚠️ This is a critical-thinking aid, not a verified fact-check. "
                   "Always cross-check important claims with trusted sources.")
    else:
        st.info("👈 Paste an article on the left and click **Check Credibility** to begin.")
