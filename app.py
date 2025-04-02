import feedparser
from flask import Flask, render_template, request


app = Flask(__name__)


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


@app.route("/")
def index():
    articles = []
    for source, feed in FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    articles = sorted(articles, key=lambda x: x[1].published_parsed, reverse=True)

    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template(
        "index.html",
        articles=paginated_articles,
        page=page,
        total_pages=total_articles // per_page + 1,
    )


@app.route("/search")
def search():
    query = request.args.get("q")

    articles = []
    for source, feed in FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    results = [
        article for article in articles if query.lower() in article[1].title.lower() or  query.lower()  in  article[0] or article[0] in query.lower()
    ]

    return render_template("search_results.html", articles=results, query=query)


if __name__ == "__main__":
    app.run()
