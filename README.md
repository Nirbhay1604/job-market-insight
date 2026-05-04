# 🚀 Job Market Insights Scraper

A complete web scraping and data pipeline that extracts remote programming job listings from [We Work Remotely](https://weworkremotely.com), cleans and validates the data, extracts in-demand tech skills, and generates visual analytics dashboards.

---

## 📁 Project Structure
job-market-insights/
├── scraper.py          # Web scraper - fetches jobs from We Work Remotely
├── cleaner.py          # Data cleaner - validates & cleans scraped data
├── skill_extractor.py  # Skill extractor - identifies 80+ tech skills
├── analyzer.py         # Analyzer - generates 2 insight dashboards
├── data/               # SQLite databases & output charts
│   ├── raw_jobs.db
│   ├── processed_jobs.db
│   ├── insights_dashboard_part1.png  # Skills & Companies
│   ├── insights_dashboard_part2.png  # Locations & Quality
│   └── summary_stats.csv
├── requirements.txt    # Python dependencies
└── README.md           # This file

---

## ⚡ Features

| Module | What It Does |
|--------|-------------|
| **Scraper** | Scrapes job titles, companies, locations & descriptions with polite 1.5s delays |
| **Cleaner** | Removes duplicates, normalizes text, filters spam, assigns quality scores (0-100) |
| **Skill Extractor** | Extracts 80+ tech skills using regex with strict word boundaries |
| **Analyzer** | Generates 2 separate dashboards to prevent text overlap |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **BeautifulSoup4** + **Requests** — Web scraping
- **SQLite** — Local data storage
- **Pandas** — Data manipulation
- **Matplotlib** — Data visualization

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Nirbhay1604/job-market-insights.git
cd job-market-insights

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

🚀 Usage
Run the pipeline in order:
# Step 1: Scrape jobs (~5-7 minutes for ~160 jobs)
python scraper.py

# Step 2: Clean and validate data
python cleaner.py

# Step 3: Extract tech skills
python skill_extractor.py

# Step 4: Generate analytics dashboards
python analyzer.py

Output Files:
data/raw_jobs.db — Raw scraped data
data/processed_jobs.db — Cleaned & validated data
data/insights_dashboard_part1.png — Top Skills & Hiring Companies
data/insights_dashboard_part2.png — Locations & Quality Distribution
data/summary_stats.csv — Summary statistics

📊 Sample Output:

📈 OVERALL STATS
----------------------------------------
Total Jobs:        161
Unique Companies:  160
Unique Locations:  1
Unique Skills:     20
Avg Quality Score: 99.8/100

🏢 TOP HIRING COMPANIES
----------------------------------------
 1. Dragos                            2 jobs
 2. Stripe                            1 jobs
 3. GitLab                            1 jobs
 ...

🎯 TOP 20 MOST DEMANDED SKILLS
   (29 mentions across 17 jobs)
----------------------------------------
 1. SECURITY               ██████████████████████████████   6 ( 3.7%)
 2. TYPESCRIPT             ██████████░░░░░░░░░░░░░░░░░░░░   2 ( 1.2%)
 3. REACT                  ██████████░░░░░░░░░░░░░░░░░░░░   2 ( 1.2%)
 4. JAVA                   ██████████░░░░░░░░░░░░░░░░░░░░   2 ( 1.2%)
 5. GO                     ██████████░░░░░░░░░░░░░░░░░░░░   2 ( 1.2%)
 6. WEB3                   █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
 7. VERCEL                 █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
 8. TDD                    █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
 9. POSTGRESQL             █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
10. NLP                    █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
11. MACHINE LEARNING       █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
12. LLM                    █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
13. KUBERNETES             █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
14. JAVASCRIPT             █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
15. GRAPHQL                █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
16. GITLAB                 █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
17. GCP                    █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
18. CI/CD                  █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
19. AZURE                  █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)
20. AWS                    █████░░░░░░░░░░░░░░░░░░░░░░░░░   1 ( 0.6%)

⚠️ Important Notes
Rate Limiting: 1.5-second delay between requests to respect We Work Remotely's servers
HTML Changes: If WWR updates their layout, update CSS selectors in scraper.py
Educational Use: Check robots.txt and Terms of Service before scraping

🤝 Contributing:
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open a Pull Request

🙏 Acknowledgments:
We Work Remotely for job listings
Built for the job-seeking developer community

---

## requirements.txt

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
lxml>=4.9.0
