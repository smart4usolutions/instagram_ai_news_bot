from news_fetcher import get_news
from ai_writer import generate_caption
from image_creator import create_post_image
from upload_image import upload_image
from instagram_post import post_to_instagram

news = get_news()

print("\nNEWS:", news["title"])
print("\nDISC:", news.get("description"))

caption = generate_caption(
    news["title"],
    news.get("description"),
    news["category"]
)

print("\nINSTAGRAM CAPTION:\n")
print(caption)

image_path = create_post_image(
    news["title"],
    news["image"],
    news["category"]
)

print("\nIMAGE CREATED:", image_path)

#upload image
image_url = upload_image(image_path)
print("Uploaded URL:", image_url)

#Post to Instagram
post_to_instagram(image_url, caption)