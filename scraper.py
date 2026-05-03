import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
os.makedirs('data', exist_ok=True)

def init_db():
    conn = sqlite3.connect('data/raw_jobs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            scraped_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def scrape_job_detail(job_url):
    """Scrape full job description from individual job page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(job_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        description = ""
        
        # Try multiple selectors for job description
        desc_selectors = [
            'div.job-description',
            'div.listing-container',
            'div.content',
            'article',
            'main',
            'div[class*="description"]',
            'div[class*="content"]',
        ]
        
        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text(separator=' ', strip=True)
                if len(description) > 100:
                    break
        
        # Clean up
        description = re.sub(r'<[^>]+>', '', description)
        description = ' '.join(description.split())
        
        return description[:8000]
        
    except Exception as e:
        logging.warning(f"Error fetching job detail {job_url}: {e}")
        return ""

def scrape_weworkremotely():
    """Scrape job listings from We Work Remotely"""
    init_db()
    conn = sqlite3.connect('data/raw_jobs.db')
    c = conn.cursor()
    
    base_url = "https://weworkremotely.com"
    scraped_count = 0
    skipped_count = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        category_url = f"{base_url}/categories/remote-programming-jobs"
        logging.info(f"Fetching: {category_url}")
        
        response = requests.get(category_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all job listings
        job_listings = soup.find_all('li', class_=re.compile('new-listing-container', re.I))
        
        if not job_listings:
            job_listings = soup.find_all('li', class_=lambda x: x and 'listing' in x.lower())
        
        logging.info(f"Found {len(job_listings)} job listings")
        
        for i, job in enumerate(job_listings, 1):
            try:
                # Extract job title - try multiple methods
                title = "Unknown Title"
                
                # Method 1: h4 with title class
                title_elem = job.find('h4', class_=re.compile('title', re.I))
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                else:
                    # Method 2: any h4
                    title_elem = job.find('h4')
                    if title_elem and title_elem.get_text(strip=True):
                        title = title_elem.get_text(strip=True)
                    else:
                        # Method 3: span with title class
                        title_elem = job.find('span', class_=re.compile('title', re.I))
                        if title_elem and title_elem.get_text(strip=True):
                            title = title_elem.get_text(strip=True)
                        else:
                            # Method 4: any element with title in class
                            title_elem = job.find(class_=re.compile('title', re.I))
                            if title_elem and title_elem.get_text(strip=True):
                                title = title_elem.get_text(strip=True)
                
                # Extract company name
                company = "Unknown Company"
                company_elem = job.find('p', class_=re.compile('company', re.I))
                if company_elem:
                    company = company_elem.get_text(strip=True)
                else:
                    company_elem = job.find('span', class_=re.compile('company', re.I))
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    else:
                        company_elem = job.find(class_=re.compile('company', re.I))
                        if company_elem:
                            company = company_elem.get_text(strip=True)
                
                # Extract location/region
                location = "Remote"
                location_elem = job.find('span', class_=re.compile('region|location|tag', re.I))
                if location_elem:
                    location = location_elem.get_text(strip=True)
                else:
                    tags = job.find_all('span', class_=re.compile('tag', re.I))
                    if tags:
                        location = ', '.join([tag.get_text(strip=True) for tag in tags[:2]])
                
                # Extract job URL
                link_elem = job.find('a', href=True)
                if not link_elem:
                    continue
                    
                job_path = link_elem['href']
                if job_path.startswith('/'):
                    job_url = f"{base_url}{job_path}"
                elif job_path.startswith('http'):
                    job_url = job_path
                else:
                    job_url = f"{base_url}/{job_path}"
                
                # Get description from detail page
                logging.info(f"  [{i}/{len(job_listings)}] {title[:40]:40} | {company[:20]}")
                description = scrape_job_detail(job_url)
                
                # If description too short, build from title + company + location
                if len(description) < 100:
                    description = f"{title} at {company}. Location: {location}. Remote programming position."
                
                # Clean up description
                description = re.sub(r'<[^>]+>', '', description)
                description = ' '.join(description.split())
                
                # Insert into database
                scraped_date = datetime.now().strftime("%Y-%m-%d")
                
                c.execute('''
                    INSERT OR IGNORE INTO jobs 
                    (title, company, location, description, url, scraped_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, company, location, description, job_url, scraped_date))
                
                if c.rowcount > 0:
                    scraped_count += 1
                    logging.info(f"  ✅ Added: {title[:50]}")
                else:
                    skipped_count += 1
                
                # Polite delay between requests
                time.sleep(1.5)
                
            except Exception as e:
                logging.warning(f"Error parsing job {i}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ Done! New: {scraped_count}, Skipped: {skipped_count}")
        return scraped_count
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        conn.close()
        return 0

if __name__ == "__main__":
    print("🚀 Starting Web Scraper...")
    print("   Target: We Work Remotely (weworkremotely.com)")
    print("   Category: Remote Programming Jobs")
    print("-" * 50)
    count = scrape_weworkremotely()
    print("-" * 50)
    print(f"✅ Done! Scraped {count} new jobs")
    print("📁 Check data/raw_jobs.db for results")