import streamlit as st
import json
import re
import plotly.graph_objects as go
import pandas as pd

from llm import get_auth_context, LLMChat, ConfigLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Executive CTI Dashboard",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS — Executive cleanup & institutional styling
# =============================================================================
st.markdown("""
<style>
    /* --- RESET: Remove Streamlit chrome --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- LAYOUT: Tighten & contain --- */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* --- TYPOGRAPHY --- */
    html, body, [class*="css"] {
        color: #1E2327;
    }
    h1 {
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #1E2327 !important;
        background: linear-gradient(90deg, rgba(0,145,90,0.08) 0%, transparent 80%);
        border-left: 5px solid #00915A;
        padding: 0.5rem 1.5rem;
        margin-bottom: 0.5rem;
        border-radius: 2px;
    }
    h2, h3, h4 {
        font-weight: 600;
        color: #1E2327 !important;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #F4F6F8 !important;
        border-right: 1px solid #E5E7EB;
    }
    [data-testid="stSidebar"] h1 {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        color: #1E2327 !important;
        font-size: 1.1rem !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1E2327 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: #6C757D !important;
        font-size: 0.84rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #E5E7EB !important;
    }
    [data-testid="stSidebar"] .stAlert {
        background: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-left: 4px solid #3B82F6 !important;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] .stAlert p,
    [data-testid="stSidebar"] .stAlert li {
        color: #1E2327 !important; /* Force black text in info boxes */
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 6px 12px !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
        transition: background 0.2s ease;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background-color: #00915A !important;
        box-shadow: 0 2px 5px rgba(0,145,90,0.3) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    /* Hide the default radio circle when selected to make it look like a pure button */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) > div:first-child {
        display: none !important;
    }

    /* --- TABS --- */
    [data-baseweb="tab-list"] {
        border-bottom: 1px solid #E5E7EB !important;
        gap: 2rem !important; /* Increased gap */
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #00915A !important;
        border-bottom: 2px solid #00915A !important;
        font-weight: 600 !important;
    }
    [data-baseweb="tab"] {
        color: #6C757D !important;
        font-size: 1rem !important; /* Increased font size */
        padding-bottom: 0.5rem !important;
    }

    /* --- EXPANDERS (Clickable elements) --- */
    [data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        background-color: #FFFFFF;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        margin-bottom: 0.5rem;
    }
    [data-testid="stExpander"] summary {
        background-color: #F8FAFC !important;
        border-radius: 6px;
        padding: 0.75rem 1rem !important;
        color: #1E2327 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: #ECFDF5 !important;
        color: #00915A !important;
        border-left: 4px solid #00915A !important;
    }

    /* --- METRIC CONTAINERS --- */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    /* --- METADATA BADGES --- */
    .exec-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: normal; /* Allow wrapping if needed */
        line-height: 1.2;
    }
    .badge-region  { background: #DBEAFE; color: #1E3A8A; border: 1px solid #BFDBFE; }
    .badge-infra   { background: #FFEDD5; color: #9A3412; border: 1px solid #FED7AA; }
    .badge-entity  { background: #F3E8FF; color: #5B21B6; border: 1px solid #E9D5FF; }
    .badge-tag     { background: #F3F4F6; color: #1F2937; border: 1px solid #D1D5DB; }

    /* --- CATEGORY BADGES --- */
    .cat-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .cat-ai           { background: #DBEAFE; color: #1E40AF; }
    .cat-cloud        { background: #E0E7FF; color: #3730A3; }
    .cat-ransomware   { background: #FEE2E2; color: #991B1B; }
    .cat-supply-chain { background: #FEF3C7; color: #92400E; }
    .cat-phishing     { background: #EDE9FE; color: #5B21B6; }
    .cat-data-leak    { background: #FCE7F3; color: #9D174D; }
    .cat-digital-asset{ background: #CFFAFE; color: #155E75; }
    .cat-malware      { background: #FEE2E2; color: #7F1D1D; }
    .cat-identity     { background: #D1FAE5; color: #065F46; }
    .cat-default      { background: #F3F4F6; color: #374151; }

    /* --- INCIDENT CARD SECTIONS --- */
    .inc-section {
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        line-height: 1.55;
    }
    .inc-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
        display: block;
    }
    .inc-overview  { background: #F0FDF4; border-left: 3px solid #00915A; }
    .inc-overview  .inc-section-label { color: #065F46; }
    .inc-vector    { background: #FFF7ED; border-left: 3px solid #D97706; }
    .inc-vector    .inc-section-label { color: #92400E; }
    .inc-impact    { background: #FEF2F2; border-left: 3px solid #DC2626; }
    .inc-impact    .inc-section-label { color: #991B1B; }
    .inc-control   { background: #EFF6FF; border-left: 3px solid #2563EB; }
    .inc-control   .inc-section-label { color: #1E3A8A; }
    .inc-meta-bar {
        background: #F9FAFB;
        border: 1px solid #F3F4F6;
        border-radius: 4px;
        padding: 8px 12px;
        margin-bottom: 12px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }

    /* --- LEADERBOARD TABLE --- */
    .exec-leaderboard {
        width: 100%;
        border-collapse: collapse;
    }
    .exec-leaderboard thead tr {
        border-bottom: 2px solid #00915A;
    }
    .exec-leaderboard thead th {
        padding: 8px 14px;
        text-align: left;
        font-size: 0.80rem;
        font-weight: 600;
        color: #6C757D;
        background: transparent;
    }
    .exec-leaderboard tbody tr {
        border-bottom: 1px solid #F3F4F6;
        transition: background 0.12s;
    }
    .exec-leaderboard tbody tr:hover {
        background: #F9FAFB;
    }
    .exec-leaderboard tbody td {
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #1E2327;
        vertical-align: middle;
    }
    .exec-rank {
        font-size: 0.82rem;
        font-weight: 700;
        color: #00915A;
        width: 36px;
        text-align: center;
    }
    .exec-bar-bg {
        background: #F3F4F6;
        border-radius: 2px;
        height: 6px;
        width: 140px;
        display: inline-block;
        vertical-align: middle;
    }
    .exec-bar-fill {
        background: #00915A;
        border-radius: 2px;
        height: 6px;
        display: block;
    }
    .crit-critical { color: #991B1B; font-weight: 600; font-size: 0.72rem; }
    .crit-high     { color: #92400E; font-weight: 600; font-size: 0.72rem; }
    .crit-medium   { color: #065F46; font-weight: 600; font-size: 0.72rem; }
    .crit-low      { color: #6C757D; font-weight: 600; font-size: 0.72rem; }

    /* --- CTI CHAT --- */
    .cti-chat-container {
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        height: 340px;
        overflow-y: auto;
        padding: 12px 16px;
        background: #F9FAFB;
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 8px;
    }
    .cti-msg-user {
        align-self: flex-end;
        background: #00915A;
        color: #fff;
        padding: 8px 14px;
        border-radius: 14px 14px 4px 14px;
        max-width: 78%;
        font-size: 0.85rem;
        line-height: 1.45;
    }
    .cti-msg-bot {
        align-self: flex-start;
        background: #FFFFFF;
        color: #1E2327;
        padding: 8px 14px;
        border-radius: 14px 14px 14px 4px;
        border: 1px solid #E5E7EB;
        max-width: 82%;
        font-size: 0.85rem;
        line-height: 1.45;
    }

    /* --- MOBILE --- */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 1. DATA FETCHING
# =============================================================================
@st.cache_data(ttl=1800)
def fetch_recent_reports(limit=7):
    driver = None
    try:
        chromedriver_path = ConfigLoader.get_chromedriver_path()
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://api.github.com/repos/Thomas-LEON/news-tracker/contents/reports")
        json_text = driver.find_element("tag name", "body").text
        files = json.loads(json_text)
        md_files = [f for f in files if isinstance(f, dict) and f.get('name', '').endswith('.md')]
        if not md_files:
            return [], "No reports found."
        md_files.sort(key=lambda x: x['name'], reverse=True)
        recent_files = md_files[:limit]
        reports_data = []
        for file_info in recent_files:
            driver.get(file_info['download_url'])
            content = driver.find_element("tag name", "body").text
            reports_data.append((file_info['name'], content))
        return reports_data, None
    except Exception as e:
        return [], f"Data sync error: {str(e)}"
    finally:
        if driver:
            driver.quit()


@st.cache_data(ttl=1800)
def fetch_json_db(db_name):
    driver = None
    try:
        chromedriver_path = ConfigLoader.get_chromedriver_path()
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(f"https://raw.githubusercontent.com/Thomas-LEON/news-tracker/main/data/{db_name}")
        json_text = driver.find_element("tag name", "body").text
        return json.loads(json_text)
    except Exception as e:
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", db_name)
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    finally:
        if driver:
            driver.quit()


# =============================================================================
# 2. PARSERS
# =============================================================================
def parse_incidents(content):
    subjects = []
    sections = re.split(r'\n## ', content)
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines:
            continue
        preview = lines[0].strip()
        preview = re.sub(r'(?i)^titre de l\'incident\s*:\s*', '', preview).strip()

        category_match  = re.search(r'\*\*Primary Category:\*\*\s*(.*?)\n', section)
        country_match   = re.search(r'\*\*Impacted Country:\*\*\s*(.*?)\n', section)
        geo_match       = re.search(r'\*\*Geolocation.*?:\*\*\s*(.*?)\n', section)
        companies_match = re.search(r'\*\*List of Companies Impacted:\*\*\s*(.*?)\n', section)
        overview_match  = re.search(r'\*\*Overview\*\*\n(.*?)(?=\n\*\*)', section, re.DOTALL)
        breach_match    = re.search(r'\*\*The Breach Mechanism\*\*\n(.*?)(?=\n\*\*)', section, re.DOTALL)
        impact_match    = re.search(r'\*\*Impact and Consequences\*\*\n(.*?)(?=\n\*\*)', section, re.DOTALL)
        control_match   = re.search(r'\*\*Proposed Control.*?\*\*\n(.*?)(?=\n\*\*|$)', section, re.DOTALL)
        link_match      = re.search(r'(https?://[^\s]+)', section)

        subjects.append({
            "preview":   preview,
            "category":  category_match.group(1).strip() if category_match else "",
            "country":   country_match.group(1).strip() if country_match else "",
            "geo":       geo_match.group(1).strip() if geo_match else "",
            "companies": companies_match.group(1).strip() if companies_match else "",
            "overview":  overview_match.group(1).strip() if overview_match else "",
            "breach":    breach_match.group(1).strip() if breach_match else "",
            "impact":    impact_match.group(1).strip() if impact_match else "",
            "control":   control_match.group(1).strip() if control_match else "",
            "link":      link_match.group(1).strip() if link_match else ""
        })
    return subjects


def extract_threat_score(content):
    match = re.search(r'\*\*Threat Score:\*\*\s*(\d+)', content, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100)
    return 0


# =============================================================================
# 3. AI ENGINE
# =============================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()


def extract_key_recursive(data, target_keys):
    if isinstance(target_keys, str):
        target_keys = [target_keys]
    targets = [str(k).lower() for k in target_keys]
    if isinstance(data, dict):
        for k, v in data.items():
            if str(k).lower() in targets:
                return v
        for v in data.values():
            res = extract_key_recursive(v, target_keys)
            if res is not None:
                return res
    elif isinstance(data, list):
        for item in data:
            res = extract_key_recursive(item, target_keys)
            if res is not None:
                return res
    return None


@st.cache_data(ttl=86400)
def generate_executive_brief(condensed_text, report_date, _auth_context):
    models_to_try = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
    debug_logs = []
    for model_id in models_to_try:
        log_entry = {"model": model_id, "raw_response": "", "error": None, "stage": "Init"}
        try:
            log_entry["stage"] = "1. API Call"
            chat = LLMChat(model_id=model_id, auth_context=_auth_context, high_reasoning_effort=True, web_search=False)
            mega_prompt = f"""You are a senior Cyber Threat Intelligence analyst briefing a Military General or the Board of Directors.
READ the incidents below and WRITE a high-level strategic summary. Focus on Business Units impacted.

ABSOLUTE RULES:
- Write in ENGLISH. Use strictly BUSINESS and MILITARY strategic language.
- YOU MUST USE THE EXACT KEYS AS THE EXAMPLE BELOW. DO NOT RENAME THEM.
- Adopt a "Military General" briefing style: Present the raw facts clearly, then provide a visionary strategic outlook.
- Present the decision clearly, but leave the final decision to the leadership.
- Extract up to 5 critical threat tags (specific CVEs, Threat Actors, Malware names, or MITRE TTPs).

EXAMPLE OF EXACT EXPECTED OUTPUT:
{{
  "bluf": "A critical zero-day vulnerability is actively exploited, requiring immediate patching.",
  "threat_landscape": ["State-sponsored actors are targeting financial institutions."],
  "business_impact": ["Potential loss of sensitive PII leading to regulatory fines."],
  "recommendations": ["Authorize emergency patching protocol vs Passive Monitoring. Leadership decision required."],
  "threat_tags": ["CVE-2026-1234", "LAZARUS GROUP", "RANSOMWARE", "LATERAL MOVEMENT"]
}}

--- INCIDENTS TO ANALYZE FOR {report_date} ---
{condensed_text}
"""
            raw = chat.say(mega_prompt)
            log_entry["raw_response"] = raw
            log_entry["stage"] = "2. JSON Extraction"
            clean_json = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL | re.IGNORECASE)
            clean_json_str = clean_json.group(1) if clean_json else (re.search(r'\{.*\}', raw, re.DOTALL).group(0) if re.search(r'\{.*\}', raw, re.DOTALL) else raw)
            parsed = json.loads(clean_json_str)
            log_entry["stage"] = "3. Validation"
            bluf_val = extract_key_recursive(parsed, ["bluf", "bottom_line_up_front", "bottom_line", "summary", "executive_summary"])
            if bluf_val:
                return {
                    "bluf": bluf_val,
                    "threat_landscape": extract_key_recursive(parsed, ["threat_landscape", "landscape"]) or [],
                    "business_impact": extract_key_recursive(parsed, ["business_impact", "impact"]) or [],
                    "recommendations": extract_key_recursive(parsed, ["recommendations", "actions"]) or [],
                    "threat_tags": extract_key_recursive(parsed, ["threat_tags", "tags"]) or []
                }, debug_logs
            else:
                log_entry["error"] = f"Missing BLUF. Keys: {list(parsed.keys()) if isinstance(parsed, dict) else type(parsed)}"
        except Exception as e:
            log_entry["error"] = f"Exception at [{log_entry['stage']}]: {str(e)}"
        debug_logs.append(log_entry)
    return None, debug_logs


def format_bullets(data_item):
    if isinstance(data_item, list):
        return "\n".join([f"- {item}" for item in data_item])
    return str(data_item)


# =============================================================================
# HELPERS
# =============================================================================
def get_cat_badge_html(category: str) -> str:
    if not category:
        return ""
    cat = category.strip().upper()
    css_map = {
        "AI": "cat-ai", "CLOUD": "cat-cloud",
        "RANSOMWARE": "cat-ransomware", "SUPPLY CHAIN": "cat-supply-chain",
        "PHISHING": "cat-phishing", "DATA LEAK": "cat-data-leak",
        "DIGITAL ASSET": "cat-digital-asset", "MALWARE": "cat-malware",
        "IDENTITY": "cat-identity",
    }
    css_class = css_map.get(cat, "cat-default")
    return f"<span class='cat-badge {css_class}'>{cat}</span>"


def render_incident_card(sub):
    """Structured, color-coded incident card. Data speaks, UI recedes."""
    cat_html  = get_cat_badge_html(sub.get('category', ''))
    country   = sub.get('country', '')   or "Global"
    geo       = sub.get('geo', '')       or "Undisclosed"
    companies = sub.get('companies', '') or "Multiple"

    meta_html = f"<div class='inc-meta-bar'>{cat_html} <span class='exec-badge badge-region'>Region: {country}</span> <span class='exec-badge badge-infra'>Infra: {geo}</span> <span class='exec-badge badge-entity'>Entities: {companies}</span></div>"
    st.markdown(meta_html, unsafe_allow_html=True)

    if sub.get('overview'):
        st.markdown(f"<div class='inc-section inc-overview'><span class='inc-section-label'>Operational Overview</span>\n\n{sub['overview']}\n\n</div>", unsafe_allow_html=True)

    if sub.get('breach'):
        st.markdown(f"<div class='inc-section inc-vector'><span class='inc-section-label'>Attack Vector</span>\n\n{sub['breach']}\n\n</div>", unsafe_allow_html=True)

    if sub.get('impact'):
        st.markdown(f"<div class='inc-section inc-impact'><span class='inc-section-label'>Business Impact</span>\n\n{sub['impact']}\n\n</div>", unsafe_allow_html=True)

    if sub.get('control'):
        st.markdown(f"<div class='inc-section inc-control'><span class='inc-section-label'>Recommended Controls</span>\n\n{sub['control']}\n\n</div>", unsafe_allow_html=True)

    if sub.get('link'):
        st.markdown(f"[View Source Intelligence]({sub['link']})")


# =============================================================================
# 4. INTERFACE
# =============================================================================
with st.spinner("Synchronising intelligence feed..."):
    reports_data, error = fetch_recent_reports(limit=7)

if error or not reports_data:
    st.error(error or "No data available.")
    st.stop()

timeline_data = []
for name, content in reports_data:
    match = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', name)
    date_str = match.group(1).replace("_", "-") if match else name.replace(".md", "")
    day_incidents = parse_incidents(content)
    score = extract_threat_score(content)
    timeline_data.append({"Date": date_str, "Filename": name, "Score": score, "Incidents": len(day_incidents)})

df_timeline = pd.DataFrame(timeline_data)
df_timeline['Date'] = pd.to_datetime(df_timeline['Date'], format='mixed', errors='coerce')
df_timeline = df_timeline.dropna(subset=['Date'])
df_timeline = df_timeline.sort_values(by="Date")
avg_7d_score = df_timeline['Score'].mean()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Intelligence Archive")
    st.caption("Select a date to load the corresponding strategic assessment.")
    report_options = [r['Filename'] for r in timeline_data]
    selected_filename = st.radio("Report date", report_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### CRQ Methodology")
    st.info(
        "**Composite Threat Score (0-100)** — FAIR framework.\n\n"
        "Score = (TC + EF + BI) x 3.33\n\n"
        "- TC: Threat Capability (1-10)\n"
        "- EF: Event Frequency (1-10)\n"
        "- BI: Business Impact (1-10)\n\n"
        "Auditable, deterministic, AI-evaluated from raw intelligence."
    )

# Resolve selected report
selected_row = next(r for r in timeline_data if r['Filename'] == selected_filename)
selected_content = next(content for name, content in reports_data if name == selected_filename)
report_date_clean = selected_filename.replace(".md", "").replace("_", " ")

incidents = parse_incidents(selected_content)
current_score = selected_row['Score']

auditable_metrics = ""
metrics_match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*(.*?)\)\*', selected_content, re.IGNORECASE)
if metrics_match:
    auditable_metrics = metrics_match.group(1).strip()

# --- TABS ---
tab_briefing, tab_controls = st.tabs(["Daily Threat Briefing", "Control Center"])

# =========================================================================
# TAB 1 — DAILY BRIEFING
# =========================================================================
with tab_briefing:
    st.title("Strategic Cyber Threat Briefing")
    st.caption(f"Assessment for **{report_date_clean}**  ·  {len(incidents)} actionable incidents")

    st.markdown("---")

    # --- CHARTS ROW ---
    col_gauge, col_trend = st.columns([1, 2])

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Composite Threat Score", 'font': {'size': 16, 'color': '#1E2327'}},
            delta={'reference': avg_7d_score, 'increasing': {'color': "#DC2626"}, 'decreasing': {'color': "#00915A"}},
            number={'font': {'size': 42, 'color': '#1E2327'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#E5E7EB", 'dtick': 25},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "#FFFFFF",
                'borderwidth': 1,
                'bordercolor': "#E5E7EB",
                'steps': [
                    {'range': [0, 33],  'color': "#D1FAE5"},
                    {'range': [33, 66], 'color': "#FEF3C7"},
                    {'range': [66, 100],'color': "#FEE2E2"}
                ],
                'threshold': {
                    'line': {'color': "#1E2327", 'width': 3},
                    'thickness': 0.75,
                    'value': current_score
                }
            }
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        if auditable_metrics:
            st.caption(auditable_metrics)

    with col_trend:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_timeline['Date'],
            y=df_timeline['Score'],
            mode='lines+markers',
            name='Daily Score',
            line=dict(color='#00915A', width=2),
            marker=dict(size=6, color='#00915A')
        ))
        fig_line.add_trace(go.Scatter(
            x=df_timeline['Date'],
            y=[avg_7d_score] * len(df_timeline),
            mode='lines',
            name='7-Day Baseline',
            line=dict(color='#D1D5DB', width=1.5, dash='dot')
        ))
        fig_line.update_layout(
            title=dict(text="7-Day Trend", font=dict(size=14, color='#1E2327')),
            height=260,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#6C757D', size=11),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=10)),
            yaxis=dict(range=[0, 100], gridcolor='#F3F4F6', zerolinecolor='#F3F4F6', title=''),
            xaxis=dict(gridcolor='#F3F4F6', zerolinecolor='#F3F4F6', title=''),
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("")

    # --- AI BRIEF ---
    condensed_report = ""
    for inc in incidents:
        condensed_report += f"- TITLE: {inc['preview']}\n"
        if inc['country']:
            condensed_report += f"  TARGETS: {inc['country']} / {inc['companies']}\n"
        condensed_report += f"  SUMMARY: {inc['overview']}\n\n"

    with st.spinner(f"Synthesizing executive brief for {report_date_clean}..."):
        auth_ctx = init_llm_auth()
        brief, debug_logs = generate_executive_brief(condensed_report, report_date_clean, auth_ctx)

    if brief and isinstance(brief, dict) and "bluf" in brief:
        with st.container(border=True):
            st.subheader("Bottom Line Up Front")
            st.info(brief.get('bluf', ''))
            tags = brief.get("threat_tags", [])
            if tags:
                tags_html = " ".join([f"<span class='exec-badge badge-tag'>{str(t).upper()}</span>" for t in tags])
                st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("")

        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("#### Threat Landscape")
                st.markdown(format_bullets(brief.get("threat_landscape", "-")))
        with col2:
            with st.container(border=True):
                st.markdown("#### Strategic Impact")
                st.markdown(format_bullets(brief.get("business_impact", "-")))
        with col3:
            with st.container(border=True):
                st.markdown("#### Decision Points")
                st.markdown(format_bullets(brief.get("recommendations", "-")))
    else:
        st.error("AI pipeline did not return a valid brief for this date.")
        if st.button("Retry"):
            generate_executive_brief.clear()
            st.rerun()

    st.markdown("---")

    # --- INTELLIGENCE FEED ---
    st.subheader("Intelligence Feed")
    st.caption("Detailed incident analysis. Expand any item for the full breakdown.")

    st.markdown("")

    if not incidents:
        st.info("No actionable intelligence for this date.")
    else:
        for sub in incidents:
            with st.expander(sub['preview']):
                render_incident_card(sub)


# =========================================================================
# TAB 2 — CONTROL CENTER
# =========================================================================
with tab_controls:
    st.title("Control Center")
    st.caption("Knowledge base mapping mitigation controls to threat incidents.")

    st.markdown("---")

    controls_db  = fetch_json_db("controls_db.json")
    incidents_db = fetch_json_db("incidents_db.json")

    if not controls_db or not incidents_db:
        st.info("Control database is empty or synchronising. It will populate during the next daily scan.")
    else:
        control_counts = {c_id: 0 for c_id in controls_db}
        for inc in incidents_db.values():
            for c_id in inc.get("linked_controls", []):
                if c_id in control_counts:
                    control_counts[c_id] += 1

        sorted_controls = sorted(control_counts.items(), key=lambda x: x[1], reverse=True)

        top_10 = [(c_id, cnt) for c_id, cnt in sorted_controls[:10] if cnt > 0]
        max_count = top_10[0][1] if top_10 else 1

        if top_10:
            st.markdown("**Top Recommended Controls**")
            st.caption("Ranked by frequency across all recorded threat incidents.")

            st.markdown("")

            rows_html = ""
            for rank, (c_id, count) in enumerate(top_10, start=1):
                c_data  = controls_db[c_id]
                name    = c_data.get("name", "Unknown")
                dmg     = c_data.get("damage_level", "").upper()
                dmg_cls = f"crit-{dmg.lower()}" if dmg.lower() in ["critical", "high", "medium", "low"] else "crit-low"
                bar_pct = int((count / max_count) * 100)
                rows_html += f"""<tr>
                    <td class='exec-rank'>{str(rank).zfill(2)}</td>
                    <td><strong>{name}</strong></td>
                    <td>
                        <div class='exec-bar-bg'><div class='exec-bar-fill' style='width:{bar_pct}%'></div></div>
                        <span style='font-size:0.75rem;color:#6C757D;margin-left:8px;'>{count}</span>
                    </td>
                    <td class='{dmg_cls}'>{dmg if dmg else 'N/A'}</td>
                </tr>"""

            st.markdown(f"""<table class='exec-leaderboard'>
                <thead><tr>
                    <th>#</th><th>Control</th><th>Frequency</th><th>Risk</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>""", unsafe_allow_html=True)
        else:
            st.info("No controls linked to incidents yet.")

        st.markdown("---")

        st.subheader("Drill-Down Matrix")
        st.caption("Expand a control to view its prerequisites, CIA impact, and linked incidents.")

        st.markdown("")

        # Wrap the expanders in a scrollable container so it doesn't take up 2000km of vertical space
        with st.container(height=400, border=False):
            for c_id, count in sorted_controls:
                if count == 0:
                    continue
                c_data = controls_db[c_id]
                label = f"{c_data.get('name', 'Unknown')}  —  {count} incident{'s' if count > 1 else ''}"
                with st.expander(label):
                col_info, col_inc = st.columns([1, 1])
                with col_info:
                    st.markdown("**Prerequisites**")
                    for p in c_data.get("prerequisites", []):
                        st.markdown(f"- {p}")
                    st.markdown("")
                    st.markdown("**CIA Impact**")
                    cia = c_data.get("cia_impact", {})
                    st.markdown(
                        f"Confidentiality: `{cia.get('Confidentiality', 'N/A')}`  "
                        f"Integrity: `{cia.get('Integrity', 'N/A')}`  "
                        f"Availability: `{cia.get('Availability', 'N/A')}`"
                    )
                    dmg = c_data.get("damage_level", "N/A")
                    color = "red" if dmg in ["Critical", "High"] else "orange" if dmg == "Medium" else "green"
                    st.markdown(f"Damage Level: :{color}[**{dmg.upper()}**]")

                with col_inc:
                    st.markdown("**Linked Incidents**")
                    linked = [d for d in incidents_db.values() if c_id in d.get("linked_controls", [])]
                    if linked:
                        for inc in linked:
                            st.markdown(f"- **{inc['date']}** — {inc['title']}")
                    else:
                        st.markdown("*No incidents linked.*")


# =========================================================================
# 5. CTI ASSISTANT
# =========================================================================
st.markdown("---")

st.subheader("CTI Assistant")
st.caption("Conversational interface. Queries are answered against the last 7 days of intelligence.")

st.markdown("")

if "messages" not in st.session_state:
    st.session_state.messages = []

chat_html = "<div class='cti-chat-container'>"
if not st.session_state.messages:
    chat_html += "<div class='cti-msg-bot'>Ready. Ask me anything about the threat landscape over the past 7 days.</div>"
for message in st.session_state.messages:
    css_class = "cti-msg-user" if message["role"] == "user" else "cti-msg-bot"
    safe = str(message['content']).replace('<', '&lt;').replace('>', '&gt;')
    
    # Parse basic Markdown (Bold, Italic) and newlines for the HTML chat bubbles
    safe = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', safe)
    safe = re.sub(r'\*(.*?)\*', r'<em>\1</em>', safe)
    safe = safe.replace('\n', '<br>')
    
    chat_html += f"<div class='{css_class}'>{safe}</div>"
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

if cti_prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": cti_prompt})
    with st.spinner("Analysing..."):
        auth_ctx = init_llm_auth()
        ctx = "--- 7-DAY THREAT INTELLIGENCE CONTEXT ---\n"
        for name, content in reports_data:
            ctx += f"\n[REPORT: {name}]\n{content[:2000]}...\n"
        sys_prompt = (
            "You are an elite Cyber Threat Intelligence Assistant. "
            "Answer strictly from the following context. Be concise.\n\n" + ctx
        )
        hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[:-1]])
        full = f"{sys_prompt}\n\n--- HISTORY ---\n{hist}\n\nUSER: {cti_prompt}\nASSISTANT:"
        models = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
        resp = "Unable to reach AI servers."
        for mid in models:
            try:
                resp = LLMChat(model_id=mid, auth_context=auth_ctx, high_reasoning_effort=False, web_search=False).say(full)
                break
            except Exception:
                continue
        st.session_state.messages.append({"role": "assistant", "content": resp})
    st.rerun()
