import sqlite3
import pandas as pd
import re
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

os.makedirs('data', exist_ok=True)

def init_cleaned_db():
    conn = sqlite3.connect('data/processed_jobs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cleaned_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            scraped_date TEXT,
            cleaned_date TEXT,
            quality_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def clean_text(text):
    if not text or pd.isna(text):
        return ""
    text = str(text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove weird unicode characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\-\(\)\/\&\+\#\@\%]', ' ', text)
    # Remove multiple spaces again
    text = ' '.join(text.split())
    return text.strip()

def normalize_location(location):
    if not location or pd.isna(location):
        return "Remote"
    location = str(location).strip()
    loc_lower = location.lower()
    
    # Common remote variations
    if any(word in loc_lower for word in ['remote', 'worldwide', 'anywhere', 'global', 'distributed']):
        return "Remote"
    if any(word in loc_lower for word in ['america', 'us ', 'usa', 'united states', 'north america']):
        return "Americas"
    if any(word in loc_lower for word in ['europe', 'eu ', 'uk ', 'united kingdom']):
        return "Europe"
    if any(word in loc_lower for word in ['asia', 'apac', 'pacific']):
        return "Asia-Pacific"
    
    return location

def validate_job(row):
    score = 100
    
    # Title validation
    title = str(row.get('title', ''))
    if not title or len(title) < 3:
        return 0
    if len(title) < 10:
        score -= 10
    
    # Company validation
    company = str(row.get('company', ''))
    if not company or len(company) < 2 or company.lower() in ['unknown company', 'unknown']:
        score -= 25
    
    # Description validation
    description = str(row.get('description', ''))
    if not description or len(description) < 50:
        score -= 40
    elif len(description) < 150:
        score -= 15
    
    # URL validation
    url = str(row.get('url', ''))
    if not url or not url.startswith('http'):
        return 0
    
    # Spam detection
    spam_phrases = [
        'click here', 'earn money fast', 'work from home easy', 
        'make money online', 'get rich quick', 'no experience needed',
        'limited spots', 'act now', 'urgent hiring', 'crypto',
        'bitcoin', 'investment opportunity'
    ]
    desc_lower = description.lower()
    if any(spam in desc_lower for spam in spam_phrases):
        return 0
    
    # Check for suspicious patterns
    if description.count('$') > 10:  # Too many dollar signs
        score -= 20
    if description.count('!') > 15:   # Too many exclamations
        score -= 10
    
    return max(0, score)

def run_cleaner():
    print("=" * 50)
    print("🧹 CLEANER STARTING...")
    print("=" * 50)

    # Check if raw database exists
    if not os.path.exists('data/raw_jobs.db'):
        print("❌ Error: data/raw_jobs.db not found. Run scraper.py first!")
        return

    # Load raw data
    conn = sqlite3.connect('data/raw_jobs.db')
    try:
        df = pd.read_sql_query('SELECT * FROM jobs', conn)
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        conn.close()
        return
    conn.close()

    if len(df) == 0:
        print("⚠️  No jobs found in raw database. Run scraper.py first!")
        return

    print(f"📥 Loaded {len(df)} raw jobs")

    # Remove duplicates by URL
    initial = len(df)
    df = df.drop_duplicates(subset=['url'], keep='first')
    print(f"🗑️  Removed {initial - len(df)} duplicate URLs")

    # Clean text fields
    df['title'] = df['title'].apply(clean_text)
    df['company'] = df['company'].apply(clean_text)
    df['location'] = df['location'].apply(normalize_location)
    df['description'] = df['description'].apply(clean_text)

    # Validate and score
    df['quality_score'] = df.apply(validate_job, axis=1)
    before = len(df)
    df = df[df['quality_score'] >= 40].copy()
    removed = before - len(df)
    print(f"🗑️  Removed {removed} low quality jobs")
    print(f"✅ Remaining: {len(df)} clean jobs")

    if len(df) == 0:
        print("⚠️  No jobs passed quality check. Check your scraper output!")
        return

    # Save to processed database
    init_cleaned_db()
    df['cleaned_date'] = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect('data/processed_jobs.db')
    df.to_sql('cleaned_jobs', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

    # Show sample
    print(f"\n📊 Sample of cleaned data:")
    print("-" * 40)
    for _, row in df.head(3).iterrows():
        print(f"  • {row['title'][:50]}...")
        print(f"    Company: {row['company']} | Location: {row['location']}")
        print(f"    Score: {row['quality_score']:.0f}/100")
        print()

    print(f"✅ Done! Saved {len(df)} cleaned jobs to data/processed_jobs.db")
    print("=" * 50)

if __name__ == "__main__":
    run_cleaner()