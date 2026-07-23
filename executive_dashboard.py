import streamlit as st
import requests
import json
from llm import ConfigLoader  # On réutilise ta propre config !
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
# =====================================================================
# 🛠️ Configuration du Dashboard Executive
# =====================================================================
st.set_page_config(
    page_title="Executive Threat Intel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed" # On cache la sidebar pour un look plus épuré
)

# =====================================================================
# 🎨 Style CSS "Corporate & Clean"
# =====================================================================
st.markdown("""
<style>
    /* Fond très clair et lisible */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Titres avec une police très "Business" */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1a1a1a;
    }
    
    .main-title {
        font-weight: 800;
        margin-bottom: 0px;
        font-size: 2.5rem;
    }
    
    .sub-title {
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Cartes d'indicateurs (KPI) */
    .metric-card {
        background-color: white;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #0d6efd;
    }
    
    /* On cache les logos Streamlit pour faire plus pro */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 📡 Fonction de récupération GitHub (avec cache)
# =====================================================================
REPO_OWNER = "Thomas-LEON"
REPO_NAME = "news-tracker"
REPORTS_PATH = "reports"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{REPORTS_PATH}"

import urllib.request

@st.cache_data(ttl=1800)
def fetch_latest_report():
    driver = None
    try:
        # On utilise exactement ton ChromeDriver configuré dans llm.py
        chromedriver_path = ConfigLoader.get_chromedriver_path()
        
        options = ChromeOptions()
        options.add_argument("--headless") # Mode invisible (la fenêtre ne s'ouvre pas)
        options.add_argument("--disable-extensions")
        
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. Chrome va chercher la liste des fichiers (Chrome passe le proxy tout seul !)
        api_url = "https://api.github.com/repos/Thomas-LEON/news-tracker/contents/reports"
        driver.get(api_url)
        
        # Chrome affiche le JSON brut dans la balise <body>
        json_text = driver.find_element("tag name", "body").text
        files = json.loads(json_text)
        
        # 2. Filtrer les .md et trouver le plus récent
        md_files = [f for f in files if isinstance(f, dict) and f.get('name', '').endswith('.md')]
        if not md_files:
            return None, "Aucun rapport Markdown trouvé dans le repository."
            
        md_files.sort(key=lambda x: x['name'], reverse=True)
        latest_file = md_files[0]
        
        # 3. Chrome va chercher le contenu brut du rapport
        driver.get(latest_file['download_url'])
        content = driver.find_element("tag name", "body").text
        
        return latest_file['name'], content
        
    except Exception as e:
        return None, f"Erreur de synchronisation via Chrome : {str(e)}"
    finally:
        if driver:
            driver.quit() # On ferme Chrome proprement en arrière-plan

# =====================================================================
# 🖥️ Interface Utilisateur (UI)
# =====================================================================

st.markdown('<h1 class="main-title">Executive Threat Intel Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Aperçu quotidien des cybermenaces globales et recommandations stratégiques.</p>', unsafe_allow_html=True)

# Récupération des données
with st.spinner("Synchronisation des données de renseignement en cours..."):
    filename, content = fetch_latest_report()

if not filename:
    st.error(content)
    st.stop()

# --- Section : Executive Summary (Mock) ---
st.markdown(f"**Source de données active :** `{filename}`")

# Ces KPI sont "statiques" pour le moment, c'est ici que l'API LLM viendra briller plus tard
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #dc3545;">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Niveau de Menace Actuel</h4>
        <h2 style="margin:0; color: #dc3545;">ÉLEVÉ</h2>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #ffc107;">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Vecteurs d'Attaque Majeurs</h4>
        <h2 style="margin:0; color: #343a40;">À évaluer</h2>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #0d6efd;">
        <h4 style="margin:0; color: #6c757d; font-size: 0.85rem; text-transform: uppercase;">Statut des Opérations</h4>
        <h2 style="margin:0; color: #0d6efd;">Analyse en cours</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Section : Contenu Brut ---
st.markdown("### 📄 Rapport d'Analyse (Vue Détaillée)")

# On utilise un Expander pour ne pas effrayer les C-Level avec un mur de texte technique
# Ils peuvent le déplier s'ils veulent voir la technique
with st.container():
    st.markdown("""
    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    """, unsafe_allow_html=True)
    
    st.markdown(content) # Affiche le markdown directement depuis Github
    
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# 💡 Vision pour la V2 (LLM Integration)
# =====================================================================
st.divider()
with st.expander("Stratégie pour la V2 (Résumés par IA)"):
    st.info("""
    **Ce que fera le LLM interne dans la V2 :**
    1. Il lira le gros bloc de texte technique ci-dessus en arrière-plan.
    2. Il en déduira dynamiquement le "Niveau de Menace" (Elevé/Modéré/Faible).
    3. Il écrira 3 "Bullet Points" exécutifs spécifiquement pour le board de direction (Impact financier, risques, recommandations).
    4. On injectera ces résultats dans les KPI en haut, et on masquera le texte technique dans un onglet "Annexe".
    """)
