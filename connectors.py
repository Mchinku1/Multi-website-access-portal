
from urllib.parse import quote
import requests

HEADERS = {
    "User-Agent": "MultiWebsitePortal/1.0 (educational project)"
}

TIMEOUT = 15

# Direct links: these open the original website.
WEBSITES = [
    {"name": "Google", "category": "Search",
     "url": "https://www.google.com/"},
    {"name": "Bing", "category": "Search",
     "url": "https://www.bing.com/"},
    {"name": "Wikipedia", "category": "Education",
     "url": "https://www.wikipedia.org/"},
    {"name": "Wikimedia Commons", "category": "Education",
     "url": "https://commons.wikimedia.org/"},
    {"name": "Google Scholar", "category": "Research",
     "url": "https://scholar.google.com/"},
    {"name": "PubMed", "category": "Health",
     "url": "https://pubmed.ncbi.nlm.nih.gov/"},
    {"name": "WHO", "category": "Health",
     "url": "https://www.who.int/"},
    {"name": "Worldometer", "category": "Statistics",
     "url": "https://www.worldometers.info/"},
    {"name": "Our World in Data", "category": "Statistics",
     "url": "https://ourworldindata.org/"},
    {"name": "World Bank Data", "category": "Finance",
     "url": "https://data.worldbank.org/"},
    {"name": "Open-Meteo", "category": "Weather",
     "url": "https://open-meteo.com/"},
    {"name": "Reuters", "category": "News",
     "url": "https://www.reuters.com/"},
    {"name": "BBC News", "category": "News",
     "url": "https://www.bbc.com/news"},
    {"name": "The Guardian", "category": "News",
     "url": "https://www.theguardian.com/"},
    {"name": "GitHub", "category": "Development",
     "url": "https://github.com/"},
    {"name": "Stack Overflow", "category": "Development",
     "url": "https://stackoverflow.com/"},
    {"name": "Open Library", "category": "Books",
     "url": "https://openlibrary.org/"},
    {"name": "Hacker News", "category": "Technology",
     "url": "https://news.ycombinator.com/"},
    {"name": "YouTube", "category": "Video",
     "url": "https://www.youtube.com/"},
    {"name": "Internet Archive", "category": "Archives",
     "url": "https://archive.org/"},
]


def request_json(url, params=None):
    """Retrieve JSON from a configured public API."""
    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def search_wikipedia(query, limit=10):
    """Search Wikipedia articles."""
    data = request_json(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
        },
    )

    results = []

    for item in data.get("query", {}).get("search", []):
        title = item.get("title", "")
        results.append({
            "source": "Wikipedia",
            "title": title,
            "description": item.get("snippet", ""),
            "url": (
                "https://en.wikipedia.org/wiki/"
                + quote(title.replace(" ", "_"), safe="_()")
            ),
        })

    return results


def search_open_library(query, limit=10):
    """Search books using Open Library."""
    data = request_json(
        "https://openlibrary.org/search.json",
        {"q": query, "limit": limit},
    )

    results = []

    for item in data.get("docs", []):
        key = item.get("key", "")
        results.append({
            "source": "Open Library",
            "title": item.get("title", "Untitled"),
            "description": ", ".join(
                item.get("author_name", [])[:3]
            ),
            "url": "https://openlibrary.org" + key
            if key.startswith("/works/") else
            "https://openlibrary.org/",
        })

    return results


def search_hacker_news(query, limit=10):
    """Search public Hacker News stories."""
    data = request_json(
        "https://hn.algolia.com/api/v1/search",
        {"query": query, "hitsPerPage": limit},
    )

    results = []

    for item in data.get("hits", []):
        url = item.get("url") or (
            "https://news.ycombinator.com/item?id="
            + str(item.get("objectID", ""))
        )

        results.append({
            "source": "Hacker News",
            "title": item.get("title") or "Untitled",
            "description": (
                f"Points: {item.get('points', 0)} | "
                f"Comments: {item.get('num_comments', 0)}"
            ),
            "url": url,
        })

    return results


SEARCH_PROVIDERS = {
    "Wikipedia": search_wikipedia,
    "Open Library": search_open_library,
    "Hacker News": search_hacker_news,
}


def search_provider(provider, query, limit=10):
    """Run a search against one supported provider."""
    if provider not in SEARCH_PROVIDERS:
        raise ValueError("Unsupported search provider.")

    if not query.strip():
        return []

    return SEARCH_PROVIDERS[provider](query.strip(), limit)
