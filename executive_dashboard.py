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
    
    /* Style pour rendre les titres des Expanders plus "Executive" */
    .streamlit-expanderHeader { font-weight: 600; font-size: 1.1rem; color: #0d6efd; }
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
        
        # Récupération de la liste des fichiers
        driver.get("https://api.github.com/repos/Thomas-LEON/news-tracker/contents/reports")
        json_text = driver.find_element("tag name", "body").text
        files = json.loads(json_text)
        
        md_files = [f for f in files if isinstance(f, dict) and f.get('name', '').endswith('.md')]
        if not md_files:
            return None, "Aucun rapport trouvé."
            
        md_files.sort(key=lambda x: x['name'], reverse=True)
        latest_file = md_files[0]
        
        # Récupération du contenu
        driver.get(latest_file['download_url'])
        content = driver.find_element("tag name", "body").text
        return latest_file['name'], content
    except Exception as e:
        return None, f"Erreur Chrome : {str(e)}"
    finally:
        if driver:
            driver.quit()

 =====================================================================
# 🧠 2. Génération par l'IA (gemma-4-26b)
# =====================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()
@st.cache_data(ttl=86400)
def generate_executive_summary(content, _auth_context):
    chat = LLMChat(
        model_id="gemma-4-26b",
        auth_context=_auth_context,
        high_reasoning_effort=False,
        web_search=False
    )
    
    # Prompt renforcé pour interdire le bavardage
    system_prompt = """Tu es un expert CTI. Analyse le rapport technique et génère UNIQUEMENT un objet JSON valide.
    RÈGLES ABSOLUES :
    - Ne dis pas "Bonjour" ou "Voici le rapport".
    - Ne mets pas de texte en dehors des accolades { et }.
    - Vérifie que toutes les guillemets sont fermées.
    
    Structure attendue :
    {
      "threat_level": "FAIBLE, MODÉRÉ, ÉLEVÉ ou CRITIQUE",
      "attack_vectors": "Ex: Ransomware",
      "status": "Ex: Surveillance renforcée",
      "subjects": [
        {
          "preview": "Phrase d'accroche très courte.",
          "details": "L'explication détaillée.",
          "link": "URL ou vide"
        }
      ]
    }
    """
    chat.messages.append({"type": "plain", "role": "system", "content": system_prompt})
    raw_response = chat.say(f"Voici le rapport brut :\n\n{content}")
    
    # Extraction du JSON et renvoi de la réponse brute pour le debug
    try:
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0)), raw_response
        return json.loads(raw_response), raw_response
    except json.JSONDecodeError:
        return None, raw_response # L'IA a échoué à faire du JSON
# =====================================================================
# 🖥️ 3. Interface Utilisateur
# =====================================================================
st.markdown('<h1 class="main-title">Executive Threat Intel Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Aperçu quotidien des cybermenaces globales et recommandations stratégiques.</p>', unsafe_allow_html=True)
with st.spinner("📥 Synchronisation avec la source de renseignement..."):
    filename, content = fetch_latest_report()
if not filename:
    st.error(content)
    st.stop()
with st.spinner(f"🧠 L'IA (gemma-4-26b) génère l'Executive Summary pour le rapport : {filename}..."):
    auth_ctx = init_llm_auth()
    # On récupère maintenant le summary ET la réponse brute
    summary, raw_response = generate_executive_summary(content, auth_ctx)
# --- SUCCÈS : L'IA a bien fait son JSON ---
if summary:
    tl_color = "#dc3545" if summary["threat_level"].upper() in ["ÉLEVÉ", "CRITIQUE"] else ("#ffc107" if "MOD" in summary["threat_level"].upper() else "#28a745")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {tl_color};">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Niveau de Menace</h4>
            <h2 style="margin:0; color: {tl_color};">{summary.get('threat_level', 'INCONNU')}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #343a40;">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Vecteurs d'Attaque</h4>
            <h2 style="margin:0; color: #343a40; font-size: 1.5rem; padding-top: 5px;">{summary.get('attack_vectors', '-')}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #0d6efd;">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Statut / Recommandation</h4>
            <h2 style="margin:0; color: #0d6efd; font-size: 1.5rem; padding-top: 5px;">{summary.get('status', '-')}</h2>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📌 Synthèse Stratégique du Jour")
    
    subjects = summary.get("subjects", [])
    if not subjects:
        st.info("Aucun sujet stratégique identifié aujourd'hui.")
        
    for sub in subjects:
        with st.expander(f"🔹 {sub.get('preview', 'Sujet non défini')}"):
            st.write(sub.get('details', ''))
            link = sub.get('link', '')
            if link and link.startswith("http"):
                st.markdown(f"[🔗 Consulter la source originale]({link})")
# --- ÉCHEC : Le modèle n'a pas renvoyé de JSON valide ---
else:
    st.error("🚨 L'IA a répondu, mais n'a pas respecté la structure attendue pour remplir le Dashboard.")
    
    # Bouton magique pour réessayer (vide le cache de l'IA et recharge la page)
    if st.button("🔄 Re-générer l'analyse (Réessayer)"):
        generate_executive_summary.clear()
        st.rerun()
        
    # Le panneau Debug pour voir ce que l'IA a vraiment dit
    with st.expander("🛠️ Mode Debug : Voir la réponse brute de l'IA"):
        st.text(raw_response)
# --- 3. ANNEXE TECHNIQUE ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
with st.expander("⚙️ Afficher le rapport technique brut complet (Annexe SOC)"):
    st.markdown(content)
