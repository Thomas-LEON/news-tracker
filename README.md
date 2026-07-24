# 🛡️ Daily Threat Intel & Emerging Tech Tracker

An automated Threat Intelligence and Cybersecurity news tracker built for Risk Analysts and Security Professionals. 

This tool autonomously scrapes top cybersecurity RSS feeds, analyzes the data using Google's Gemini AI, and generates a structured, executive-ready Markdown report highlighting the most critical threats of the last 24 hours.

## ✨ Features

- **Automated Daily Briefings:** Runs automatically via GitHub Actions every morning.
- **AI-Powered Curation:** Leverages Google Gemini to filter the noise and isolate the TOP 10 most critical incidents (e.g., AI flaws, supply chain attacks, autonomous agent activities).
- **Executive Formatting:** Outputs reports directly aligned with C-Level/Executive communication standards.
- **Metadata Extraction:** Automatically extracts critical structured data for every incident:
  - Impacted Country
  - Geolocation / Cloud Region
  - List of Companies Impacted
- **High Recall Strategy:** Tuned to favor inclusivity (high recall) ensuring no potentially critical threat is missed.

## 📁 Repository Structure

- `news_tracker.py`: Core logic for RSS parsing, AI prompt engineering, and Markdown report generation.
- `.github/workflows/daily-tracker.yml`: GitHub Actions pipeline for daily automated execution.
- `requirements.txt`: Python dependencies.
- `SOP.md`: Standard Operating Procedure document detailing internal maintenance and troubleshooting.
- `reports/`: Destination folder for the generated daily Markdown briefings.

## 🚀 Setup and Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
git clone https://github.com/Thomas-LEON/news-tracker.git
cd news-tracker
pip install -r requirements.txt
```

### 3. API Key Configuration
This tool relies on Google Gemini API. Get an API key from Google AI Studio.

**For Local Usage:**
Set the environment variable on your machine:
```bash
# Windows
set GEMINI_API_KEY=your_api_key

# Linux/Mac
export GEMINI_API_KEY=your_api_key
```

**For GitHub Actions (Automated Mode):**
Go to your repository settings on GitHub:
1. Navigate to **Settings** > **Secrets and variables** > **Actions**.
2. Create a new repository secret named `GEMINI_API_KEY` and paste your key.

## 🛠️ Usage

**Run Locally:**
```bash
python news_tracker.py
```
This will fetch the last 24h of news, interact with Gemini, and drop a new `.md` report inside the `reports/` directory.

**Run via GitHub Actions:**
The tool runs on a daily schedule automatically. To trigger it manually:
1. Go to the **Actions** tab in this repository.
2. Select **Daily Threat Intel Tracker**.
3. Click **Run workflow**.

## 📡 Current Information Sources

The script currently monitors the following high-quality cybersecurity RSS feeds:
- The Hacker News
- Bleeping Computer
- Dark Reading
- CyberScoop
- Krebs on Security
- SecurityWeek
- InfoSecurity Magazine
- TechCrunch Security
- Ars Technica Security

*(To add more, simply edit the `RSS_FEEDS` list in `news_tracker.py`).*
