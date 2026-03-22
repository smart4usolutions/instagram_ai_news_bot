import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# topics rotation
topics = [
    "artificial intelligence",
    "startup funding",
    "cryptocurrency",
    "technology",
    "india",
    "finance market",
    "entertainment industry"
]

# file to store last topic index
INDEX_FILE = "topic_index.txt"


def get_next_topic():

    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w") as f:
            f.write("0")

    with open(INDEX_FILE, "r") as f:
        index = int(f.read())

    topic = topics[index]

    index = (index + 1) % len(topics)

    with open(INDEX_FILE, "w") as f:
        f.write(str(index))

    return topic


def get_news():

    topic = get_next_topic()

    print("Fetching news for topic:", topic)

    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=1&sortBy=publishedAt&apiKey={NEWS_API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "articles" in data and len(data["articles"]) > 0:

        article = data["articles"][0]

        description = article.get("description") or ""
        content = article.get("content") or ""

        full_text = description + " " + content

        return {
            "title": article["title"],
            "image": article["urlToImage"],
            "category": topic,
            "description": article["description"]
        }

    else:
        print("News API Error:", data)

        return {
            "title": article["title"],
            "description": article.get("description"),
            "image": article["urlToImage"],
            "category": topic
        }
