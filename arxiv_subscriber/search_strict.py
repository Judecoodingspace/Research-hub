"""Deep search for UAV + semantic communication + multi-UAV cooperation papers"""
import csv
import re

path = r'D:\Research-hub\metadata\2026-05-18_arxiv_daily.csv'
with open(path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# STRICT search - must match BOTH uav/drone AND (semantic OR cooperative)
uav_patterns = [r'\buav\b', r'\bdrone\b', r'\bunmanned\s+aerial\b']
sem_patterns = [r'\bsemantic\s+comm', r'\bsemantic\s+transmission', r'\bsemantic\s+source', r'\bsemantic\s+coding',
               r'\btask.?oriented\s+comm', r'\btask.?oriented\s+transmission']
coop_patterns = [r'\bmulti.?uav\b', r'\bmulti.?drone\b', r'\bswarm\b', r'\bcooperative\s+uav\b',
                 r'\bcollaborative\s+uav\b', r'\bmulti.?agent.*\buav\b', r'\brelay.*\buav\b',
                 r'\bcooperative\s+perception\b', r'\bcooperative\s+sensing\b']

print("=== STRICT Match: UAV/Drone + (Semantic Communication OR Multi-UAV Cooperation) ===\n")

for row in rows:
    title = row.get('Title', '')
    summary = row.get('Abstract Note', '')
    full_text = (title + ' ' + summary).lower()
    arxiv_id = row.get('ArXiv ID', '')
    
    has_uav = any(re.search(p, full_text) for p in uav_patterns)
    has_sem = any(re.search(p, full_text) for p in sem_patterns)
    has_coop = any(re.search(p, full_text) for p in coop_patterns)
    
    if has_uav and (has_sem or has_coop):
        tags = []
        if has_sem: tags.append("语义通信")
        if has_coop: tags.append("多机协同")
        
        print(f"[{'|'.join(tags)}] {arxiv_id}")
        print(f"  {title[:130]}")
        # Show key sentence
        for sent in summary.split('. '):
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in ['uav', 'drone', 'semantic', 'cooperative', 'collaborat', 'swarm', 'multi-agent', 'relay', 'task-oriented']):
                print(f"  > {sent.strip()[:200]}...")
                break
        print()

print("--- End of strict matches ---")
