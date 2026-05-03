import sqlite3
import re
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# FIXED: Removed problematic short words, added stricter matching
TECH_SKILLS = [
    # Languages
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'golang',
    'rust', 'kotlin', 'swift', 'typescript', 'php', 'scala', 'perl',
    'matlab', 'dart', 'elixir', 'clojure', 'haskell', 'lua', 'shell', 'bash',
    
    # Web Frontend
    'react', 'reactjs', 'angular', 'vue', 'vuejs', 'svelte', 'nextjs',
    'gatsby', 'jquery', 'bootstrap', 'tailwind', 'tailwindcss', 'webpack',
    'vite', 'sass', 'html5', 'css3', 'webgl',
    
    # Web Backend  
    'django', 'flask', 'fastapi', 'spring boot', 'spring', 'express',
    'expressjs', 'nestjs', 'laravel', 'symfony', 'rails', 'ruby on rails',
    'asp.net', 'dotnet', '.net', 'graphql', 'rest api', 'grpc',
    'microservices', 'serverless',
    
    # Databases
    'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis',
    'elasticsearch', 'cassandra', 'dynamodb', 'firebase', 'supabase',
    'prisma', 'sequelize', 'sqlalchemy', 'orm',
    
    # Data Science / ML
    'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
    'jupyter', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch',
    'keras', 'xgboost', 'lightgbm', 'opencv', 'nltk', 'spacy',
    'hugging face', 'transformers', 'llm', 'langchain', 'openai',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    'data science', 'data engineering', 'big data', 'apache spark',
    'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'snowflake',
    'databricks', 'tableau', 'power bi',
    
    # DevOps / Cloud / Infra
    'docker', 'kubernetes', 'k8s', 'helm', 'terraform', 'ansible',
    'jenkins', 'github actions', 'gitlab ci', 'circleci', 'argo cd',
    'nginx', 'aws', 'amazon web services', 'ec2', 's3', 'lambda',
    'gcp', 'google cloud', 'azure', 'cloudflare', 'vercel', 'netlify',
    'heroku', 'prometheus', 'grafana', 'datadog',
    
    # Mobile
    'react native', 'flutter', 'android', 'ios',
    
    # Testing
    'jest', 'mocha', 'cypress', 'playwright', 'selenium', 'puppeteer',
    'pytest', 'junit', 'cucumber', 'tdd', 'bdd',
    
    # Tools / Other
    'git', 'github', 'gitlab', 'jira', 'confluence', 'figma',
    'postman', 'swagger', 'openapi', 'linux', 'ubuntu',
    'agile', 'scrum', 'kanban', 'ci/cd', 'cicd', 'sre',
    'oauth', 'jwt', 'sso', 'security',
    'blockchain', 'web3', 'solidity', 'ethereum', 'smart contracts',
    'seo', 'google analytics'
]

# Skills that are too short and cause false positives - require space before/after
SHORT_SKILLS = {'go', 'r', 'c', 'sql', 'js', 'ts', 'tf'}  # Not included in main list to avoid false matches

def extract_skills(description):
    if not description:
        return []
    
    description_lower = description.lower()
    found = []
    seen = set()
    
    for skill in TECH_SKILLS:
        # Build pattern based on skill format
        if ' ' in skill or '.' in skill:
            # Multi-word skill: match as phrase with word boundaries at ends
            pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
        else:
            # Single word: strict word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
        
        if re.search(pattern, description_lower):
            if skill not in seen:
                found.append(skill)
                seen.add(skill)
    
    return found

def run_extractor():
    print("=" * 50)
    print("🔍 SKILL EXTRACTOR STARTING...")
    print("=" * 50)

    if not os.path.exists('data/processed_jobs.db'):
        print("❌ Error: data/processed_jobs.db not found!")
        return

    conn = sqlite3.connect('data/processed_jobs.db')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS job_skills')
    c.execute('CREATE TABLE job_skills (job_id INTEGER, skill TEXT)')

    c.execute('SELECT id, description FROM cleaned_jobs WHERE description IS NOT NULL')
    jobs = c.fetchall()
    
    if not jobs:
        print("⚠️ No jobs found!")
        conn.close()
        return
    
    print(f"📥 Processing {len(jobs)} jobs...")

    total_skills = 0
    jobs_with_skills = 0
    
    # DEBUG: Track which skills match most
    skill_counts_debug = {}
    
    for job_id, description in jobs:
        skills = extract_skills(description)
        if skills:
            jobs_with_skills += 1
            for skill in skills:
                c.execute('INSERT INTO job_skills (job_id, skill) VALUES (?, ?)', (job_id, skill))
                total_skills += 1
                skill_counts_debug[skill] = skill_counts_debug.get(skill, 0) + 1

    conn.commit()

    # DEBUG: Print all found skills before showing top 25
    print(f"\n🐛 DEBUG: All {len(skill_counts_debug)} unique skills found:")
    for skill, count in sorted(skill_counts_debug.items(), key=lambda x: x[1], reverse=True):
        print(f"   {skill}: {count}")
    
    c.execute('SELECT skill, COUNT(*) as count FROM job_skills GROUP BY skill ORDER BY count DESC LIMIT 25')
    results = c.fetchall()
    conn.close()

    if results:
        max_count = max(r[1] for r in results)
        
        print(f"\n🎯 TOP 25 MOST DEMANDED SKILLS")
        print(f"   ({total_skills} mentions across {jobs_with_skills} jobs)")
        print("-" * 50)
        
        for i, (skill, count) in enumerate(results, 1):
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            percentage = (count / len(jobs)) * 100
            print(f"{i:2}. {skill.upper():22} {bar} {count:3} ({percentage:4.1f}%)")
    else:
        print("⚠️ No skills found.")

    print(f"\n✅ Done!")
    print("=" * 50)

if __name__ == "__main__":
    run_extractor()