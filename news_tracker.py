import os
import datetime
import feedparser
import re
from google import genai
from google.genai import types
from bs4 import BeautifulSoup
import httpx
import certifi

# --- CONFIGURATION ---
# Remplacez "VOTRE_CLE_API" par votre véritable clé API Google Gemini (AI Studio).
# Il est recommandé de la définir dans les variables d'environnement Windows.
API_KEY = os.environ.get("GEMINI_API_KEY", "VOTRE_CLE_API")

# Liste des flux RSS (Sources cyber & Tech)
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.cyberscoop.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.securityweek.com/feed/",
    "https://www.infosecurity-magazine.com/rss/news/",
    "https://techcrunch.com/category/security/feed/",
    "https://feeds.arstechnica.com/arstechnica/security"
]
# ---------------------

def fetch_recent_news():
    """Récupère les articles publiés dans les dernières 24h via les flux RSS."""
    recent_articles = []
    now = datetime.datetime.now(datetime.timezone.utc)
    yesterday = now - datetime.timedelta(days=1)
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                    if published > yesterday:
                        recent_articles.append({
                            "title": entry.title,
                            "link": entry.link,
                            "summary": entry.get('summary', ''),
                            "source": feed.feed.get('title', feed_url)
                        })
        except Exception as e:
            print(f"Erreur lors de la lecture du flux {feed_url}: {e}")
            
    return recent_articles

def get_previously_covered_incidents(days=3):
    """Recupere les titres des incidents traites dans les rapports des N derniers jours."""
    covered = []
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    if not os.path.exists(output_dir):
        return covered
        
    now = datetime.datetime.now()
    for i in range(days + 1):
        target_date = (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        filepath = os.path.join(output_dir, f"Daily_Threat_Intel_{target_date}.md")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                titles = re.findall(r'^## (.*)', content, re.MULTILINE)
                for t in titles:
                    clean_t = t.strip()
                    if clean_t:
                        covered.append(clean_t)
    return list(set(covered))

def generate_executive_summary(articles, covered_incidents=None):
    """Utilise l'IA pour trier les articles et générer un Executive Summary."""
    if not articles:
        return "Aucun incident ou article majeur détecté dans les dernières 24 heures."
    
    try:
        # Configuration pour le nouveau package google.genai
        # Contournement SSL local (Windows/Zscaler/proxy...) : On utilise client_args={'verify': False}
        client = genai.Client(api_key=API_KEY, http_options={'client_args': {'verify': False}})
        
        prompt = """
        Tu es un Strategic Advisor spécialisé en Threat Intelligence (Emerging Tech & AI) rapportant directement au Comex et à la C-Suite (CISO, CIO, CRO, CAIO) d'une institution BANCAIRE d'importance systémique (G-SIB).
        Voici une liste d'articles récupérés aujourd'hui. Ton rôle est d'identifier un TOP 1 à 10 maximum des incidents ou menaces les plus critiques, et de rédiger un rapport détaillé pour CHACUN d'entre eux.
        
        CRITÈRES STRICTS D'INCLUSION (Un article doit valider l'un de ces points stratégiques pour être retenu) :
        1. Impact systémique ou géopolitique Banque : Attaques ciblées contre le secteur financier, espionnage étatique, compromission grave de la Supply Chain logicielle, ou fuites majeures de données réglementées.
        2. Risque fournisseurs & Big Tech (IA / Cloud) : Incidents majeurs touchant les géants du Cloud (AWS, Azure, GCP) ou de l'IA (OpenAI, Anthropic, Hugging Face) UNIQUEMENT s'ils impliquent une rupture de service globale, un empoisonnement de modèle (AI Poisoning), l'évasion d'agents autonomes ou une compromission d'infrastructure cloud.
        3. Infrastructures critiques & Cloud-Native : Failles majeures permettant la compromission matérielle (Data Center, BMC/IPMI), l'évasion de machines virtuelles (VM Escape), ou la prise de contrôle d'hyperviseurs/orchestrateurs.
        4. Décisionnel C-Level : La menace doit nécessiter un arbitrage stratégique, budgétaire, un changement d'architecture majeur, ou l'activation d'une cellule de crise.
        
        CRITÈRES STRICTS D'EXCLUSION (Ignore IMPÉRATIVEMENT ces articles, c'est du bruit opérationnel) :
        1. Hygiène IT et correctifs de routine : Patch Tuesdays, mises à jour massives de sécurité éditeurs (Apple iOS/macOS, Windows, Android, navigateurs web) SAUF si une exploitation active ciblée contre des exécutifs bancaires est avérée.
        2. Failles applicatives ou bibliothèques isolées : Vulnérabilités logicielles (ex: Ruby on Rails, paquets Python/Node mineurs, plugins) se remédiant par une simple mise à jour de dépendance (DevSecOps de routine).
        3. Élévations de privilèges locales (LPE) : Failles noyaux (ex: Linux kernel) ou locales ne permettant pas de sortir d'un conteneur, d'une VM, ou ne touchant pas directement le plan de contrôle Cloud.
        4. Cybercriminalité non-stratégique : Ransomwares classiques sur des acteurs secondaires (PME, hôpitaux), fuites de données e-commerce, campagnes de phishing de masse, piratages de réseaux sociaux.
        5. ACTUALITÉS ANCIENNES : Vérifie bien que l'événement s'est produit récemment. Exclus les résumés mensuels ou les vieilles alertes remontées dans le flux RSS.
        
        Pour CHAQUE incident retenu, tu DOIS IMPÉRATIVEMENT utiliser LA STRUCTURE EXACTE suivante. Sépare chaque incident par une ligne de séparation horizontale (---).
        
        ## Titre de l'incident : Doit INCLURE les noms des acteurs impliqués (ex: OpenAI et HuggingFace) et la date la plus précise possible
        
        **Incident Metadata:**
        - **Impacted Country:** [Pays impacté, ou "Global" / "Unknown"]
        - **Geolocation / Cloud Region:** [Localité précise ou région Cloud impactée, si connue]
        - **List of Companies Impacted:** [Entreprises touchées, si connues]
        
        [Introduction courte de 1 ou 2 phrases adressant le problème. Tu dois EXPLICITEMENT nommer les entreprises impactées et la date précise de l'événement.]
        
        **Overview**
        [Un paragraphe résumant la situation globale de l'incident, en rappelant les acteurs, la date exacte, et les détails d'infrastructure cloud si applicable]
        
        **The Breach Mechanism**
        [Explication contextuelle du mécanisme]
        - [Point 1 : Titre en gras et explication]
        - [Point 2 : Titre en gras et explication]
        - ...
        
        **Impact and Consequences**
        - [Impact 1 : Titre en gras et explication axée sur le risque systémique, d'architecture ou stratégique]
        - [Impact 2 : Titre en gras et explication axée sur le risque systémique, d'architecture ou stratégique]
        - ...
        
        **Proposed Control: Mitigating Threats**
        To address the vulnerabilities exposed by this incident, I propose the implementation of the following control framework:
        - I. Governance & Containment (Prevention): [Action stratégique / directive C-Level]
        - II. Identity & Access Management (Containment): [Action stratégique / directive C-Level]
        - III. Infrastructure Intelligence (Detection): [Action stratégique / directive C-Level]
        - IV. Operational Resilience: [Action stratégique / directive C-Level]
        - V. Simulation environment: [Action stratégique / directive C-Level]
        (Adapte les propositions de contrôles pour qu'elles orientent l'architecture globale et la gouvernance, sans tomber dans les manipulations techniques de bas niveau !)
        
        **Conclusion**
        [Une conclusion courte sur la leçon stratégique à tirer de cet incident pour le Groupe bancaire]
        
        **Further Reading**
        [Lien(s) pertinent(s) additionnel(s) si possible]
        
        **Footnotes**
        [1] [Lien de la source 1]
        [2] [Lien de la source 2]
        
        Rédige l'intégralité du rapport en Anglais. Utilise un ton très professionnel, "Executive", analytique et concis.
        Utilise des footnotes (indices comme ceci : ¹ ²) dans le texte pour lier aux sources de la section Footnotes de chaque incident.
        N'oublie pas de bien séparer chaque incident avec '---'.
        
        Voici les articles bruts :

        """
        
        for i, art in enumerate(articles):
            soup = BeautifulSoup(art['summary'], 'html.parser')
            clean_summary = soup.get_text()[:400]
            prompt += f"\n- Titre: {art['title']}\n  Lien: {art['link']}\n  Source: {art['source']}\n  Extrait: {clean_summary}\n"
            
        if covered_incidents:
            prompt += "\n\nCRITERE D'EXCLUSION ABSOLU (DOUBLONS DEJA TRAITES) :\n"
            prompt += "Les incidents suivants ont DEJA ete traites dans nos rapports des jours precedents. Tu ne DOIS PAS les inclure dans ton rapport d'aujourd'hui (certains flux RSS font remonter de vieux articles). Ignore-les totalement :\n"
            for ci in covered_incidents:
                prompt += f"- {ci}\n"
                
        models_to_try = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
        
        for model_name in models_to_try:
            try:
                print(f"Tentative de generation avec le modele {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                    )
                )
                return response.text
            except Exception as e:
                print(f"Echec avec le modele {model_name}: {e}")
                continue
                
        return "Erreur : Impossible de generer le rapport avec les modeles Gemini disponibles (3.6, 3.5, 3.1-lite)."
        
    except Exception as e:
        return f"Erreur lors de l'appel a l'API IA : {e}\nAvez-vous bien configure la cle d'API GEMINI_API_KEY ?"

def main():
    print("Recherche des actualites (Threat Intel & Cyber) des dernieres 24h...")
    articles = fetch_recent_news()
    print(f"{len(articles)} articles trouves.")
    
    print("Recherche des anciens rapports pour eviter les doublons...")
    covered = get_previously_covered_incidents(days=3)
    
    print("Analyse par l'IA et redaction de l'Executive Summary...")
    report = generate_executive_summary(articles, covered_incidents=covered)
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"Daily_Threat_Intel_{today_str}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🛡️ Daily Threat Intel & Emerging Tech Briefing\n")
        f.write(f"**Date:** {today_str}\n\n")
        f.write(report)
        
    print(f"\nTermine ! Le rapport a ete sauvegarde ici :\n{filename}")

if __name__ == "__main__":
    main()
