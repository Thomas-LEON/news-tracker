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

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Executive CTI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Petit nettoyage Streamlit de base et CSS Feedly / Mobile Responsive
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Typographie moderne et propre type Feedly */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Design des petits Badges "Super Executive" */
    .exec-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }
    .badge-red    { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a;}
    .badge-blue   { background-color: #e3f2fd; color: #1565c0; border: 1px solid #90caf9;}
    .badge-green  { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7;}
    .badge-dark   { background-color: #37474f; color: #ffffff; border: 1px solid #263238;}
    .badge-purple { background-color: #ede7f6; color: #4527a0; border: 1px solid #b39ddb;}
    .badge-orange { background-color: #fff3e0; color: #e65100; border: 1px solid #ffcc80;}

    /* CTI Chat Box - fixed height, scrollable */
    .cti-chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        height: 370px;
        overflow-y: auto;
        padding: 12px 16px;
        background: #fafafa;
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 10px;
    }
    .cti-msg-user {
        align-self: flex-end;
        background: #1565c0;
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
        border: 1px solid #e0e0e0;
        max-width: 85%;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    /* Responsivité Mobile Ultime */
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
# 📡 1. DATA FETCHING (7-Day History)
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

# =====================================================================
# ⚙️ 2. NATIVE MARKDOWN PARSER & MATHEMATICAL SCORING
# =====================================================================
def parse_incidents(content):
    subjects = []
    # On découpe le document à chaque titre H2 (##)
    sections = re.split(r'\n## ', content)
    
    # Le premier élément (sections[0]) contient l'en-tête principal, on l'ignore.
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines: continue
        
        # La première ligne devient automatiquement le titre de l'incident (sans le ##)
        preview = lines[0].strip()
        # Rétrocompatibilité : on supprime le préfixe s'il est présent dans les anciens rapports
        preview = re.sub(r'(?i)^titre de l\'incident\s*:\s*', '', preview).strip()
        
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
    Extrait le score généré par l'IA directement depuis le markdown.
    """
    match = re.search(r'\*\*Threat Score:\*\*\s*(\d+)', content, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100) # Sécurité pour bloquer à 100 maximum
    return 0 # Si pas de score trouvé, on met 0

# =====================================================================
# 🧠 3. AI ENGINE (Qualitative BLUF Only)
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

# =====================================================================
# 🖥️ 4. USER INTERFACE (V9 MATHEMATICAL CRQ + PLOTLY)
# =====================================================================
with st.spinner("Synchronising historical intelligence feed..."):
    reports_data, error = fetch_recent_reports(limit=7)

if error or not reports_data:
    st.error(error or "No data available.")
    st.stop()

# Build timeline data
timeline_data = []
for name, content in reports_data:
    # On sécurise l'extraction de la date via Regex pour ignorer le texte parasite
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
# On supprime les lignes où la date n'a pas pu être parsée
df_timeline = df_timeline.dropna(subset=['Date'])
df_timeline = df_timeline.sort_values(by="Date") # Sort chronologically for the chart
avg_7d_score = df_timeline['Score'].mean()

# --- SIDEBAR: HISTORY SELECTION ONLY ---
with st.sidebar:
    st.title("📅 Intelligence Archive")
    st.caption("Select a date to view the strategic assessment.")
    report_options = [r['Filename'] for r in timeline_data]
    selected_filename = st.radio("Past 7 Days", report_options, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🧮 CRQ Methodology (FAIR)")
    st.info("The **Composite Threat Score (0-100)** is calculated using a deterministic mathematical model based on the FAIR framework:\n\n"
            "**Score = (TC + EF + BI) × 3.33**\n\n"
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

# Extraction des métriques FAIR pour les afficher sous le score si elles existent
auditable_metrics = ""
metrics_match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*(.*?)\)\*', selected_content, re.IGNORECASE)
if metrics_match:
    auditable_metrics = metrics_match.group(1).strip()

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

with st.spinner(f"🧠 Synthesizing executive brief for {report_date_clean}..."):
    auth_ctx = init_llm_auth()
    brief, debug_logs = generate_executive_brief(condensed_report, report_date_clean, auth_ctx)

# --- THE BLUF & PILLARS ---
if brief and isinstance(brief, dict) and "bluf" in brief:
    
    with st.container(border=True):
        st.subheader("Bottom Line Up Front (BLUF)")
        st.info(brief.get('bluf', ''))
        
        # Affichage des Threat Tags Façon Feedly
        tags = brief.get("threat_tags", [])
        if tags:
            tags_html = " ".join([f"<span class='exec-badge badge-dark'>🏷️ {str(t).upper()}</span>" for t in tags])
            st.markdown(tags_html, unsafe_allow_html=True)
    
    st.write("")
    
    # Rendre les colonnes responsives nativement sur mobile
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("#### 🌍 Threat Landscape")
            st.markdown(format_bullets(brief.get("threat_landscape", "—")))
    with col2:
        with st.container(border=True):
            st.markdown("#### 📉 Strategic Vision & Impact")
            st.markdown(format_bullets(brief.get("business_impact", "—")))
    with col3:
        with st.container(border=True):
            st.markdown("#### 🛡️ Decision Points")
            st.markdown(format_bullets(brief.get("recommendations", "—")))

else:
    st.error("🚨 The AI pipeline failed for this specific date.")
    if st.button("🔄 Retry Generation"):
        generate_executive_brief.clear()
        st.rerun()

# =====================================================================
# 🤖 5. CTI-BOT — Conversational Box (Main Body, Fixed Height)
# =====================================================================
st.write("")
st.subheader("💬 Ask CTI-Bot")
st.caption("Chat with the AI about the last 7 days of threat intelligence. The bot cross-references all available daily reports to answer your questions.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Build scrollable chat history as HTML (fixed-height, no infinite growth)
chat_html = "<div class='cti-chat-container' id='cti-chat-scroll'>"
if not st.session_state.messages:
    chat_html += "<div class='cti-msg-bot'>👋 Hello! Ask me anything about the threat landscape over the past 7 days.</div>"
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
st.subheader("📋 Intelligence Feed (Incident Deep Dive)")

if not incidents:
    st.info("No actionable intelligence detected for this date.")
else:
    for sub in incidents:
        with st.expander(f"📰 {sub['preview']}"):

            country   = sub.get('country', '') or "Global/Unknown"
            geo       = sub.get('geo', '') or "Unknown"
            companies = sub.get('companies', '') or "Multiple/Unknown"

            st.markdown(f"""
                <span class='exec-badge badge-blue'>🌍 REGION: {country}</span>
                <span class='exec-badge badge-orange'>📡 INFRA: {geo}</span>
                <span class='exec-badge badge-purple'>🏢 COMPANY: {companies}</span>
            """, unsafe_allow_html=True)

            st.divider()

            if sub['overview']:
                st.markdown("##### 🔍 Operational Overview")
                st.write(sub['overview'])
            if sub['breach']:
                st.markdown("##### ⚙️ Technical Vector")
                st.write(sub['breach'])
            if sub['impact']:
                st.markdown("##### 💥 Consequences")
                st.write(sub['impact'])
            if sub['control']:
                st.markdown("##### 🛡️ Mitigation Options")
                st.write(sub['control'])

            if sub['link']:
                st.markdown(f"\n[🔗 Go to Original Intel Source]({sub['link']})")
