import streamlit as st
import json
import re

# Imports spécifiques (llm et selenium)
from llm import get_auth_context, LLMChat, ConfigLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# =====================================================================
# 🛠️ Configuration du Dashboard (Design Corporate Neutre)
# =====================================================================
st.set_page_config(
    page_title="Executive Threat Intel",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Palette basée sur le Vert Émeraude corporate sans logo
st.markdown("""
<style>
    .stApp { background-color: #f4f6f8; color: #2D2D2D; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1a1a1a; }
    
    .main-title { font-weight: 800; margin-bottom: 0px; font-size: 2.5rem; color: #00915A; } /* Vert Corporate */
    .sub-title { color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem; font-style: italic; }
    
    /* Boîte pour l'Executive Brief */
    .exec-brief-box {
        background-color: white; 
        border-left: 5px solid #00915A; 
        padding: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        border-radius: 4px; 
        font-size: 1.15rem; 
        line-height: 1.6;
        color: #2D2D2D;
    }
    
    /* Design des Expanders */
    .streamlit-expanderHeader { font-weight: 600; font-size: 1.15rem; color: #2D2D2D; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 📡 1. Récupération des Données (via Chrome Headless)
# =====================================================================
@st.cache_data(ttl=1800)
def fetch_latest_report():
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
            return None, "Aucun rapport trouvé."
            
        md_files.sort(key=lambda x: x['name'], reverse=True)
        latest_file = md_files[0]
        
        driver.get(latest_file['download_url'])
        content = driver.find_element("tag name", "body").text
        return latest_file['name'], content
    except Exception as e:
        return None, f"Erreur Chrome : {str(e)}"
    finally:
        if driver:
            driver.quit()

# =====================================================================
# ⚙️ 2. Parsing Hyper-Détaillé (Python Natif)
# =====================================================================
def parse_markdown_subjects(content):
    """ Extrait toutes les informations clés de tes propres analyses markdown """
    subjects = []
    sections = re.split(r'## Titre de l\'incident :', content)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines: continue
        
        preview = lines[0].strip()
        
        # Extraction des Métadonnées
        country_match = re.search(r'\*\*Impacted Country:\*\*\s*(.*?)\n', section)
        country = country_match.group(1).strip() if country_match else ""
        
        companies_match = re.search(r'\*\*List of Companies Impacted:\*\*\s*(.*?)\n', section)
        companies = companies_match.group(1).strip() if companies_match else ""
        
        overview_match = re.search(r'\*\*Overview\*\*\n(.*?)(?=\n\*\*|$)', section, re.DOTALL)
        overview = overview_match.group(1).strip() if overview_match else ""
        
        control_match = re.search(r'\*\*Proposed Control: Mitigating Threats\*\*\n(.*?)(?=\n\*\*|$)', section, re.DOTALL)
        control = control_match.group(1).strip() if control_match else ""
        
        link_match = re.search(r'(https?://[^\s]+)', section)
        link = link_match.group(1).strip() if link_match else ""
        
        subjects.append({
            "preview": preview,
            "country": country,
            "companies": companies,
            "overview": overview,
            "control": control,
            "link": link
        })
        
    return subjects

# =====================================================================
# 🧠 3. IA : Rédaction de l'Executive Brief (Narratif)
# =====================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()

@st.cache_data(ttl=86400)
def generate_executive_brief(content, _auth_context):
    models_to_try = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
    
    system_prompt = """Tu es un expert CTI rédigeant un "Executive Brief" pour le Comex.
    Rédige UN SEUL paragraphe percutant (max 3 ou 4 phrases) qui résume le paysage des menaces globales du rapport fourni.
    Va droit au but : quels sont les risques majeurs et l'impact potentiel. 
    RÈGLES ABSOLUES :
    - Ne dis pas "Bonjour" ni "Voici le résumé". Commence directement par le contenu.
    - Utilise un ton ultra-professionnel, neutre et stratégique.
    """
    
    for model_id in models_to_try:
        try:
            chat = LLMChat(model_id=model_id, auth_context=_auth_context, high_reasoning_effort=False, web_search=False)
            chat.messages.append({"type": "plain", "role": "system", "content": system_prompt})
            
            raw_response = chat.say(f"Rédige l'Executive Brief pour ce rapport :\n\n{content}")
            # Si on a récupéré une phrase de plus de 20 caractères, c'est bon !
            if raw_response and len(raw_response) > 20:
                return raw_response
        except Exception:
            continue
            
    return "L'intelligence artificielle n'est actuellement pas disponible pour résumer ce rapport."

# =====================================================================
# 🖥️ 4. Interface Utilisateur
# =====================================================================
st.markdown('<h1 class="main-title">Daily Cyber Threat Briefing</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Aperçu stratégique des cybermenaces globales et de leurs impacts sectoriels.</p>', unsafe_allow_html=True)

with st.spinner("📥 Importation des données de renseignement..."):
    filename, content = fetch_latest_report()

if not filename:
    st.error(content)
    st.stop()

native_subjects = parse_markdown_subjects(content)

# --- 1. L'EXECUTIVE BRIEF (Généré par l'IA) ---
with st.spinner("🧠 Rédaction du Brief Stratégique par l'IA..."):
    auth_ctx = init_llm_auth()
    exec_brief = generate_executive_brief(content, auth_ctx)

st.markdown("### 🎯 Executive Summary")
st.markdown(f"<div class='exec-brief-box'>{exec_brief}</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 2. LES DÉTAILS STRATÉGIQUES (Tirés de tes propres analyses) ---
st.markdown("### 📋 Détail des Incidents Majeurs")

if not native_subjects:
    st.warning("Aucun incident détecté dans le format attendu.")
else:
    for sub in native_subjects:
        # L'Expander affiche le gros titre
        with st.expander(f"🚨 {sub['preview']}"):
            
            # Les tags visuels pour les pays et entreprises
            meta_html = "<div style='margin-bottom:15px; color:#6c757d; font-size:0.95rem;'>"
            if sub['country']:
                meta_html += f"🌍 <b>Zone Géographique:</b> {sub['country']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            if sub['companies']:
                meta_html += f"🏢 <b>Cibles / Secteurs:</b> {sub['companies']}"
            meta_html += "</div>"
            st.markdown(meta_html, unsafe_allow_html=True)
            
            # Ton Overview
            st.markdown(f"**Contexte de l'incident :**\n{sub['overview']}")
            
            # Tes recommandations (Proposed Controls)
            if sub['control']:
                st.markdown(f"**🛡️ Contrôles Proposés :**\n{sub['control']}")
                
            # Le lien source
            if sub['link']:
                st.markdown(f"<br>[🔗 Consulter la source de l'incident]({sub['link']})", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
with st.expander("⚙️ Afficher le rapport brut original"):
    st.markdown(content)
