import streamlit as st
import json
import re

# Imports spécifiques (llm et selenium)
from llm import get_auth_context, LLMChat, ConfigLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# =====================================================================
# 🛠️ Configuration du Dashboard
# =====================================================================
st.set_page_config(
    page_title="Executive Threat Intel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #212529; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1a1a1a; }
    .main-title { font-weight: 800; margin-bottom: 0px; font-size: 2.5rem; }
    .sub-title { color: #6c757d; font-size: 1.2rem; margin-bottom: 2rem; }
    .metric-card { background-color: white; border-radius: 6px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .streamlit-expanderHeader { font-weight: 600; font-size: 1.1rem; color: #0d6efd; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 📡 1. Récupération des Données
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
# ⚙️ 2. Parsing Robuste (Python Natif, 0% IA)
# =====================================================================
def parse_markdown_subjects(content):
    """ Extrait nativement les sujets sans faire appel à l'IA pour garantir 100% de fiabilité """
    subjects = []
    # On découpe le document par les balises d'incident que tu utilises
    sections = re.split(r'## Titre de l\'incident :', content)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines: continue
        
        # Le titre est la première ligne
        preview = lines[0].strip()
        
        # On attrape le paragraphe Overview
        overview_match = re.search(r'\*\*Overview\*\*\n(.*?)(?=\n\*\*|$)', section, re.DOTALL)
        details = overview_match.group(1).strip() if overview_match else "Pas de résumé."
        
        # On attrape le lien dans les footnotes (le caractère étrange avant http)
        link_match = re.search(r'?\s*(https?://[^\s]+)', section)
        link = link_match.group(1).strip() if link_match else ""
        
        subjects.append({"preview": preview, "details": details, "link": link})
        
    return subjects

# =====================================================================
# 🧠 3. IA : Uniquement pour les 3 encarts (LLM Interne)
# =====================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()

@st.cache_data(ttl=86400)
def generate_executive_kpis(content, _auth_context):
    models_to_try = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
    
    system_prompt = """Tu es un expert CTI. Analyse ce rapport technique et génère UNIQUEMENT un JSON avec 3 clés.
    
    EXEMPLE DE RÉPONSE STRICTE :
    {
      "threat_level": "ÉLEVÉ",
      "attack_vectors": "Ex: 0-Day, Distillation IA, Phishing",
      "status": "Ex: Patch Urgent Requis"
    }
    """
    
    for model_id in models_to_try:
        try:
            # On désactive le Reasoning pour ça, c'est trop basique pour nécessiter 2 minutes de réflexion
            chat = LLMChat(model_id=model_id, auth_context=_auth_context, high_reasoning_effort=False, web_search=False)
            chat.messages.append({"type": "plain", "role": "system", "content": system_prompt})
            
            raw_response = chat.say(f"Donne le niveau de menace global pour ce rapport :\n\n{content}")
            
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(raw_response)
        except Exception:
            continue # Si ça plante, on tente le modèle suivant
            
    return {} # Si tout échoue, renvoie un dictionnaire vide

# =====================================================================
# 🖥️ 4. Interface Utilisateur
# =====================================================================
st.markdown('<h1 class="main-title">Executive Threat Intel Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Aperçu quotidien des cybermenaces globales et recommandations stratégiques.</p>', unsafe_allow_html=True)

with st.spinner("📥 Récupération du rapport GitHub en cours..."):
    filename, content = fetch_latest_report()

if not filename:
    st.error(content)
    st.stop()

# Extraction 100% sûre en Python (zéro temps d'attente)
native_subjects = parse_markdown_subjects(content)

with st.spinner("🧠 Évaluation de la criticité globale par l'IA..."):
    auth_ctx = init_llm_auth()
    kpis = generate_executive_kpis(content, auth_ctx) or {}

# --- AFFICHER LES KPI (IA) ---
tl_val = str(kpis.get("threat_level", "À ÉVALUER")).upper()
tl_color = "#dc3545" if any(x in tl_val for x in ["ÉLEVÉ", "ELEVE", "CRITIQUE", "HIGH"]) else ("#ffc107" if "MOD" in tl_val else "#28a745")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid {tl_color};">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Niveau de Menace</h4>
        <h2 style="margin:0; color: {tl_color};">{tl_val}</h2>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid #343a40;">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Vecteurs Principaux</h4>
        <h2 style="margin:0; color: #343a40; font-size: 1.5rem; padding-top: 5px;">{kpis.get('attack_vectors', '-')}</h2>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 5px solid #0d6efd;">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Statut / Recommandation</h4>
        <h2 style="margin:0; color: #0d6efd; font-size: 1.5rem; padding-top: 5px;">{kpis.get('status', '-')}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- AFFICHER LES SUJETS (Python Natif) ---
st.markdown("### 📌 Synthèse Stratégique du Jour")

if not native_subjects:
    st.warning("Aucun incident détecté dans le rapport (vérifier le format Markdown).")
else:
    for sub in native_subjects:
        with st.expander(f"🔹 {sub['preview']}"):
            st.write(sub['details'])
            if sub['link']:
                st.markdown(f"[🔗 Consulter la source originale]({sub['link']})")

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
with st.expander("⚙️ Afficher le rapport technique brut complet (Annexe SOC)"):
    st.markdown(content)
