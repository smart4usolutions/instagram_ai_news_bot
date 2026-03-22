from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime
import textwrap
from headline_formatter import format_headline
import os


def center_text(draw, text, font, y, img_width, color="white"):
    bbox = draw.textbbox((0,0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (img_width - text_width) / 2
    draw.text((x, y), text, fill=color, font=font)


def create_post_image(headline, image_url, category):

    width = 1080
    height = 1080
    center_x = width / 2

    # download background image
    response = requests.get(image_url, timeout=10)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img = img.resize((width, height))

    draw = ImageDraw.Draw(img)

    # dark gradient bottom
    gradient = Image.new("RGBA", (width, height), (0,0,0,0))
    gdraw = ImageDraw.Draw(gradient)

    gradient_height = int(height * 0.45)  # 40% of image
    for i in range(gradient_height):
        opacity = int(255 * (i / gradient_height))
        gdraw.rectangle(
            (0, height - gradient_height + i, width, height - gradient_height + i + 1),
            fill=(0, 0, 0, opacity)
        )


    img = Image.alpha_composite(img.convert("RGBA"), gradient)

    draw = ImageDraw.Draw(img)

    # fonts
    try:
        font_headline = ImageFont.truetype("arialbd.ttf", 70)
        font_category = ImageFont.truetype("arialbd.ttf", 42)
        font_page = ImageFont.truetype("arialbd.ttf", 45)
        font_date = ImageFont.truetype("arial.ttf", 35)
    except:
        font_headline = ImageFont.load_default()
        font_category = ImageFont.load_default()
        font_page = ImageFont.load_default()
        font_date = ImageFont.load_default()

    # page name
    pageName = os.getenv("pageName")
    draw.text(
    (40, 40),
    pageName,
    fill="white",
    font=font_page,
    stroke_width=3,
    stroke_fill="black"
    )

    # date with border
    date_text = datetime.now().strftime("%d %b %Y")
    date_bbox = draw.textbbox((0,0), date_text, font=font_date)
    date_width = date_bbox[2] - date_bbox[0]

    draw.text(
        (width - date_width - 40, 40),
        date_text,
        fill="white",
        font=font_date,
        stroke_width=3,
        stroke_fill="black"
    )

    # category
    category_text = category.upper()

    # get exact bbox
    bbox = draw.textbbox((0, 0), category_text, font=font_category)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    category_y = height - 470
    x = (width - text_width) / 2

    padding_x = 20
    padding_y = 12

    # draw background box FIRST
    draw.rectangle(
        (
            x - padding_x,
            category_y - padding_y,
            x + text_width + padding_x,
            category_y + text_height + padding_y
        ),
        fill=(0, 0, 0, 200)
    )

    # draw text EXACTLY aligned
    draw.text(
        (x - bbox[0], category_y - bbox[1]),
        category_text,
        fill="white",
        font=font_category
    )

    # separator line
    line_width = 350
    line_y = category_y + 45
    draw.line(
        (center_x - line_width/2, line_y, center_x + line_width/2, line_y),
        fill="white",
        width=4
    )

    # headline wrapping
    wrapped = textwrap.wrap(headline.upper(), width=24)
    # headline = format_headline(headline)
    # wrapped = headline.split("\n")


    y = line_y + 40

    for line in wrapped:

        bbox = draw.textbbox((0,0), line, font=font_headline)
        text_width = bbox[2] - bbox[0]

        x = (width - text_width) / 2

        draw.text((x, y), line, fill="white", font=font_headline)

        y += 80

    # ensure folder exists
    folder = "generated_posts"
    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/post.png"

    img.convert("RGB").save(filename)

    return filename
