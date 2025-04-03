import feedparser
import time
from flask import Flask, render_template, request
from flask_caching import Cache

app = Flask(__name__)

# Configure caching (simple in-memory caching)
app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 600  # Cache timeout in seconds (5 min)
cache = Cache(app)
cache.init_app(app)

FEEDS = {
    "medium_tech": "https://medium.com/feed/tag/tech",
    "medium_technology": "https://medium.com/feed/tag/technology",
    "medium_tech_news": "https://medium.com/feed/tag/tech-news",
    "dev.to": "https://dev.to/feed/",
    "stackoverflow": "https://stackoverflow.blog/feed/",
    "hackernews": "https://hnrss.org/frontpage",
    "css-tricks": "https://css-tricks.com/feed/",
    "Github": "https://github.blog/feed/",
}


@cache.cached(timeout=600)  # Cache the function for 10 minutes
def fetch_articles():
    """Fetch and parse RSS feeds, returning sorted articles."""
    articles = []
    for source, feed in FEEDS.items():
        try:
            parsed_feed = feedparser.parse(feed)
            entries = [(source, entry) for entry in parsed_feed.entries]
            articles.extend(entries)
        except Exception as e:
            print(f"Error fetching {source}: {e}")
            continue

    return sorted(
        articles,
        key=lambda x: time.mktime(x[1].published_parsed)
        if hasattr(x[1], "published_parsed")
        else 0,
        reverse=True,
    )


@app.errorhandler(404)
def _404page(e):
    return render_template("404.html"), 404


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/feeds")
def index():
    """Home page with cached articles and pagination."""
    articles = fetch_articles()

    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)
    total_pages = (total_articles + per_page - 1) // per_page  # Avoids float issues

    start, end = (page - 1) * per_page, page * per_page
    paginated_articles = articles[start:end]

    return render_template(
        "feeds.html", articles=paginated_articles, page=page, total_pages=total_pages
    )


@app.route("/search")
def search():
    """Search articles using cached data for speed."""
    query = request.args.get("q", "").lower()
    articles = fetch_articles()

    results = [
        article
        for article in articles
        if query in article[1].title.lower()
        or query in article[0].lower()
        or query in article[1].get("author", "").lower()
    ]

    return render_template("search_results.html", articles=results, query=query)


if __name__ == "__main__":
    app.run(debug=True)
