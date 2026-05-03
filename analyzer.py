import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

os.makedirs('data', exist_ok=True)

def run_analyzer():
    print("=" * 50)
    print("📊 ANALYZER STARTING...")
    print("=" * 50)

    if not os.path.exists('data/processed_jobs.db'):
        print("❌ Error: data/processed_jobs.db not found. Run the pipeline first!")
        return

    conn = sqlite3.connect('data/processed_jobs.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cleaned_jobs'")
    if not c.fetchone():
        print("❌ Error: cleaned_jobs table not found. Run cleaner.py first!")
        conn.close()
        return

    c.execute('SELECT COUNT(*) FROM cleaned_jobs')
    total_jobs = c.fetchone()[0] or 0

    c.execute('SELECT COUNT(DISTINCT company) FROM cleaned_jobs')
    unique_companies = c.fetchone()[0] or 0

    c.execute('SELECT COUNT(DISTINCT location) FROM cleaned_jobs')
    unique_locations = c.fetchone()[0] or 0

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_skills'")
    has_skills = c.fetchone() is not None
    unique_skills = 0
    if has_skills:
        c.execute('SELECT COUNT(DISTINCT skill) FROM job_skills')
        unique_skills = c.fetchone()[0] or 0

    c.execute('SELECT quality_score FROM cleaned_jobs')
    scores = [row[0] for row in c.fetchall() if row[0] is not None]

    print(f"\n📈 OVERALL STATS")
    print("-" * 40)
    print(f"Total Jobs:        {total_jobs}")
    print(f"Unique Companies:  {unique_companies}")
    print(f"Unique Locations:  {unique_locations}")
    print(f"Unique Skills:     {unique_skills}")
    if scores:
        print(f"Avg Quality Score: {np.mean(scores):.1f}/100")

    if total_jobs == 0:
        print("\n⚠️  No jobs to analyze!")
        conn.close()
        return

    skill_data = []
    if has_skills:
        c.execute("SELECT skill, COUNT(*) as count FROM job_skills GROUP BY skill ORDER BY count DESC LIMIT 15")
        skill_data = c.fetchall()

    c.execute("SELECT company, COUNT(*) as count FROM cleaned_jobs GROUP BY company ORDER BY count DESC LIMIT 10")
    company_data = c.fetchall()

    c.execute("SELECT location, COUNT(*) as count FROM cleaned_jobs GROUP BY location ORDER BY count DESC LIMIT 10")
    location_data = c.fetchall()

    c.execute("SELECT COUNT(*) FROM cleaned_jobs WHERE scraped_date >= date('now', '-7 days')")
    recent_jobs = c.fetchone()[0] or 0

    conn.close()

    print(f"\n🏢 TOP HIRING COMPANIES")
    print("-" * 40)
    for i, (company, count) in enumerate(company_data, 1):
        print(f"{i:2}. {company[:35]:35} {count} jobs")

    print(f"\n📍 TOP LOCATIONS")
    print("-" * 40)
    for i, (location, count) in enumerate(location_data, 1):
        print(f"{i:2}. {location[:35]:35} {count} jobs")

    print(f"\n📅 RECENT ACTIVITY")
    print("-" * 40)
    print(f"Jobs posted in last 7 days: {recent_jobs}")

    # ============================================
    # FIGURE 1: Skills + Companies (Side by Side)
    # ============================================
    print(f"\n📊 Generating Figure 1: Skills & Companies...")

    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig1.suptitle('Job Market Insights - Part 1: Skills & Companies', 
                  fontsize=16, fontweight='bold', y=0.98)

    # Chart 1: Top Skills
    if skill_data and len(skill_data) > 0:
        skills, skill_counts = zip(*skill_data)
        colors_skills = plt.cm.viridis(np.linspace(0.2, 0.8, len(skills)))
        
        y_pos = np.arange(len(skills))
        bars = ax1.barh(y_pos, skill_counts, color=colors_skills, height=0.6, edgecolor='white', linewidth=0.5)
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([s.title() for s in skills], fontsize=9)
        ax1.set_xlabel('Number of Job Postings', fontsize=10)
        ax1.set_title('Top 15 Most Demanded Skills', fontweight='bold', fontsize=12, pad=10)
        ax1.invert_yaxis()
        
        for bar, count in zip(bars, skill_counts):
            ax1.text(bar.get_width() + max(skill_counts) * 0.01, 
                    bar.get_y() + bar.get_height()/2, 
                    str(count), va='center', fontsize=8, fontweight='bold')
        
        ax1.xaxis.grid(True, linestyle='--', alpha=0.3)
        ax1.set_axisbelow(True)
    else:
        ax1.text(0.5, 0.5, 'No skill data available', ha='center', va='center', fontsize=11)
        ax1.set_title('Top 15 Most Demanded Skills', fontweight='bold', fontsize=12, pad=10)

    # Chart 2: Top Companies
    companies, company_counts = zip(*company_data)
    colors_comp = plt.cm.plasma(np.linspace(0.2, 0.8, len(companies)))
    
    y_pos = np.arange(len(companies))
    bars = ax2.barh(y_pos, company_counts, color=colors_comp, height=0.6, edgecolor='white', linewidth=0.5)
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([c[:25] for c in companies], fontsize=9)
    ax2.set_xlabel('Number of Job Postings', fontsize=10)
    ax2.set_title('Top 10 Hiring Companies', fontweight='bold', fontsize=12, pad=10)
    ax2.invert_yaxis()
    
    for bar, count in zip(bars, company_counts):
        ax2.text(bar.get_width() + max(company_counts) * 0.01, 
                bar.get_y() + bar.get_height()/2, 
                str(count), va='center', fontsize=8, fontweight='bold')
    
    ax2.xaxis.grid(True, linestyle='--', alpha=0.3)
    ax2.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig1.savefig('data/insights_dashboard_part1.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()  # FIX: removed fig1 argument
    print("✅ Figure 1 saved: data/insights_dashboard_part1.png")

    # ============================================
    # FIGURE 2: Locations + Quality (Side by Side)
    # ============================================
    print(f"\n📊 Generating Figure 2: Locations & Quality...")

    fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 9))
    fig2.suptitle('Job Market Insights - Part 2: Locations & Quality', 
                  fontsize=16, fontweight='bold', y=0.98)

    # Chart 3: Location Distribution - DONUT CHART
    locations, location_counts = zip(*location_data)
    
    total_loc = sum(location_counts)
    threshold = total_loc * 0.03
    
    filtered_locs = []
    filtered_counts = []
    other_count = 0
    
    for loc, cnt in zip(locations, location_counts):
        if cnt >= threshold:
            filtered_locs.append(loc[:15])
            filtered_counts.append(cnt)
        else:
            other_count += cnt
    
    if other_count > 0:
        filtered_locs.append('Others')
        filtered_counts.append(other_count)
    
    colors_loc = plt.cm.coolwarm(np.linspace(0.15, 0.85, len(filtered_locs)))
    
    wedges, texts, autotexts = ax3.pie(
        filtered_counts,
        labels=filtered_locs,
        autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
        colors=colors_loc,
        startangle=90,
        textprops={'fontsize': 9},
        pctdistance=0.75,
        labeldistance=1.12,
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)
    
    ax3.set_title('Job Distribution by Location', fontweight='bold', fontsize=12, pad=10)
    ax3.text(0, 0, f'{total_jobs}\nJobs', ha='center', va='center', 
            fontsize=13, fontweight='bold', color='#333333')

    # Chart 4: Quality Score Distribution
    if scores:
        n, bins, patches = ax4.hist(scores, bins=12, color='steelblue', 
                                     edgecolor='black', alpha=0.75, linewidth=1.2)
        
        for patch, height in zip(patches, n):
            if height == max(n):
                patch.set_facecolor('#2E86AB')
            else:
                patch.set_facecolor('#A8DADC')
        
        mean_score = np.mean(scores)
        ax4.axvline(mean_score, color='#E63946', linestyle='--', 
                   linewidth=2.5, label=f'Mean: {mean_score:.1f}')
        ax4.axvline(np.median(scores), color='#F4A261', linestyle=':', 
                   linewidth=2, label=f'Median: {np.median(scores):.1f}')
        
        ax4.set_xlabel('Quality Score', fontsize=10)
        ax4.set_ylabel('Number of Jobs', fontsize=10)
        ax4.set_title('Quality Score Distribution', fontweight='bold', fontsize=12, pad=10)
        ax4.legend(loc='upper left', fontsize=9)
        ax4.set_xlim(0, 105)
        ax4.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax4.set_axisbelow(True)
    else:
        ax4.text(0.5, 0.5, 'No quality score data', ha='center', va='center', fontsize=11)
        ax4.set_title('Quality Score Distribution', fontweight='bold', fontsize=12, pad=10)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig2.savefig('data/insights_dashboard_part2.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()  # FIX: removed fig2 argument
    print("✅ Figure 2 saved: data/insights_dashboard_part2.png")

    # Save summary CSV
    summary_data = {
        'Metric': ['Total Jobs', 'Unique Companies', 'Unique Locations', 'Unique Skills', 'Recent Jobs (7d)', 'Avg Quality Score'],
        'Value': [total_jobs, unique_companies, unique_locations, unique_skills, recent_jobs, round(np.mean(scores), 1) if scores else 0]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('data/summary_stats.csv', index=False)
    print(f"\n✅ Summary saved: data/summary_stats.csv")

    print(f"\n✅ Analysis complete! Generated 2 figures.")
    print("=" * 50)

if __name__ == "__main__":
    run_analyzer()