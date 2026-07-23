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

# =====================================================================
# 🧠 2. Génération par l'IA (Avec système de Fallback et Reasoning)
# =====================================================================
@st.cache_resource
def init_llm_auth():
    return get_auth_context()

@st.cache_data(ttl=86400)
def generate_executive_summary(content, _auth_context):
    # L'ordre de priorité : on commence par les plus puissants
    models_to_try = ["gpt-oss-120b", "mistral-medium-3.5-ITG", "gemma-4-26b"]
    
    system_prompt = """Tu es un expert CTI qui rédige des rapports pour le Comex.
    Analyse le rapport technique et génère UNIQUEMENT un objet JSON valide.
    
    RÈGLES ABSOLUES :
    1. Ne dis JAMAIS "Bonjour". Renvoie UNIQUEMENT les accolades JSON { }.
    2. Tu DOIS extraire et lister TOUS les sujets traités dans le rapport. Ne t'arrête pas au premier.
    
    EXEMPLE DE RÉPONSE ATTENDUE :
    {
      "threat_level": "ÉLEVÉ",
      "attack_vectors": "Ransomware, Faille 0-Day",
      "status": "Alerte globale",
      "subjects": [
        {
          "preview": "Vulnérabilité critique Pulse Secure",
          "details": "Faille 0-day permettant l'exécution de code à distance, patch urgent requis.",
          "link": "https://source.com"
        }
      ]
    }
    """
    
    last_raw_response = ""
    
    # --- BOUCLE DE FALLBACK ---
    for model_id in models_to_try:
        try:
            # On instancie le chat avec le modèle en cours et ton idée de "Reasoning"
            chat = LLMChat(
                model_id=model_id,
                auth_context=_auth_context,
                high_reasoning_effort=True, # Donne le temps à l'IA de planifier sa réponse sans couper
                web_search=False
            )
            chat.messages.append({"type": "plain", "role": "system", "content": system_prompt})
            
            # On lance l'inférence
            raw_response = chat.say(f"Synthétise TOUT le rapport suivant en JSON :\n\n{content}")
            last_raw_response = raw_response
            
            # Extraction JSON robuste
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0)), raw_response
            else:
                return json.loads(raw_response), raw_response
                
        except Exception as e:
            # Si le JSON est mal formé ou si l'API coupe au milieu (Token limit)
            # On ignore l'erreur, la boucle continue avec le prochain modèle de la liste !
            print(f"⚠️ Échec avec le modèle {model_id}, passage au suivant... (Erreur: {str(e)})")
            continue
            
    # Si TOUS les modèles ont échoué, on renvoie une erreur propre
    return None, last_raw_response
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
# Si l'IA a bien réussi à générer un JSON (et que c'est bien un dictionnaire)
if summary and isinstance(summary, dict):
    
    # --- 1. SÉCURISATION DU NIVEAU DE MENACE ---
    # On utilise .get() pour ne pas planter si la clé n'existe pas, et on force en majuscules
    tl_val = summary.get("threat_level", summary.get("Niveau de menace", "INCONNU"))
    tl_str = str(tl_val).upper()
    
    if any(x in tl_str for x in ["ÉLEVÉ", "ELEVE", "CRITIQUE", "HIGH"]):
        tl_color = "#dc3545" # Rouge
    elif "MOD" in tl_str:
        tl_color = "#ffc107" # Orange
    else:
        tl_color = "#28a745" # Vert
    
    # --- 2. AFFICHAGE DES KPI ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {tl_color};">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Niveau de Menace</h4>
            <h2 style="margin:0; color: {tl_color};">{tl_str}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        val_vectors = str(summary.get('attack_vectors', summary.get('vecteurs', '-')))
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #343a40;">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Vecteurs d'Attaque</h4>
            <h2 style="margin:0; color: #343a40; font-size: 1.5rem; padding-top: 5px;">{val_vectors}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        val_status = str(summary.get('status', summary.get('statut', '-')))
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #0d6efd;">
            <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Statut / Recommandation</h4>
            <h2 style="margin:0; color: #0d6efd; font-size: 1.5rem; padding-top: 5px;">{val_status}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- 3. LES SUJETS DU JOUR (Expanders) ---
    st.markdown("### 📌 Synthèse Stratégique du Jour")
    
    # On cherche "subjects" ou "sujets" au cas où l'IA a traduit la clé
    subjects = summary.get("subjects", summary.get("sujets", []))
    
    if not subjects or not isinstance(subjects, list):
        st.info("Aucun sujet stratégique identifié aujourd'hui ou format inattendu.")
        with st.expander("🛠️ Mode Debug : Voir la réponse brute"):
            st.json(summary) # Affiche le JSON brut pour comprendre ce que l'IA a fait
            
    else:
        for sub in subjects:
            if isinstance(sub, dict): # Sécurité
                preview = sub.get('preview', sub.get('titre', 'Sujet non défini'))
                details = sub.get('details', sub.get('details', ''))
                link = sub.get('link', sub.get('lien', ''))
                
                with st.expander(f"🔹 {preview}"):
                    st.write(details)
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
