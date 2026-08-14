import os
import datetime
import feedparser
import re
import json
import uuid
from google import genai
from google.genai import types
import httpx
from bs4 import BeautifulSoup
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
    "https://feeds.arstechnica.com/arstechnica/security",
    "https://www.helpnetsecurity.com/feed/",
    "https://thecyberwire.com/feeds/rss.xml",
    "https://www.cybersecuritydive.com/feeds/news/"
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
    for i in range(1,days + 1):
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
        - **Primary Category:** [Un seul mot clé principal: AI, CLOUD, RANSOMWARE, SUPPLY CHAIN, DATA LEAK, etc.]
        - **Timeline:** [Event: date la plus précise de l'évenement | Disclosed: Date la plus précise de l'anonce de l'évenement]
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
        To address the vulnerabilities exposed by this incident, the implementation of the following control framework is proposed:
        - **I. Governance & Containment (Prevention):** [Action proposee]
        - **II. Identity & Access Management (Containment):** [Action proposee]
        - **III. Infrastructure Intelligence (Detection):** [Action proposee]
        - **IV. Operational Resilience:** [Action proposee]
        - **V. Simulation environment:** [Action proposee]
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
                
        models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
        
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

def verify_and_correct_report(draft_report, articles):
    """
    Audite le rapport brouillon généré, supprime les incidents hors-sujet (géopolitique, régulation sans incident technique)
    et corrige scrupuleusement les dates des incidents en s'appuyant sur les articles originaux.
    """
    print("\nLancement de l'Audit IA (Double Check)...")
    prompt = f"""Tu es un Auditeur Cyber (Red Team / Fact Checker) extrêmement strict.
On t'a soumis un brouillon de rapport Threat Intel, ainsi que les articles bruts d'origine.
Ton rôle est de corriger les erreurs de l'IA qui a rédigé ce brouillon.

Voici le brouillon :
---
{draft_report}
---

Voici les articles bruts d'origine (pour vérifier les dates et les faits) :
---
"""
    for i, art in enumerate(articles):
        soup = BeautifulSoup(art['summary'], 'html.parser')
        clean_summary = soup.get_text()[:300]
        prompt += f"- Titre: {art['title']}\n  Lien: {art['link']}\n  Date/Source: {art['source']}\n  Extrait: {clean_summary}\n\n"

    prompt += """
TA MISSION :
1. SUPPRESSION DES HORS-SUJETS : Supprime IMPITOYABLEMENT toute section entière du brouillon qui relate un événement purement politique, gouvernemental, ou régulatoire (ex: "Executive Order", "New Bill", etc.) à moins qu'il n'y ait une vraie cyberattaque ou une vulnérabilité critique d'infrastructure mentionnée.
2. VÉRIFICATION DES DATES : L'IA précédente a tendance à inventer ou forcer des dates récentes pour de vieux articles remontés dans le flux RSS. Vérifie dans les articles bruts si la date de l'incident est réellement récente (moins de 7 jours).
  - Si l'incident date de plus d'une semaine (ex: un vieil article d'il y a un an), supprime toute la section.
  - Si la date de l'incident dans le rapport ne correspond pas à la date réelle de l'article, corrige la date dans le rapport (Timeline: Event: ...).
3. Rends UNIQUEMENT le rapport Markdown final corrigé. Conserve le formatage exact (titres ##, puces, structure). Ne rajoute pas d'intro ou de conclusion générale de ta part, donne juste le rapport final (les balises Markdown sont autorisées).
"""

    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
    try:
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False)})
        
        for model_name in models_to_try:
            try:
                print(f"Tentative d'audit avec {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.0)
                )
                
                raw_text = response.text.strip()
                if raw_text.startswith("```markdown"):
                    raw_text = raw_text[11:]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                return raw_text.strip()
            except Exception as e:
                print(f"Echec de l'audit avec {model_name}: {e}")
                continue
                
        return draft_report
    except Exception as e:
        print(f"Erreur globale lors de l'audit : {e}")
        return draft_report

def update_databases(report_content, today_str):
    """
    Lit le rapport généré, en extrait les incidents et les contrôles associés,
    dédoublonne les contrôles avec la base de données existante (via IA),
    et met à jour les fichiers JSON.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    controls_db_path = os.path.join(data_dir, "controls_db.json")
    incidents_db_path = os.path.join(data_dir, "incidents_db.json")
    
    # Load existing DBs
    controls_db = {}
    if os.path.exists(controls_db_path):
        with open(controls_db_path, "r", encoding="utf-8") as f:
            controls_db = json.load(f)
            
    incidents_db = {}
    if os.path.exists(incidents_db_path):
        with open(incidents_db_path, "r", encoding="utf-8") as f:
            incidents_db = json.load(f)
            
    # Build a simplified list of existing controls to send to the LLM
    existing_controls_list = [{"id": k, "name": v["name"]} for k, v in controls_db.items()]
    
    prompt = f"""Tu es un analyste expert en Risk Management.
Voici le rapport quotidien Cyber :
---
{report_content}
---

Voici la liste des contrôles DÉJÀ EXISTANTS dans notre base de données :
{json.dumps(existing_controls_list, indent=2)}

TA TACHE :
1. Isole chaque incident du rapport (chaque section H2 commençant par ##).
2. Pour chaque incident, identifie les "Mitigating Controls" recommandés.
3. Pour chaque contrôle identifié :
   - Regarde s'il correspond SÉMANTIQUEMENT à un contrôle de la base existante. Si oui, réutilise son ID existant.
   - S'il s'agit d'un nouveau contrôle (nouveau concept), crée-lui un ID sous la forme 'CTRL-NOUVEAU-XXXX' (remplace XXXX par 4 chiffres aléatoires).
   - Génère pour ce NOUVEAU contrôle ses attributs : 'name', 'prerequisites' (liste de 3 pré-requis courts), 'cia_impact' (un objet contenant Confidentiality, Integrity, Availability notés Low, Medium, High, ou Critical), et 'damage_level' (Low, Medium, High, ou Critical).

Tu DOIS retourner UNIQUEMENT un objet JSON valide, sans balises Markdown, structuré EXACTEMENT comme ceci :
{{
    "new_controls": {{
        "CTRL-NOUVEAU-1234": {{
            "name": "MFA for Admins",
            "prerequisites": ["IdP deployment", "Hardware tokens", "User training"],
            "cia_impact": {{"Confidentiality": "High", "Integrity": "High", "Availability": "Medium"}},
            "damage_level": "Critical"
        }}
    }},
    "incidents": [
        {{
            "title": "Titre complet de l'incident (celui du rapport)",
            "controls": ["ID-EXISTANT", "CTRL-NOUVEAU-1234"]
        }}
    ]
}}
"""
    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
    try:
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False)})
        
        raw_output = None
        for model_name in models_to_try:
            try:
                print(f"[DB Update] Tentative avec {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.0)
                )
                raw_output = response.text
                break
            except Exception as model_err:
                print(f"[DB Update] Echec avec {model_name}: {model_err}")
                continue
        
        if not raw_output:
            print("[DB Update] Aucun modèle disponible pour la mise à jour des bases JSON.")
            return
        
        # Extraction robuste : on cherche le premier '{' et le dernier '}' dans la réponse,
        # sans dépendre du formatage Markdown (backticks) que l'IA peut oublier.
        start_idx = raw_output.find('{')
        end_idx = raw_output.rfind('}')
        if start_idx == -1 or end_idx == -1:
            print(f"[DB Update] Impossible de trouver un objet JSON dans la réponse IA : {raw_output[:200]}")
            return
        clean_json_str = raw_output[start_idx:end_idx + 1]
        parsed_data = json.loads(clean_json_str)
        
        # Merge new controls
        if "new_controls" in parsed_data:
            for c_id, c_data in parsed_data["new_controls"].items():
                if c_id not in controls_db:
                    controls_db[c_id] = c_data
                    
        # Add incidents
        if "incidents" in parsed_data:
            for inc in parsed_data["incidents"]:
                inc_id = f"INC-{today_str.replace('-','')}-{uuid.uuid4().hex[:6].upper()}"
                incidents_db[inc_id] = {
                    "date": today_str,
                    "title": inc.get("title", "Unknown Incident"),
                    "linked_controls": inc.get("controls", [])
                }
                
        # Save DBs
        with open(controls_db_path, "w", encoding="utf-8") as f:
            json.dump(controls_db, f, indent=4)
        with open(incidents_db_path, "w", encoding="utf-8") as f:
            json.dump(incidents_db, f, indent=4)
            
        print("Base de données JSON (Controls & Incidents) mise à jour avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour des bases JSON : {e}")

def main():
    print("Recherche des actualites (Threat Intel & Cyber) des dernieres 24h...")
    articles = fetch_recent_news()
    if not articles:
        print("Aucun article recent trouve.")
        return
        
    print(f"{len(articles)} articles trouves.")
    
    print("Recherche des anciens rapports pour eviter les doublons...")
    covered = get_previously_covered_incidents(days=3)
    
    print("Analyse par l'IA et redaction de l'Executive Summary (Brouillon)...")
    draft_report = generate_executive_summary(articles, covered_incidents=covered)
    
    final_report = verify_and_correct_report(draft_report, articles)
    
    print("Calcul mathematique et deterministe du score de risque final...")
    match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*Threat Capability:\s*(\d+)/10\s*\|\s*Event Frequency:\s*(\d+)/10\s*\|\s*Business Impact:\s*(\d+)/10\s*\)\*', final_report, re.IGNORECASE)
    
    if match:
        tc = int(match.group(1))
        ef = int(match.group(2))
        bi = int(match.group(3))
        threat_score = int((tc + ef + bi) * 3.33)
        threat_score = min(threat_score, 100) # Cap at 100
        
        # Inject the final Threat Score line just before the Auditable Metrics
        final_report = final_report.replace(match.group(0), f"**Threat Score:** {threat_score}/100\n" + match.group(0))
    else:
        # Fallback if AI fails to format properly
        final_report = "**Threat Score:** 0/100\n" + final_report
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f"Daily_Threat_Intel_{today_str}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🛡️ Daily Threat Intel & Emerging Tech Briefing\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(final_report)
        
    print(f"\nTermine ! Le rapport final a ete sauvegarde ici :\n{filename}")
    
    print("\nMise à jour de la base de connaissances (Contrôles)...")
    update_databases(final_report, today_str)

if __name__ == "__main__":
    main()
