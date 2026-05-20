"""Quick test for arXiv fetcher"""
import sys
sys.path.insert(0, r'D:\Research-hub\arxiv_subscriber')
from fetcher import _arxiv_request, _parse_arxiv_response, ARXIV_API_BASE
import urllib.parse

params = {
    'search_query': 'UAV semantic communication',
    'sortBy': 'submittedDate',
    'sortOrder': 'descending',
    'start': 0,
    'max_results': 5,
}
url = ARXIV_API_BASE + '?' + urllib.parse.urlencode(params)
print('Fetching:', url[:100])
xml = _arxiv_request(url)
papers = _parse_arxiv_response(xml)
print(f'Total: {len(papers)} papers')
for p in papers[:5]:
    print(f'  [{p.get("published_date", "?")}] {p.get("title", "?")[:120]}')
    print(f'    arxiv_id={p.get("arxiv_id", "?")}, authors={p.get("first_author", "?")}')
