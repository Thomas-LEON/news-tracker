import os
import datetime
import feedparser
from google import genai
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
    "https://krebsonsecurity.com/feed/"
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

def generate_executive_summary(articles):
    """Utilise l'IA pour trier les articles et générer un Executive Summary."""
    if not articles:
        return "Aucun incident ou article majeur détecté dans les dernières 24 heures."
    
    try:
        # Configuration pour le nouveau package google.genai
        # Contournement SSL local (Windows/Zscaler/proxy...) : On utilise client_args={'verify': False}
        client = genai.Client(api_key=API_KEY, http_options={'client_args': {'verify': False}})
        
        prompt = """
        Tu es un expert en Threat Intelligence et analyste des risques lies aux technologies emergentes (IA, Cyberattaques, etc.).
        Voici une liste brute d'articles recuperes aujourd'hui. Ton role est de filtrer cette liste pour ne garder que le TOP 1 a 5 des incidents les plus critiques pour ton metier. (Typiquement : failles dans des modeles d'IA, attaques sur des entreprises tech, nouvelles methodes de menaces).
        
        Pour chaque incident retenu, redige un 'Executive Summary' en francais, oriente 'Business & Risk'.
        
        REGLES IMPORTANTES :
        1. Le resume doit inclure les 5W (Who, What, When, Where, Why/How) de maniere fluide et naturelle. NE FAIS PAS de liste 'Who: ... What: ...'. Le format doit etre executif, pro, sous forme de 1 a 2 paragraphes max.
        2. Ajoute les sources en footnotes au format Markdown (ex: [^1]).
        
        Format attendu pour chaque point :
        
        ### [Titre de l'incident / Menace]
        **Executive Summary:**
        [Ton resume executif fluide integrant les 5W]
        
        ---
        
        [A la toute fin de ton texte, insere les references des footnotes avec les URLs d'origine]
        
        Voici les articles bruts :
        """
        
        for i, art in enumerate(articles):
            soup = BeautifulSoup(art['summary'], 'html.parser')
            clean_summary = soup.get_text()[:400]
            prompt += f"\n- Titre: {art['title']}\n  Lien: {art['link']}\n  Source: {art['source']}\n  Extrait: {clean_summary}\n"
            
        response = client.models.generate_content(
            model='gemini-3.1-flash',
            contents=prompt,
        )
        return response.text
        
    except Exception as e:
        return f"Erreur lors de l'appel a l'API IA : {e}\nAvez-vous bien configure la cle d'API GEMINI_API_KEY ?"

def main():
    print("Recherche des actualites (Threat Intel & Cyber) des dernieres 24h...")
    articles = fetch_recent_news()
    print(f"{len(articles)} articles trouves.")
    
    print("Analyse par l'IA et redaction de l'Executive Summary...")
    report = generate_executive_summary(articles)
    
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
