# Standard Operating Procedure (SOP) - Daily Threat Intel Tracker

## 1. Objectif du Projet
Le projet **News Tracker** est un outil automatisé de Threat Intelligence conçu pour les analystes de risques cyber (Emerging Tech & AI). 
Il collecte quotidiennement les dernières actualités de cybersécurité via des flux RSS, filtre les événements les plus critiques (jusqu'au TOP 10) et génère automatiquement un rapport "Executive Summary" ultra-structuré grâce à l'Intelligence Artificielle (Google Gemini).

## 2. Architecture et Composants
- `news_tracker.py` : Script Python principal contenant la logique d'extraction (RSS), d'appel à l'API LLM et de formatage.
- `requirements.txt` : Liste des dépendances Python (google-genai, beautifulsoup4, feedparser, httpx, certifi).
- `.github/workflows/daily-tracker.yml` : Workflow GitHub Actions assurant l'exécution quotidienne du script.
- `reports/` : Dossier généré automatiquement contenant les rapports quotidiens au format Markdown.

## 3. Déclenchement et Exécution

### Exécution Automatique (Standard)
L'outil s'exécute de manière autonome tous les jours le matin via GitHub Actions.
1. Le script s'exécute sur les serveurs GitHub.
2. Il récupère les flux RSS des 24 dernières heures.
3. Il génère le rapport avec l'API Gemini.
4. Il "commit" et "push" automatiquement le nouveau fichier dans le dossier `reports/` du dépôt GitHub.

### Exécution Manuelle (Ad-hoc)
**Sur GitHub :**
1. Aller dans l'onglet **Actions**.
2. Sélectionner **Daily Threat Intel Tracker** à gauche.
3. Cliquer sur **Run workflow**.

**En Local :**
1. Assurez-vous d'avoir Python installé et les dépendances (`pip install -r requirements.txt`).
2. Définissez votre variable d'environnement : `set GEMINI_API_KEY=votre_cle_api`
3. Lancez le script : `python news_tracker.py`

## 4. Maintenance et Configuration

### Ajouter de nouvelles sources d'information (RSS)
1. Ouvrir `news_tracker.py`.
2. Localiser la liste `RSS_FEEDS`.
3. Ajouter l'URL du nouveau flux RSS dans la liste.

### Modifier le comportement de l'IA (Prompt ou Modèle)
1. Ouvrir `news_tracker.py`.
2. **Pour changer le format** : Modifier la variable `prompt` (attention à bien respecter les instructions existantes de formatage Markdown).
3. **Pour changer la constante/créativité** : Ajuster la valeur `temperature=0.2` (0.0 = très strict, 1.0 = créatif).
4. L'outil utilise un système de "fallback" de modèles (`gemini-3.6-flash` > `gemini-3.5-flash` > `gemini-3.1-flash-lite`). Ce tableau peut être modifié.

### Gestion de la Clé API
La clé de l'API Google Gemini doit être stockée de manière sécurisée :
- **Sur GitHub** : Allez dans *Settings > Secrets and variables > Actions*, et assurez-vous que `GEMINI_API_KEY` est bien renseigné.

## 5. Dépannage (Troubleshooting)

- **L'Action GitHub échoue sur l'API Gemini** : Vérifiez que la clé `GEMINI_API_KEY` n'a pas expiré et que votre quota gratuit/payant n'est pas dépassé.
- **Rapport généré mais non poussé sur GitHub (Erreur réseau/Git)** : Si le dépôt a été modifié manuellement pendant que l'Action tournait, cela peut créer un conflit. Lancez un `git pull --rebase` en local et poussez vos modifications pour resynchroniser la branche.
- **Nombre d'articles incohérent** : L'IA est paramétrée en "High Recall" avec une température de 0.2. Si un jour il n'y a que 2 actualités, c'est que l'IA a jugé le reste des flux totalement hors-sujet. 

---
*Dernière mise à jour de la SOP : Juillet 2026*
