# Usage: poetry run python search.py "best vps providers"
import json
from duckduckgo_search import ddg

def search(query, num_results=8):
    """Return the results of a duckduckgo search"""
    search_results = []
    if not query:
        return json.dumps(search_results)

    for j in ddg(query, max_results=num_results):
        search_results.append(j)

    return json.dumps(search_results, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    import sys
    query = sys.argv[1]
    print(search(query))
