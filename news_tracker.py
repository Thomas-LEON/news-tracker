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
        # Contournement SSL local (Windows/Zscaler/proxy...) : On utilise httpx_client
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False)})
        
        prompt = """
        Tu es un expert en Threat Intelligence et analyste des risques cyber (Emerging Tech & AI) au sein d'une grande institution BANCAIRE.
        Voici une liste d'articles recuperes aujourd'hui. Ton role est d'identifier un TOP 1 a 10 des incidents ou menaces, et de rediger un rapport detaille pour CHACUN d'entre eux.
        
        CRITERES STRICTS D'INCLUSION (Un article doit valider l'un de ces points pour etre retenu) :
        1. Impact direct / indirect Banque : Attaques ciblant le secteur financier, vos fournisseurs (Supply Chain, editeurs logiciels), ou fuites de donnees reglementees (RGPD).
        2. Gros acteurs technologiques : Tout incident (meme sans impact immediat) impliquant les geants du Cloud (AWS, Azure, GCP), les leaders de l'IA (OpenAI, Anthropic, HuggingFace...), les grands du Web (Meta, Apple) ou de la Cyber (CrowdStrike, Palo Alto, etc.).
        3. Infrastructures critiques : Failles majeures touchant des technos d'entreprise classiques (Windows, Linux, reseaux).
        4. Alertes CVE (Failles) : A ne retenir UNIQUEMENT si la faille touche un grand nom de l'IA ou du Cloud.
        
        CRITERES STRICTS D'EXCLUSION (Ignore IMPERATIVEMENT ces articles, c'est du bruit) :
        1. Ransomwares "classiques" touchant des entites non-strategiques (PME, mairies, hopitaux).
        2. Fuites de donnees grand public (sites e-commerce, forums, jeux video).
        3. Campagnes de phishing ou malwares generiques de masse.
        4. Piratages de comptes de reseaux sociaux de celebrites/influenceurs.
        5. ACTUALITES ANCIENNES : Verifie bien que l'evenement s'est produit recemment. Exclut les resumes mensuels, ou les vieilles actualites remontees artificiellement dans le flux RSS.

        --- EVALUATION DU SCORE DE GRAVITE GLOBAL (METHODOLOGIE CRQ / FAIR) ---
        AVANT de lister le premier incident, tu DOIS IMPERATIVEMENT évaluer scientifiquement la gravité globale de la journée (basé sur l'incident le plus critique).
        Ne donne pas un chiffre au hasard. Evalue ces 3 vecteurs stricts de 1 à 10 :
        1. Threat Capability (TC) : Sophistication de l'attaque (1 = Script kiddie, 10 = Nation-State Zero Day indétectable).
        2. Event Frequency (EF) : Probabilité d'attaque sur le secteur BANCAIRE à court terme (1 = Très faible, 10 = Imminente/En cours).
        3. Business Impact (BI) : Impact financier, systémique et réputationnel (1 = Négligeable, 10 = Faillite/Système paralysé).
        
        Laisse le code Python faire le calcul mathématique final. Tu dois juste fournir les notes dans CE FORMAT EXACT pour la première ligne de ton rapport :
        *(Auditable Metrics - Threat Capability: X/10 | Event Frequency: Y/10 | Business Impact: Z/10)*
        
        Ensuite, saute une ligne et commence à lister les incidents.
        
        Pour CHAQUE incident retenu, tu DOIS IMPERATIVEMENT utiliser LA STRUCTURE EXACTE suivante. Separe chaque incident par une ligne de separation horizontale (---).

        ## Titre de l'incident : Doit INCLURE les noms des acteurs impliques (ex: OpenAI et HuggingFace) et la date la plus precise possible

        **Incident Metadata:**
        - **Impacted Country:** [Pays impacte, ou "Global" / "Unknown"]
        - **Geolocation / Cloud Region:** [Localite precise ou region Cloud impactee, si connue]
        - **List of Companies Impacted:** [Entreprises touchees, si connues]

        [Introduction courte de 1 ou 2 phrases adressant le probleme. Tu dois EXPLICITEMENT nommer les entreprises impactees et la date precise de l'evenement.]

        **Overview**
        [Un paragraphe resumant la situation globale de l'incident, en rappelant les acteurs, la date exacte, et les details d'infrastructure cloud si applicable]

        **The Breach Mechanism**
        [Explication contextuelle du mecanisme]
        - [Point 1 : Titre en gras et explication]
        - [Point 2 : Titre en gras et explication]
        - ...

        **Impact and Consequences**
        - [Impact 1 : Titre en gras et explication]
        - [Impact 2 : Titre en gras et explication]
        - ...

        **Proposed Control: Mitigating Threats**
        To address the vulnerabilities exposed by this incident, I propose the implementation of the following control framework:
        - I. Governance & Containment (Prevention): [Action proposee]
        - II. Identity & Access Management (Containment): [Action proposee]
        - III. Infrastructure Intelligence (Detection): [Action proposee]
        - IV. Operational Resilience: [Action proposee]
        - V. Simulation environment: [Action proposee]
        (Adapte les propositions de controles a la nature exacte de la menace !)

        **Conclusion**
        [Une conclusion courte sur la lecon a tirer de cet incident]

        **Further Reading**
        [Lien(s) pertinent(s) additionnel(s) si possible]

        **Footnotes**
        [1. Lien de la source 1]
        [2. Lien de la source 2]
        
        Redige l'integralite du rapport en Anglais. Utilise un ton tres professionnel, "Executive", analytique et concis.
        Utilise des footnotes (indices comme ceci : ¹ ²) dans le texte pour lier aux sources de la section Footnotes de chaque incident.
        N'oublie pas de bien separer chaque incident avec '---'.
        
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
    
    print("Calcul mathematique et deterministe du score de risque final...")
    match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*Threat Capability:\s*(\d+)/10\s*\|\s*Event Frequency:\s*(\d+)/10\s*\|\s*Business Impact:\s*(\d+)/10\s*\)\*', report, re.IGNORECASE)
    
    if match:
        tc = int(match.group(1))
        ef = int(match.group(2))
        bi = int(match.group(3))
        threat_score = int((tc + ef + bi) * 3.33)
        threat_score = min(threat_score, 100) # Cap at 100
        
        # Inject the final Threat Score line just before the Auditable Metrics
        report = report.replace(match.group(0), f"**Threat Score:** {threat_score}/100\n" + match.group(0))
    else:
        # Fallback if AI fails to format properly
        report = "**Threat Score:** 0/100\n" + report
    
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
