============================================================
        TRUTHLENS — AI FAKE NEWS DETECTOR FOR STUDENTS
============================================================

Submitted by  : Samrudhee Dattatray Adhav
College       : Aurangabad College of Engineering
Internship    : AI Domain
Submission    : Final Project

------------------------------------------------------------
PROJECT DESCRIPTION
------------------------------------------------------------
TruthLens is an AI-powered web application that helps students
detect fake news and assess the credibility of online articles
before sharing them.

The app analyzes an article's writing style, tone, emotional
language, sourcing, and internal consistency — then gives:
  - A credibility score (0 to 100)
  - A verdict (Likely Reliable / Mixed / Likely Unreliable)
  - A plain-language summary
  - Red flags (suspicious signs)
  - Green flags (trustworthy signs)
  - Claims worth verifying independently
  - A downloadable report

------------------------------------------------------------
TECH STACK
------------------------------------------------------------
  Language    : Python 3
  Framework   : Streamlit
  AI API      : Google Gemini API (gemini-1.5-flash)
  Libraries   : google-generativeai, requests,
                beautifulsoup4, plotly, fpdf2

------------------------------------------------------------
API USED
------------------------------------------------------------
  Google Gemini API
  Free key available at: https://aistudio.google.com/apikey
  No credit card required.

------------------------------------------------------------
HOW TO RUN
------------------------------------------------------------
  Step 1: Install dependencies
          pip install streamlit google-generativeai requests beautifulsoup4 plotly fpdf2

  Step 2: Run the app
          streamlit run app.py

  Step 3: Open browser at http://localhost:8501

  Step 4: Paste your free Gemini API key in the sidebar

  Step 5: Paste any news article and click "Check credibility"

------------------------------------------------------------
PROJECT FEATURES
------------------------------------------------------------
  1. Credibility score (0-100) with visual gauge
  2. AI verdict with confidence level
  3. Red flags & green flags analysis
  4. Plain-language article summary
  5. Claims worth independently verifying
  6. Session history with score trend chart
  7. Downloadable PDF/TXT credibility report
  8. Reset / New article button
  9. Built-in demo samples (reliable vs fake)
 10. Professional light-mode editorial design

------------------------------------------------------------
