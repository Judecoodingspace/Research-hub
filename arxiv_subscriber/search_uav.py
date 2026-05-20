"""Search today's arXiv papers for UAV + semantic communication + multi-drone cooperation"""
import csv
import re

path = r'D:\Research-hub\metadata\2026-05-18_arxiv_daily.csv'
with open(path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# Search patterns
patterns = {
    "UAV + Multi-UAV + Swarm": [r'\buav\b', r'\bdrone\b', r'\bmulti.?uav\b', r'\bswarm\b', r'\bunmanned\b'],
    "Semantic Communication": [r'\bsemantic\s+communication\b', r'\bsemantic\s+transmission\b', r'\btask.?oriented\s+communication\b'],
    "Cooperative / Collaborative": [r'\bcooperative\b', r'\bcollaborat\w+\b', r'\bmulti.?agent\b', r'\bcoordination\b'],
    "Task-oriented + Semantic": [r'\btask.?oriented\b', r'\bsemantic\b'],
    "UAV Communication": [r'\buav\b.*\bcommunication\b', r'\bcommunication\b.*\buav\b', r'\bdrone\b.*\bcommunication\b'],
    "Resource Allocation UAV": [r'\bresource\s+allocation\b', r'\bscheduling\b', r'\boffload\w+\b'],
}

# Score-based filtering
scored_papers = []
for row in rows:
    title = row.get('Title', '').lower()
    summary = row.get('Abstract Note', '').lower()
    full_text = title + ' ' + summary
    
    score = 0
    matched_cats = []
    
    # UAV keywords
    uav_hits = sum(1 for p in patterns["UAV + Multi-UAV + Swarm"] if re.search(p, full_text))
    if uav_hits >= 1:
        score += 3
        matched_cats.append("UAV")
    
    # Semantic communication
    sem_hits = sum(1 for p in patterns["Semantic Communication"] if re.search(p, full_text))
    if sem_hits >= 1:
        score += 5
        matched_cats.append("SemComm")
    
    # Cooperative
    coop_hits = sum(1 for p in patterns["Cooperative / Collaborative"] if re.search(p, full_text))
    if coop_hits >= 1:
        score += 2
        matched_cats.append("Coop")
    
    # Task-oriented + semantic
    task_hits = sum(1 for p in patterns["Task-oriented + Semantic"] if re.search(p, full_text))
    if task_hits >= 1:
        score += 4
        matched_cats.append("TaskSem")
    
    if score >= 3:
        scored_papers.append((score, matched_cats, row))

# Sort by score
scored_papers.sort(key=lambda x: x[0], reverse=True)

# Print results
print(f"=== Papers matching UAV + Semantic + Cooperative (out of {len(rows)} total) ===")
print(f"Found {len(scored_papers)} potentially relevant papers\n")

for score, cats, row in scored_papers[:30]:
    title = row.get('Title', '')[:120]
    arxiv_id = row.get('ArXiv ID', '')
    print(f"[Score={score}] [{'|'.join(cats)}] {arxiv_id}")
    print(f"  {title}")
    # Show relevant snippet from abstract
    summary = row.get('Abstract Note', '')
    # Find first sentence mentioning UAV/drone/semantic
    sentences = summary.split('. ')
    relevant = [s for s in sentences if any(kw in s.lower() for kw in ['uav', 'drone', 'semantic', 'cooperative', 'collaborat', 'communication', 'resource'])]
    if relevant:
        snippet = relevant[0][:200]
        print(f"  Abstract: {snippet}...")
    print()
