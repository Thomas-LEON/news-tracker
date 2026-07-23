# Standard Operating Procedure (SOP) - Daily Threat Intel Tracker

## 1. Project Objective
The **News Tracker** project is an automated Threat Intelligence tool designed for cyber risk analysts (Emerging Tech & AI).
It daily collects the latest cybersecurity news via RSS feeds, filters the most critical events (up to the TOP 10), and automatically generates a highly structured "Executive Summary" report using Artificial Intelligence (Google Gemini).

## 2. Architecture and Components
- `news_tracker.py`: Main Python script containing the extraction logic (RSS), LLM API calls, and formatting.
- `requirements.txt`: List of Python dependencies (google-genai, beautifulsoup4, feedparser, httpx, certifi).
- `.github/workflows/daily-tracker.yml`: GitHub Actions workflow ensuring the daily execution of the script.
- `reports/`: Automatically generated folder containing daily reports in Markdown format.

## 3. Triggering and Execution

### Automated Execution (Standard)
The tool runs autonomously every day in the morning via GitHub Actions.
1. The script runs on GitHub servers.
2. It fetches RSS feeds from the last 24 hours.
3. It generates the report using the Gemini API.
4. It automatically commits and pushes the new file to the `reports/` folder of the GitHub repository.

### Manual Execution (Ad-hoc)
**On GitHub:**
1. Go to the **Actions** tab.
2. Select **Daily Threat Intel Tracker** on the left.
3. Click on **Run workflow**.

**Locally:**
1. Ensure Python is installed along with dependencies (`pip install -r requirements.txt`).
2. Set your environment variable: `set GEMINI_API_KEY=your_api_key`
3. Run the script: `python news_tracker.py`

## 4. Maintenance and Configuration

### Adding New Information Sources (RSS)
1. Open `news_tracker.py`.
2. Locate the `RSS_FEEDS` list.
3. Add the URL of the new RSS feed to the list.

### Modifying AI Behavior (Prompt or Model)
1. Open `news_tracker.py`.
2. **To change the format**: Modify the `prompt` variable (be careful to follow the existing Markdown formatting instructions).
3. **To change consistency/creativity**: Adjust the `temperature=0.2` value in the `config` object (0.0 = very strict, 1.0 = creative).
4. The tool uses a model fallback system (`gemini-3.6-flash` > `gemini-3.5-flash` > `gemini-3.1-flash-lite`). This array can be modified.

### API Key Management
The Google Gemini API key must be securely stored:
- **On GitHub**: Go to *Settings > Secrets and variables > Actions*, and ensure `GEMINI_API_KEY` is properly set.

## 5. Troubleshooting

- **GitHub Action fails on the Gemini API**: Verify that the `GEMINI_API_KEY` has not expired and your free/paid quota has not been exceeded.
- **Report generated but not pushed to GitHub (Network/Git Error)**: If the repository was manually modified while the Action was running, this can create a conflict. Run a `git pull --rebase` locally and push your changes to resync the branch.
- **Inconsistent number of articles**: The AI is set to "High Recall" with a temperature of 0.2. If there are only 2 news items on a given day, it means the AI judged the rest of the feeds as completely irrelevant to the threat scope.

---
*Last update of the SOP: July 2026*
