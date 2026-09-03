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
import socket
socket.setdefaulttimeout(15.0)

# Remplacez "VOTRE_CLE_API" par votre véritable clé API Google Gemini (AI Studio).
# Il est recommandé de la définir dans les variables d'environnement Windows.
API_KEY = os.environ.get("GEMINI_API_KEY", "VOTRE_CLE_API")

# Format de sortie : "html" (newsletter email) ou "markdown" (ancien format).
# Rollback rapide : mettre OUTPUT_FORMAT=markdown dans le workflow GitHub Actions.
OUTPUT_FORMAT = os.environ.get("OUTPUT_FORMAT", "html").lower()

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
                            "source": feed.feed.get('title', feed_url),
                            "published": published.strftime("%Y-%m-%d %H:%M:%S UTC")
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
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False, timeout=360.0)})
        
        prompt = """
        Tu es un expert en Threat Intelligence et analyste des risques cyber (Emerging Tech & AI) au sein d'une grande institution BANCAIRE.
        Voici une liste d'articles recuperes aujourd'hui. Ton role est d'identifier JUSQU'A 10 incidents ou menaces majeurs.
        Si AUCUN article ne correspond aux critères stricts ci-dessous, ou si tu n'as pas de preuves concrètes dans les articles fournis, tu DOIS IMPÉRATIVEMENT répondre uniquement par le mot "SKIPPED". Ne comble JAMAIS les vides par l'invention.
        
        CRITERES STRICTS D'INCLUSION (Un article doit valider l'un de ces points pour etre retenu) :
        1. Impact direct / indirect Banque : Attaques ciblant le secteur financier, vos fournisseurs (Supply Chain, editeurs logiciels), ou fuites de donnees reglementees (RGPD).
        2. Gros acteurs technologiques : Tout incident impliquant les geants du Cloud (AWS, Azure, GCP) ou de l'IA (OpenAI, Anthropic...).
        3. Infrastructures critiques : Failles majeures touchant des technos d'entreprise classiques.
        
        CRITERES STRICTS D'EXCLUSION (Ignore IMPERATIVEMENT ces articles, c'est du bruit. DROP-LES) :
        1. ZERO HALLUCINATION : Ne génère rien qui ne soit pas explicitement écrit dans l'article. Ne comble pas les trous.
        2. ZERO EXTRAPOLATION : Ne transforme JAMAIS un simple tutoriel de sécurité ou un article de conseil en une campagne d'attaque active. Contente-toi des faits stricts.
        3. IT OUTAGES != CYBER THREAT : Une panne de service (Outage) n'est PAS un incident de sécurité, sauf si elle est explicitement attribuée à une attaque (ex: DDoS, Ransomware).
        4. ACTUALITES ANCIENNES : Si un article parle d'une attaque vieille de plusieurs années SANS nouvel élément, IGNORE. MAIS si c'est une *nouvelle révélation* (Disclosure) d'une ancienne faille (ex: fuite de clés AWS découverte aujourd'hui), tu DOIS la traiter comme un incident pertinent.
        5. Ransomwares "classiques" touchant des PME/hôpitaux, ou fuites grand public (jeux vidéo, influenceurs).

        --- EVALUATION DU SCORE DE GRAVITE GLOBAL (METHODOLOGIE CRQ / FAIR) ---
        AVANT de lister le premier incident (si tu en as trouvé), tu DOIS IMPERATIVEMENT évaluer scientifiquement la gravité globale de la journée (basé sur l'incident le plus critique).
        RÉFÉRENTIEL DE NOTATION STRICT (N'utilise pas la note de 7 ou 8 par défaut ! Un jour normal avec des menaces basiques DOIT être noté entre 2 et 4. Réserve les notes de 8 à 10 UNIQUEMENT pour les crises systémiques) :
        1. Threat Capability (TC) : 1-3 = Vulnérabilité connue et patchée / Attaque basique | 4-7 = Attaque sophistiquée nécessitant une action humaine | 8-10 = Zero-Day critique en cours d'exploitation, Zero-click, Nation-State.
        2. Event Frequency (EF) : 1-3 = Ne cible pas du tout le secteur bancaire/IA | 4-7 = Campagne mondiale opportuniste (la banque peut être touchée) | 8-10 = Le secteur financier ou l'infrastructure Cloud/IA de la banque est la cible directe.
        3. Business Impact (BI) : 1-3 = Impact négligeable, perturbation d'un service mineur | 4-7 = Indisponibilité prolongée, vol de données non-critiques | 8-10 = Risque systémique mondial, vol massif de données financières, faillite.
        
        Tu dois juste fournir les notes dans CE FORMAT EXACT pour la première ligne de ton rapport :
        *(Auditable Metrics - Threat Capability: X/10 | Event Frequency: Y/10 | Business Impact: Z/10)*
        
        Ensuite, saute une ligne et commence à lister les incidents.

        
        Pour CHAQUE incident retenu, tu DOIS IMPERATIVEMENT utiliser LA STRUCTURE EXACTE suivante. Separe chaque incident par une ligne de separation horizontale (---).

        ## Titre de l'incident : Doit INCLURE les noms des acteurs impliques (ex: OpenAI et HuggingFace) et la date la plus precise possible

        **Incident Metadata:**
        - **Primary Category:** [Un seul mot clé principal: AI, CLOUD, RANSOMWARE, SUPPLY CHAIN, DATA LEAK, etc.]
        - **News Nature:** [Nouvelle attaque / Post-mortem / Mise à jour de patch / Arrestation]
        - **Timeline:** [Incident Date: (Quand l'attaque a eu lieu, ex: Juillet 2026 ou Inconnue) | Source Publication Date: (Date de l'article)]
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
            prompt += f"\n- Titre: {art['title']}\n  Lien: {art['link']}\n  Source: {art['source']}\n  Date de publication: {art.get('published', 'Inconnue')}\n  Extrait: {clean_summary}\n"
            
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
                        temperature=0.1,
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
1. SUPPRESSION DES HALLUCINATIONS : Traque les CVE inventées ou les entreprises fictives. Si le brouillon parle d'une attaque qui n'existe ABSOLUMENT PAS dans les articles bruts, supprime toute la section.
2. SUPPRESSION DES FAUX POSITIFS : Une panne informatique (Outage) sans preuve d'attaque n'est PAS un incident cyber. Un tutoriel de sécurité n'est PAS une campagne d'attaque active. Si le brouillon a extrapolé, supprime la section.
3. VÉRIFICATION DES DATES : Ne supprime PAS une section si elle relate la *découverte récente* d'une fuite passée (ex: fuite AWS de 2023 révélée aujourd'hui). Supprime uniquement si l'article est un simple résumé ou rappel d'une vieille affaire sans aucun nouvel élément d'actualité.
4. Rends UNIQUEMENT le rapport Markdown final corrigé. Si TOUTES les sections sont supprimées car elles étaient fausses, retourne UNIQUEMENT le mot "SKIPPED". Ne rajoute pas d'intro ou de conclusion.
"""

    models_to_try = ['gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']
    try:
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False, timeout=360.0)})
        
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
        client = genai.Client(api_key=API_KEY, http_options={'httpx_client': httpx.Client(verify=False, timeout=360.0)})
        
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

def _md_section_to_html(section_text):
    """Convertit un bloc de texte Markdown d'un incident en HTML."""
    lines = section_text.strip().split('\n')
    html_parts = []
    in_metadata = False
    in_control = False
    metadata_lines = []
    control_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_metadata:
                in_metadata = False
                html_parts.append('<div class="metadata">' + '<br>\n'.join(metadata_lines) + '</div>')
                metadata_lines = []
            if in_control:
                in_control = False
                html_parts.append('<div class="control-box">' + '<br>\n'.join(control_lines) + '</div>')
                control_lines = []
            continue
        
        # Detect metadata block start
        if stripped == '**Incident Metadata:**':
            in_metadata = True
            continue
        if in_metadata:
            # Convert - **Key:** Value
            cleaned = re.sub(r'^-\s*', '', stripped)
            cleaned = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cleaned)
            metadata_lines.append(cleaned)
            continue
            
        # Detect section headers like **Overview**, **The Breach Mechanism**, etc.
        header_match = re.match(r'^\*\*(.+?)\*\*\s*$', stripped)
        if header_match and not stripped.startswith('- '):
            title = header_match.group(1)
            if 'Proposed Control' in title:
                in_control = True
                html_parts.append(f'<h3>{title}</h3>')
                continue
            elif 'Conclusion' in title:
                # Close control box if still open
                if in_control:
                    in_control = False
                    html_parts.append('<div class="control-box">' + '<br>\n'.join(control_lines) + '</div>')
                    control_lines = []
                html_parts.append(f'<h3>{title}</h3>')
                continue
            else:
                html_parts.append(f'<h3>{title}</h3>')
                continue
        
        # Bullet points
        if stripped.startswith('- '):
            content = stripped[2:]
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            if in_control:
                control_lines.append(content)
                continue
            html_parts.append(f'<p><strong>•</strong> {content}</p>')
            continue
        
        # Footnotes / Sources section
        if stripped.startswith('[') and re.match(r'^\[\d+\.?\s', stripped):
            url_match = re.search(r'(https?://\S+)', stripped)
            if url_match:
                url = url_match.group(1).rstrip('])')
                domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
                domain_name = domain.group(1) if domain else url
                html_parts.append(f'<a href="{url}">{domain_name}</a><br>')
            continue
        
        # Regular paragraph - convert bold
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
        # Convert markdown links
        para = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', para)
        # Replace em dashes
        para = para.replace(' — ', ' - ').replace('—', '-')
        html_parts.append(f'<p>{para}</p>')
    
    # Flush any remaining control box
    if in_control and control_lines:
        html_parts.append('<div class="control-box">' + '<br>\n'.join(control_lines) + '</div>')
    if in_metadata and metadata_lines:
        html_parts.append('<div class="metadata">' + '<br>\n'.join(metadata_lines) + '</div>')
    
    return '\n'.join(html_parts)

def convert_to_html_report(final_report, threat_score, date_str):
    """Convertit le rapport Markdown final en HTML newsletter stylée."""
    
    # Determine score color
    if threat_score <= 50:
        score_class = "score-green"
        score_emoji = "&#128994;"  # 🟢
    elif threat_score <= 75:
        score_class = "score-orange"
        score_emoji = "&#128992;"  # 🟠
    else:
        score_class = "score-red"
        score_emoji = "&#128308;"  # 🔴
    
    # Extract incident titles for TOC
    titles = re.findall(r'^## (.*)', final_report, re.MULTILINE)
    
    # Build TOC HTML
    toc_html = ""
    for idx, title in enumerate(titles, 1):
        clean_title = title.strip().replace('—', '-')
        toc_html += f'<div class="toc-item"><span class="toc-number">{idx}.</span> {clean_title}</div>\n'
    
    # Split report into incident sections
    # Remove everything before the first ## (score line, TOC, etc.)
    first_incident = final_report.find('## ')
    if first_incident == -1:
        incidents_text = final_report
    else:
        incidents_text = final_report[first_incident:]
    
    # Split by --- separator
    raw_sections = re.split(r'\n---\n', incidents_text)
    
    # Build incidents HTML
    incidents_html = ""
    for idx, section in enumerate(raw_sections, 1):
        section = section.strip()
        if not section:
            continue
        
        # Extract title from ## header
        title_match = re.match(r'^## (.+)', section)
        if title_match:
            incident_title = title_match.group(1).strip().replace('—', '-')
            section_body = section[title_match.end():].strip()
        else:
            incident_title = f"Incident {idx}"
            section_body = section
        
        body_html = _md_section_to_html(section_body)
        
        separator = '<tr><td><hr class="incident-separator"></td></tr>' if idx > 1 else ''
        
        incidents_html += f"""
        {separator}
        <tr>
          <td style="background-color:#e5f4ee;padding:15px 30px;border-top:2px solid #00915A;">
            <h2 style="color:#00915A;margin:0;font-size:18px;">{idx}. {incident_title}</h2>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 30px 10px 30px;">
            {body_html}
          </td>
        </tr>
"""
    
    # Format the date nicely
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
    except:
        formatted_date = date_str
    
    # Assemble the full HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Daily Threat Intel Report</title>
<style>
  p {{ margin-bottom:10px; line-height:1.6; color:#555555; font-size:14px; }}
  h3 {{ color:#333333; font-size:16px; margin:20px 0 10px 0; border-bottom:1px solid #eeeeee; padding-bottom:5px; }}
  .control-box {{ font-weight:bold; background:#f9f9f9; padding:10px; border-left:3px solid #00915A; margin-bottom:15px; color:#333333; font-size:13px; }}
  .metadata {{ background:#f5f5f5; padding:12px 15px; border-radius:4px; margin:10px 0 15px 0; font-size:13px; line-height:1.8; color:#444; }}
  .metadata strong {{ color:#333; }}
  a {{ color:#00915A; text-decoration:none; font-weight:bold; }}
  .incident-separator {{ border:0; border-top:2px solid #eeeeee; margin:25px 0; }}
  .score-badge {{ display:inline-block; padding:6px 14px; border-radius:20px; font-weight:bold; font-size:16px; color:#fff; }}
  .score-green {{ background-color:#28a745; }}
  .score-orange {{ background-color:#fd7e14; }}
  .score-red {{ background-color:#dc3545; }}
  .toc-item {{ font-size:14px; line-height:2; color:#333; }}
  .toc-number {{ font-weight:bold; color:#00915A; }}
</style>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:20px 0;">
  <tr>
    <td align="center">
      <table width="100%" style="max-width:800px;background:#ffffff;border:1px solid #dddddd;border-collapse:collapse;">
        <tr>
          <td style="background-color:#00915A;padding:30px 20px;text-align:center;">
            <h1 style="color:#fff;margin:0;font-size:24px;">Daily Threat Intel Report</h1>
            <p style="color:#e5f4ee;margin:10px 0 0;font-size:14px;">RISK ORM CTFR Intelligence Briefing - {formatted_date}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 30px 10px 30px;text-align:center;">
            <span class="score-badge {score_class}">{score_emoji} Threat Score: {threat_score}/100</span>
          </td>
        </tr>
        <tr>
          <td style="background-color:#e5f4ee;padding:15px 30px;border-top:2px solid #00915A;">
            <h2 style="color:#00915A;margin:0;font-size:18px;">Executive Summary - Incidents</h2>
          </td>
        </tr>
        <tr>
          <td style="padding:15px 30px;">
            {toc_html}
          </td>
        </tr>
        {incidents_html}
        <tr>
          <td style="background:#f9f9f9;padding:20px 30px;text-align:center;">
            <p style="margin:0;font-size:14px;line-height:1.5;color:#555555;">
              For additional information, please contact the <strong>Emerging Technology Risk and Intelligence</strong> team.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background-color:#eeeeee;padding:20px;text-align:center;">
            <p style="margin:0;font-size:11px;color:#999999;">Synthesis by Emerging Technology Risk and Intelligence</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""
    
    return html

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
    
    if "SKIPPED" in draft_report.strip().upper():
        print("L'IA n'a trouvé aucun incident majeur qualifié aujourd'hui. Fin du script.")
        return

    # Extraire le Threat Score du BROUILLON (avant l'audit, car l'auditeur peut reformater cette ligne)
    print("Calcul mathematique et deterministe du score de risque final...")
    match = re.search(r'\*\(\s*Auditable Metrics\s*-\s*Threat Capability:\s*(\d+)/10\s*\|\s*Event Frequency:\s*(\d+)/10\s*\|\s*Business Impact:\s*(\d+)/10\s*\)\*', draft_report, re.IGNORECASE)
    
    if match:
        tc = int(match.group(1))
        ef = int(match.group(2))
        bi = int(match.group(3))
        threat_score = int((tc + ef + bi) * 3.33)
        threat_score = min(threat_score, 100) # Cap at 100
        # Color indicator based on score thresholds
        if threat_score <= 50:
            color_emoji = "🟢"
        elif threat_score <= 75:
            color_emoji = "🟠"
        else:
            color_emoji = "🔴"
        score_line = f"{color_emoji} **Threat Score:** {threat_score}/100\n*(Auditable Metrics - Threat Capability: {tc}/10 | Event Frequency: {ef}/10 | Business Impact: {bi}/10)*\n\n"
    else:
        score_line = "🟢 **Threat Score:** 0/100\n\n"
    
    final_report = verify_and_correct_report(draft_report, articles)
    
    if "SKIPPED" in final_report.strip().upper():
        print("L'Auditeur IA a invalidé l'intégralité du brouillon (hors-sujet ou hallucinations). Aucun rapport ne sera publié.")
        return

    # Injecter le score calculé en tête du rapport final audité
    final_report = score_line + final_report

    # Génération du sommaire (Table of Contents) - sans hyperliens
    titles = re.findall(r'^## (.*)', final_report, re.MULTILINE)
    if titles:
        toc = "**Executive Summary - Incidents:**\n"
        for idx, title in enumerate(titles, 1):
            clean_title = title.strip()
            toc += f"{idx}. {clean_title}\n"
        toc += "\n---\n\n"
        final_report = final_report.replace(score_line, score_line + toc, 1)

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    # Toujours sauvegarder le Markdown (pour GitHub et la DB)
    md_filename = os.path.join(output_dir, f"Daily_Threat_Intel_{today_str}.md")
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Threat Intel Report\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(final_report)
    print(f"\nRapport Markdown sauvegarde : {md_filename}")
    
    # Générer le fichier .eml dans un dossier séparé newsletters/
    if OUTPUT_FORMAT == "html":
        nl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "newsletters")
        os.makedirs(nl_dir, exist_ok=True)
        html_content = convert_to_html_report(final_report, threat_score, today_str)
        eml_filename = os.path.join(nl_dir, f"Daily_Threat_Intel_{today_str}.eml")
        with open(eml_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Newsletter .eml sauvegardee : {eml_filename}")
        
    print(f"\nTermine ! Format de sortie : {OUTPUT_FORMAT.upper()}")
    
    print("\nMise à jour de la base de connaissances (Contrôles)...")
    update_databases(final_report, today_str)

if __name__ == "__main__":
    main()
