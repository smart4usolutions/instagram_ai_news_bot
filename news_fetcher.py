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
    "entertainment",
    "sports"
]

# file to store last topic index
INDEX_FILE = "topic_index.txt"


def get_next_topic():
    try:
        # Check if file exists, create if not
        if not os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "w") as f:
                f.write("0")
            print("File created successfully.")

        # Try reading file
        with open(INDEX_FILE, "r") as f:
            index = int(f.read())
        print("File read successfully. old index value is ",index)

        topic = topics[index]

        # Update index
        index = (index + 1) % len(topics)

        # Try writing file
        # with open(INDEX_FILE, "w") as f:
        #     f.write(str(index))
        # print("File written successfully. old index value is ",index)
        with open(INDEX_FILE, "w") as f:
            f.write(str(index))
            f.flush()
            os.fsync(f.fileno())

        # 🔥 Read immediately after writing
        with open(INDEX_FILE, "r") as f:
            print("File after write:", f.read())

        return topic

    except Exception as e:
        print("Error accessing file:", e)
        return None



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
        source = article["source"]["name"]

        full_text = description + " " + content

        return {
            "title": article["title"],
            "image": article["urlToImage"],
            "category": topic,
            "source":source,
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
