import streamlit as st
import json
import re
import traceback
import plotly.graph_objects as go
import pandas as pd

from llm import get_auth_context, LLMChat, ConfigLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Executive CTI Dashboard",
    page_icon="ðŸ›¡ï¸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- EXECUTIVE BRAND DESIGN SYSTEM ----
# Primary:  #00965E (Brand Green)
# Dark:     #006B44 (Brand Dark Green)
# Text:     #1A1A1A (Near-black institutional)
# Bg:       #F7F8F6 (Off-white)
# -----------------------------------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- EXECUTIVE TYPOGRAPHY --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1A1A1A;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #00965E !important;
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: rgba(255,255,255,0.92) !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.25) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] caption {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stAlert {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 6px;
        padding: 4px 8px;
        margin-bottom: 4px;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] [aria-checked="true"] > div {
        background: rgba(255,255,255,0.28) !important;
        border-radius: 6px;
    }

    /* --- TABS --- */
    [data-baseweb="tab-list"] {
        border-bottom: 2px solid #00965E !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #00965E !important;
        border-bottom: 3px solid #00965E !important;
        font-weight: 700 !important;
    }
    [data-baseweb="tab"] {
        color: #666666 !important;
    }

    /* --- EXEC METADATA BADGES (Region/Infra/Company) --- */
    .exec-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }
    .badge-red    { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
    .badge-blue   { background-color: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    .badge-green  { background-color: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7; }
    .badge-dark   { background-color: #1A1A1A; color: #ffffff; border: 1px solid #333333; }
    .badge-purple { background-color: #F5F3FF; color: #4C1D95; border: 1px solid #DDD6FE; }
    .badge-orange { background-color: #FFF7ED; color: #9A3412; border: 1px solid #FDBA74; }
    .badge-brand    { background-color: #00965E; color: #ffffff; border: 1px solid #006B44; }

    /* --- CATEGORY BADGES (Intelligence Feed) --- */
    .cat-badge {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 3px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 8px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        vertical-align: middle;
    }
    .cat-ai           { background: #0EA5E9; color: #fff; }
    .cat-cloud        { background: #6366F1; color: #fff; }
    .cat-ransomware   { background: #DC2626; color: #fff; }
    .cat-supply-chain { background: #D97706; color: #fff; }
    .cat-phishing     { background: #9333EA; color: #fff; }
    .cat-data-leak    { background: #DB2777; color: #fff; }
    .cat-digital-asset{ background: #0891B2; color: #fff; }
    .cat-malware      { background: #B91C1C; color: #fff; }
    .cat-identity     { background: #065F46; color: #fff; }
    .cat-default      { background: #374151; color: #fff; }

    /* --- LEADERBOARD TABLE (Control Center) --- */
    .exec-leaderboard {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }
    .exec-leaderboard thead tr {
        background: #00965E;
        color: white;
    }
    .exec-leaderboard thead th {
        padding: 10px 14px;
        text-align: left;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .exec-leaderboard tbody tr {
        border-bottom: 1px solid #E5E7EB;
        transition: background 0.15s;
    }
    .exec-leaderboard tbody tr:hover {
        background: #F0FDF4;
    }
    .exec-leaderboard tbody td {
        padding: 11px 14px;
        font-size: 0.88rem;
        color: #1A1A1A;
        vertical-align: middle;
    }
    .exec-rank {
        font-size: 1rem;
        font-weight: 800;
        color: #00965E;
        width: 32px;
        text-align: center;
    }
    .exec-progress-bar-bg {
        background: #E5E7EB;
        border-radius: 3px;
        height: 7px;
        width: 160px;
        display: inline-block;
        vertical-align: middle;
    }
    .exec-progress-bar-fill {
        background: #00965E;
        border-radius: 3px;
        height: 7px;
        display: block;
    }
    .exec-crit-critical { color: #991B1B; font-weight: 700; font-size: 0.75rem; }
    .exec-crit-high     { color: #92400E; font-weight: 700; font-size: 0.75rem; }
    .exec-crit-medium   { color: #065F46; font-weight: 700; font-size: 0.75rem; }
    .exec-crit-low      { color: #374151; font-weight: 700; font-size: 0.75rem; }

    /* --- CTI CHAT BOX --- */
    .cti-chat-container {
        border: 1px solid #D1FAE5;
        border-radius: 10px;
        height: 370px;
        overflow-y: auto;
        padding: 12px 16px;
        background: #F7FFF9;
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 10px;
    }
    .cti-msg-user {
        align-self: flex-end;
        background: #00965E;
        color: white;
        padding: 8px 14px;
        border-radius: 16px 16px 4px 16px;
        max-width: 80%;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .cti-msg-bot {
        align-self: flex-start;
        background: #ffffff;
        color: #1a1a1a;
        padding: 8px 14px;
        border-radius: 16px 16px 16px 4px;
        border: 1px solid #D1FAE5;
        max-width: 85%;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    /* --- MOBILE RESPONSIVE --- */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# ðŸ“¡ 1. DATA FETCHING (7-Day History & JSON DB)
# =====================================================================
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
        # Fallback local
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", db_name)
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    finally:
        if driver:
            driver.quit()

# =====================================================================
# âš™ï¸ 2. NATIVE MARKDOWN PARSER & MATHEMATICAL SCORING
# =====================================================================
def parse_incidents(content):
    subjects = []
    # On dÃ©coupe le document Ã  chaque titre H2 (##)
    sections = re.split(r'\n## ', content)
    
    # Le premier Ã©lÃ©ment (sections[0]) contient l'en-tÃªte principal, on l'ignore.
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines: continue
        
        # La premiÃ¨re ligne devient automatiquement le titre de l'incident (sans le ##)
        preview = lines[0].strip()
        # RÃ©trocompatibilitÃ© : on supprime le prÃ©fixe s'il est prÃ©sent dans les anciens rapports
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
    """
    Extrait le score gÃ©nÃ©rÃ© par l'IA directement depuis le markdown.
    """
    match = re.search(r'\*\*Threat Score:\*\*\s*(\d+)', content, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100) # SÃ©curitÃ© pour bloquer Ã  100 maximum
    return 0 # Si pas de score trouvÃ©, on met 0

# =====================================================================
# ðŸ§  3. AI ENGINE (Qualitative BLUF Only)
# =====================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()

def extract_key_recursive(data, target_keys):
    if isinstance(target_keys, str): target_keys = [target_keys]
    targets = [str(k).lower() for k in target_keys]
    if isinstance(data, dict):
        for k, v in data.items():
            if str(k).lower() in targets: return v
        for v in data.values():
            res = extract_key_recursive(v, target_keys)
            if res is not None: return res
    elif isinstance(data, list):
        for item in data:
            res = extract_key_recursive(item, target_keys)
            if res is not None: return res
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
- Adopt a "Military General" briefing style: Present the raw facts clearly, then provide a visionary strategic outlook (e.g., "AI could become a severe threat to our quantum projects within 6 months"). 
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
                log_entry["error"] = f"Missing BLUF. Keys found: {list(parsed.keys()) if isinstance(parsed, dict) else type(parsed)}"
                
        except Exception as e:
            log_entry["error"] = f"Exception at [{log_entry['stage']}]: {str(e)}"
            
        debug_logs.append(log_entry)
            
    return None, debug_logs

def format_bullets(data_item):
    if isinstance(data_item, list): 
        return "\n".join([f"- {item}" for item in data_item])
    return str(data_item)

# Category badge helper
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

# =====================================================================
# ðŸ–¥ï¸ 4. USER INTERFACE (V9 MATHEMATICAL CRQ + PLOTLY)
# =====================================================================
with st.spinner("Synchronising historical intelligence feed..."):
    reports_data, error = fetch_recent_reports(limit=7)

if error or not reports_data:
    st.error(error or "No data available.")
    st.stop()

# Build timeline data
timeline_data = []
for name, content in reports_data:
    # On sÃ©curise l'extraction de la date via Regex pour ignorer le texte parasite
    match = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', name)
    if match:
        date_str = match.group(1).replace("_", "-")
    else:
        date_str = name.replace(".md", "") # Fallback
        
    day_incidents = parse_incidents(content)
    score = extract_threat_score(content)
    timeline_data.append({"Date": date_str, "Filename": name, "Score": score, "Incidents": len(day_incidents)})

df_timeline = pd.DataFrame(timeline_data)
# L'ajout de errors='coerce' transforme les dates invalides en NaT sans faire planter l'application
df_timeline['Date'] = pd.to_datetime(df_timeline['Date'], format='mixed', errors='coerce')
# On supprime les lignes oÃ¹ la date n'a pas pu Ãªtre parsÃ©e
df_timeline = df_timeline.dropna(subset=['Date'])
df_timeline = df_timeline.sort_values(by="Date") # Sort chronologically for the chart
avg_7d_score = df_timeline['Score'].mean()

# --- SIDEBAR: HISTORY SELECTION ONLY ---
with st.sidebar:
    st.title("ðŸ“… Intelligence Archive")
    st.caption("Select a date to view the strategic assessment.")
    report_options = [r['Filename'] for r in timeline_data]
    selected_filename = st.radio("Past 7 Days", report_options, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### ðŸ§® CRQ Methodology (FAIR)")
    st.info("The **Composite Threat Score (0-100)** is calculated using a deterministic mathematical model based on the FAIR framework:\n\n"
            "**Score = (TC + EF + BI) Ã— 3.33**\n\n"
            "- **TC** (Threat Capability): Attacker sophistication (1-10)\n"
            "- **EF** (Event Frequency): Probability of attack (1-10)\n"
            "- **BI** (Business Impact): Potential financial/systemic impact (1-10)\n\n"
            "*Note: The AI strictly evaluates these 3 vectors based on the raw intel, ensuring an auditable and transparent final score.*")

# Get the content for the selected date
selected_row = next(r for r in timeline_data if r['Filename'] == selected_filename)
selected_content = next(content for name, content in reports_data if name == selected_filename)
report_date_clean = selected_filename.replace(".md", "").replace("_", " ")

incidents = parse_incidents(selected_content)
current_score = selected_row['Score']

# Extraction des mÃ©triques FAIR pour les afficher sous le score si elles existent
auditable_metrics = ""
metrics_match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*(.*?)\)\*', selected_content, re.IGNORECASE)
if metrics_match:
    auditable_metrics = metrics_match.group(1).strip()

tab_briefing, tab_controls = st.tabs(["ðŸ“… Daily Threat Briefing", "ðŸ›¡ï¸ Control Center & Knowledge Base"])

with tab_briefing:
    st.title("Strategic Cyber Threat Briefing")
    st.caption(f"Executive assessment for **{report_date_clean}** | {len(incidents)} actionable incidents analyzed")
    st.divider()

    # --- DATAVIZ ROW (PLOTLY) ---
    col_gauge, col_trend = st.columns([1, 2])

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Composite Threat Score", 'font': {'size': 20}},
            delta = {'reference': avg_7d_score, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': "#00915A"},
                    {'range': [33, 66], 'color': "#ff9800"},
                    {'range': [66, 100], 'color': "#e53935"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': current_score
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        if auditable_metrics:
            st.markdown(f"<div style='text-align: center; font-size: 0.85rem; color: #666; margin-top: -15px;'><i>{auditable_metrics}</i></div>", unsafe_allow_html=True)

    with col_trend:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_timeline['Date'], 
            y=df_timeline['Score'],
            mode='lines+markers',
            name='Daily Score',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=df_timeline['Date'], 
            y=[avg_7d_score]*len(df_timeline),
            mode='lines',
            name='7-Day Baseline',
            line=dict(color='gray', width=2, dash='dash')
        ))
        fig_line.update_layout(
            title="7-Day Historical Threat Baseline",
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis_title="",
            yaxis_title="Threat Score",
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig_line, use_container_width=True)


    # AI Generation
    condensed_report = ""
    for inc in incidents:
        condensed_report += f"- TITLE: {inc['preview']}\n"
        if inc['country']: condensed_report += f"  TARGETS: {inc['country']} / {inc['companies']}\n"
        condensed_report += f"  SUMMARY: {inc['overview']}\n\n"

    with st.spinner(f"ðŸ§  Synthesizing executive brief for {report_date_clean}..."):
        auth_ctx = init_llm_auth()
        brief, debug_logs = generate_executive_brief(condensed_report, report_date_clean, auth_ctx)

    # --- THE BLUF & PILLARS ---
    if brief and isinstance(brief, dict) and "bluf" in brief:
        
        with st.container(border=True):
            st.subheader("Bottom Line Up Front (BLUF)")
            st.info(brief.get('bluf', ''))
            
            # Affichage des Threat Tags FaÃ§on Feedly
            tags = brief.get("threat_tags", [])
            if tags:
                tags_html = " ".join([f"<span class='exec-badge badge-dark'>ðŸ·ï¸ {str(t).upper()}</span>" for t in tags])
                st.markdown(tags_html, unsafe_allow_html=True)
        
        st.write("")
        
        # Rendre les colonnes responsives nativement sur mobile
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.markdown("#### ðŸŒ Threat Landscape")
                st.markdown(format_bullets(brief.get("threat_landscape", "â€”")))
        with col2:
            with st.container(border=True):
                st.markdown("#### ðŸ“‰ Strategic Vision & Impact")
                st.markdown(format_bullets(brief.get("business_impact", "â€”")))
        with col3:
            with st.container(border=True):
                st.markdown("#### ðŸ›¡ï¸ Decision Points")
                st.markdown(format_bullets(brief.get("recommendations", "â€”")))

    else:
        st.error("ðŸš¨ The AI pipeline failed for this specific date.")
        if st.button("ðŸ”„ Retry Generation"):
            generate_executive_brief.clear()
            st.rerun()

    # --- TECHNICAL APPENDIX (FEEDLY UX) ---
    st.write("")
    st.subheader("ðŸ“‹ Intelligence Feed (Incident Deep Dive)")

    if not incidents:
        st.info("No actionable intelligence detected for this date.")
    else:
        for sub in incidents:
            cat_html = get_cat_badge_html(sub.get('category', ''))
            label = f"{sub['preview']}"
            with st.expander(f"ðŸ“° {sub['preview']}"):
                if sub.get('category'):
                    st.markdown(cat_html, unsafe_allow_html=True)

                country   = sub.get('country', '') or "Global/Unknown"
                geo       = sub.get('geo', '') or "Unknown"
                companies = sub.get('companies', '') or "Multiple/Unknown"

                st.markdown(f"""
                    <span class='exec-badge badge-blue'>ðŸŒ REGION: {country}</span>
                    <span class='exec-badge badge-orange'>ðŸ“¡ INFRA: {geo}</span>
                    <span class='exec-badge badge-purple'>ðŸ¢ COMPANY: {companies}</span>
                """, unsafe_allow_html=True)

                st.divider()

                if sub['overview']:
                    st.markdown("##### ðŸ” Operational Overview")
                    st.write(sub['overview'])
                if sub['breach']:
                    st.markdown("##### âš™ï¸ Technical Vector")
                    st.write(sub['breach'])
                if sub['impact']:
                    st.markdown("##### ðŸ’¥ Consequences")
                    st.write(sub['impact'])
                if sub['control']:
                    st.markdown("##### ðŸ›¡ï¸ Mitigation Options")
                    st.write(sub['control'])

                if sub['link']:
                    st.markdown(f"\n[ðŸ”— Go to Original Intel Source]({sub['link']})")

with tab_controls:
    st.title("ðŸ›¡ï¸ Strategic Control Center")
    st.caption("Central Knowledge Base mapping generated mitigation controls to real-world threat incidents.")
    
    controls_db = fetch_json_db("controls_db.json")
    incidents_db = fetch_json_db("incidents_db.json")
    
    if not controls_db or not incidents_db:
        st.info("ðŸ”„ The Control Database is currently empty or synchronizing from GitHub. It will populate automatically during the next daily threat scan.")
    else:
        # Calculate occurrences
        control_counts = {c_id: 0 for c_id in controls_db}
        for inc in incidents_db.values():
            for c_id in inc.get("linked_controls", []):
                if c_id in control_counts:
                    control_counts[c_id] += 1
                    
        # Sort top controls
        sorted_controls = sorted(control_counts.items(), key=lambda x: x[1], reverse=True)
        
        # --- LEADERBOARD (Top 10 Controls) ---
        top_10 = [(c_id, cnt) for c_id, cnt in sorted_controls[:10] if cnt > 0]
        max_count = top_10[0][1] if top_10 else 1

        if top_10:
            st.markdown("<p style='font-size:0.8rem;color:#666;margin-bottom:6px;'>Top recommended security controls ranked by number of threat incidents requiring their implementation.</p>", unsafe_allow_html=True)
            rows_html = ""
            for rank, (c_id, count) in enumerate(top_10, start=1):
                c_data = controls_db[c_id]
                name = c_data.get("name", "Unknown Control")
                dmg = c_data.get("damage_level", "").upper()
                dmg_class = f"exec-crit-{dmg.lower()}" if dmg.lower() in ["critical","high","medium","low"] else "exec-crit-low"
                bar_pct = int((count / max_count) * 100)
                medal = {1: "ðŸ¥‡", 2: "ðŸ¥ˆ", 3: "ðŸ¥‰"}.get(rank, str(rank))
                rows_html += f"""
                <tr>
                    <td class='exec-rank'>{medal}</td>
                    <td><strong>{name}</strong></td>
                    <td>
                        <div class='exec-progress-bar-bg'>
                            <div class='exec-progress-bar-fill' style='width:{bar_pct}%'></div>
                        </div>
                        <span style='font-size:0.8rem;color:#555;margin-left:8px;'>{count} incident{'s' if count > 1 else ''}</span>
                    </td>
                    <td class='{dmg_class}'>{dmg if dmg else 'N/A'}</td>
                </tr>"""
            leaderboard_html = f"""
            <table class='exec-leaderboard'>
                <thead><tr>
                    <th>#</th>
                    <th>Control</th>
                    <th>Frequency</th>
                    <th>Risk Level</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>"""
            st.markdown(leaderboard_html, unsafe_allow_html=True)
        else:
            st.info("No controls have been linked to incidents yet.")
            
        st.divider()
        st.subheader("ðŸ“š Drill-Down Matrix")
        
        # Display each control in an expander
        for c_id, count in sorted_controls:
            if count == 0: continue
            
            c_data = controls_db[c_id]
            with st.expander(f"ðŸ›¡ï¸ {c_data.get('name', 'Unknown')} (Recommended {count} times)"):
                col_info, col_inc = st.columns([1, 1])
                
                with col_info:
                    st.markdown("##### ðŸŽ¯ Prerequisites")
                    for p in c_data.get("prerequisites", []):
                        st.markdown(f"- {p}")
                    
                    st.markdown("##### ðŸ’¥ CIA Impact Matrix")
                    cia = c_data.get("cia_impact", {})
                    st.markdown(f"**Confidentiality:** `{cia.get('Confidentiality', 'N/A')}` | **Integrity:** `{cia.get('Integrity', 'N/A')}` | **Availability:** `{cia.get('Availability', 'N/A')}`")
                    
                    dmg = c_data.get("damage_level", "N/A")
                    color = "red" if dmg in ["Critical", "High"] else "orange" if dmg == "Medium" else "green"
                    st.markdown(f"**Potential Damage Level:** :{color}[**{dmg.upper()}**]")
                    
                with col_inc:
                    st.markdown("##### ðŸ”— Linked Threat Incidents")
                    # Find incidents that linked this control
                    linked_incs = []
                    for inc_id, inc_data in incidents_db.items():
                        if c_id in inc_data.get("linked_controls", []):
                            linked_incs.append(inc_data)
                    
                    if linked_incs:
                        for inc in linked_incs:
                            st.markdown(f"- **{inc['date']}**: {inc['title']}")
                    else:
                        st.markdown("*No specific incidents linked in history.*")

# =====================================================================
# ðŸ¤– 5. CTI-BOT â€” Conversational Box (Main Body, Fixed Height)
# =====================================================================
st.write("")
st.subheader("ðŸ’¬ Ask CTI-Bot")
st.caption("Chat with the AI about the last 7 days of threat intelligence. The bot cross-references all available daily reports to answer your questions.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Build scrollable chat history as HTML (fixed-height, no infinite growth)
chat_html = "<div class='cti-chat-container' id='cti-chat-scroll'>"
if not st.session_state.messages:
    chat_html += "<div class='cti-msg-bot'>ðŸ‘‹ Hello! Ask me anything about the threat landscape over the past 7 days.</div>"
for message in st.session_state.messages:
    css_class = "cti-msg-user" if message["role"] == "user" else "cti-msg-bot"
    safe_content = str(message['content']).replace('<', '&lt;').replace('>', '&gt;')
    chat_html += f"<div class='{css_class}'>{safe_content}</div>"
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

if cti_prompt := st.chat_input("Ask a question (e.g. 'Which incidents target Azure?')"):
    st.session_state.messages.append({"role": "user", "content": cti_prompt})
    with st.spinner("Analyzing 7-day threat data..."):
        auth_ctx = init_llm_auth()
        context_block = "--- 7-DAY THREAT INTELLIGENCE CONTEXT ---\n"
        for name, content in reports_data:
            context_block += f"\n[REPORT: {name}]\n{content[:2000]}...\n"
        system_instruction = f"You are an elite Cyber Threat Intelligence Assistant. Answer the user's questions strictly based on the following 7-day threat intelligence context. Be concise and precise.\n\n{context_block}"
        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[:-1]])
        full_prompt = f"{system_instruction}\n\n--- CHAT HISTORY ---\n{history_text}\n\nUSER: {cti_prompt}\nASSISTANT:"
        models_to_try = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
        response_text = "Sorry, unable to reach the AI servers at the moment."
        for model_id in models_to_try:
            try:
                chat_model = LLMChat(model_id=model_id, auth_context=auth_ctx, high_reasoning_effort=False, web_search=False)
                response_text = chat_model.say(full_prompt)
                break
            except Exception:
                continue
        st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# --- TECHNICAL APPENDIX (FEEDLY UX) ---
st.write("")
st.subheader("ðŸ“‹ Intelligence Feed (Incident Deep Dive)")

if not incidents:
    st.info("No actionable intelligence detected for this date.")
else:
    for sub in incidents:
        cat_html = get_cat_badge_html(sub.get('category', ''))
        with st.expander(f"ðŸ“° {sub['preview']}"):
            if sub.get('category'):
                st.markdown(cat_html, unsafe_allow_html=True)


            country   = sub.get('country', '') or "Global/Unknown"
            geo       = sub.get('geo', '') or "Unknown"
            companies = sub.get('companies', '') or "Multiple/Unknown"

            st.markdown(f"""
                <span class='exec-badge badge-blue'>ðŸŒ REGION: {country}</span>
                <span class='exec-badge badge-orange'>ðŸ“¡ INFRA: {geo}</span>
                <span class='exec-badge badge-purple'>ðŸ¢ COMPANY: {companies}</span>
            """, unsafe_allow_html=True)

            st.divider()

            if sub['overview']:
                st.markdown("##### ðŸ” Operational Overview")
                st.write(sub['overview'])
            if sub['breach']:
                st.markdown("##### âš™ï¸ Technical Vector")
                st.write(sub['breach'])
            if sub['impact']:
                st.markdown("##### ðŸ’¥ Consequences")
                st.write(sub['impact'])
            if sub['control']:
                st.markdown("##### ðŸ›¡ï¸ Mitigation Options")
                st.write(sub['control'])

            if sub['link']:
                st.markdown(f"\n[ðŸ”— Go to Original Intel Source]({sub['link']})")

