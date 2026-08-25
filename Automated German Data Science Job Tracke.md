Automated German Data Science Job Tracker & Telegram Alert Bot

## 1. Project Goal
Build an automated, serverless Python job alert agent hosted on GitHub Actions. The system polls real-time German student roles (Werkstudent, Praktikum, Masterarbeit) across the official **Bundesagentur für Arbeit Public API** and **LinkedIn/Indeed (via JobSpy guest scrapers)** every 20–30 minutes, deduplicates postings, and delivers instant push notifications to a personal Telegram chat with direct application links.

---

## 2. Tech Stack & Environment
- **Runtime:** Python 3.11+
- **Host / Scheduler:** GitHub Actions (Cron schedule every 25 minutes)
- **Data Sources:**
  - Bundesagentur für Arbeit Public REST API (`angebotsart=4`)
  - `python-jobspy` (Guest endpoint scraper for LinkedIn & Indeed DE)
- **State Store:** `data/seen_jobs.json` (version-controlled directly via GitHub Actions Git commit-back)
- **Notifier:** Telegram Bot API (`https://api.telegram.org/bot<TOKEN>/sendMessage`)
- **Key Dependencies:** `requests`, `python-jobspy`, `pandas`

---

## 3. Directory Structure

```text
.
├── .github/
│   └── workflows/
│       └── job_tracker.yml
├── data/
│   └── seen_jobs.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── storage.py
│   ├── notifier.py
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── arbeitsagentur.py
│   │   └── jobspy_scraper.py
│   └── main.py
├── requirements.txt
├── .gitignore
└── README.md
4. Implementation Specification
4.1. Dependencies (requirements.txt)
Plaintext
requests>=2.31.0
python-jobspy>=1.1.55
pandas>=2.1.0
4.2. Configuration (src/config.py)
Read secrets from environment variables:

TELEGRAM_BOT_TOKEN: Telegram bot token from @BotFather.

TELEGRAM_CHAT_ID: Recipient numeric chat ID.

Define search parameters:

Keywords: ["Werkstudent Data Science", "Praktikum Data Science", "Masterarbeit Data Science", "Working Student Machine Learning", "Werkstudent KI", "Internship Data Science"]

Location: Germany / Dortmund (configurable via env JOB_LOCATION, default: Deutschland).

Max Age: hours_old=2 / veroeffentlichtseit=1.

4.3. State Management (src/storage.py)
Manage data/seen_jobs.json.

State format:

JSON
{
  "seen_ids": {
    "aa_10000-1234567890-S": "2026-08-25T14:30:00Z",
    "li_3987654321": "2026-08-25T14:35:00Z"
  }
}
Implement:

load_seen_ids(filepath: str) -> set: Reads file; returns set of IDs. If file does not exist, return empty set.

save_seen_ids(filepath: str, new_ids: dict): Appends new IDs, removes entries older than 30 days to prevent unbounded growth, and writes back formatted JSON.

4.4. Fetcher: Arbeitsagentur API (src/fetchers/arbeitsagentur.py)
Endpoint: https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs

Headers:

X-API-Key: jobboerse-jobsuche

User-Agent: StudentJobAgent/1.0

Query Parameters per keyword:

was: keyword

wo: location

angebotsart: 4 (Praktikum / Werkstudent / Abschlussarbeit)

veroeffentlichtseit: 1 (last 24 hours)

size: 50

Mapping output normalized schema:

job_id: "aa_" + item.get("refnr")

title: item.get("titel")

company: item.get("arbeitgeber")

location: item.get("arbeitsort", {}).get("ort", "Germany")

url: Direct portal link constructed from refnr or item.get("externeUrl")

source: "Bundesagentur für Arbeit"

4.5. Fetcher: JobSpy / LinkedIn & Indeed (src/fetchers/jobspy_scraper.py)
Call jobspy.scrape_jobs:

site_name=["linkedin", "indeed"]

search_term=keyword

location="Germany"

results_wanted=15

hours_old=2

country_indeed="germany"

Handle exceptions gracefully (e.g. rate-limiting, missing fields) without crashing the pipeline.

Map to normalized schema:

job_id: "li_" + str(job.get("id")) or SHA1 hash of URL if ID missing

title: job.get("title")

company: job.get("company")

location: job.get("location")

url: job.get("job_url")

source: "LinkedIn / Indeed"

4.6. Notifier (src/notifier.py)
Format Telegram messages using HTML mode:

HTML
🎯 <b>New Student Role Found!</b>

📌 <b>Title:</b> {title}
🏢 <b>Company:</b> {company}
📍 <b>Location:</b> {location}
📡 <b>Source:</b> {source}

🔗 <a href="{url}">Apply Directly</a>
Send via POST https://api.telegram.org/bot{TOKEN}/sendMessage.

Rate-limit safety: Include time.sleep(0.5) between messages if multiple jobs are found in a single cycle.

4.7. Orchestrator (src/main.py)
Initialize storage and load seen_ids.

Fetch jobs sequentially from Arbeitsagentur and JobSpy across configured keywords.

Filter out any job whose job_id exists in seen_ids.

Send Telegram alerts for newly discovered jobs.

Update and write back seen_jobs.json.

Print summary statistics (e.g., Total fetched: X | New alert sent: Y).

5. GitHub Actions Workflow (.github/workflows/job_tracker.yml)
YAML
name: Run Job Alert Tracker

on:
  schedule:
    - cron: '*/25 * * * *'  # Runs every 25 minutes
  workflow_dispatch:        # Allows manual run from GitHub UI

concurrency:
  group: job-tracker
  cancel-in-progress: false

jobs:
  track-and-alert:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Execute Tracker Script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          JOB_LOCATION: "Germany"
        run: |
          python src/main.py

      - name: Commit and push updated seen state
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add data/seen_jobs.json
          git diff-index --quiet HEAD || git commit -m "chore(cache): update seen jobs state [skip ci]"
          git push
6. Execution & Setup Instructions for the Agent
Initialize Project Files:

Create all files matching the directory structure above.

Initialize data/seen_jobs.json with {"seen_ids": {}}.

Configure GitHub Repository Secrets:

Add TELEGRAM_BOT_TOKEN

Add TELEGRAM_CHAT_ID

Local Testing:

Run python src/main.py locally with test environment variables to verify API parsing and Telegram delivery.

Verify that running the script twice does not trigger duplicate notifications.

Push to Remote:

Push to the main branch.

Trigger a manual run via the GitHub Actions tab to confirm permissions for git commit-back.