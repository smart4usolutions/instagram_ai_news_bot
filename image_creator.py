import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import textwrap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 1080
HEIGHT = 1350  # Instagram 4:5


# ----------------------------
# RESIZE IMAGE (NO STRETCH)
# ----------------------------
def resize_cover(image, target_width, target_height):
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2

    return image.crop((left, top, left + target_width, top + target_height))


# ----------------------------
# LOAD IMAGE (ROBUST)
# ----------------------------
def load_image(image_url):
    try:
        print("IMAGE URL:", image_url)

        if not image_url:
            raise Exception("Empty image URL")

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(
            image_url,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        if response.status_code != 200:
            raise Exception("Bad response")

        img = Image.open(BytesIO(response.content)).convert("RGB")
        print("✅ Image loaded")

    except Exception as e:
        print("❌ Image load failed:", e)
        img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))

    return img


# ----------------------------
# STRONG BOTTOM GRADIENT
# ----------------------------
def apply_bottom_gradient(image):
    gradient = Image.new("L", (1, HEIGHT))

    for y in range(HEIGHT):
        if y < HEIGHT * 0.3:
            value = 0
        else:
            value = int(255 * ((y - HEIGHT * 0.4) / (HEIGHT * 0.6)))

        gradient.putpixel((0, y), value)

    alpha = gradient.resize((WIDTH, HEIGHT))
    black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))

    return Image.composite(black, image, alpha)


# ----------------------------
# TEXT WRAP
# ----------------------------
def wrap_text(text, width=30):
    return "\n".join(textwrap.wrap(text, width))


# ----------------------------
# DYNAMIC FONT
# ----------------------------
def get_dynamic_font(text, font_path, max_width, max_size=80, min_size=30):
    for size in range(max_size, min_size, -2):
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return font

    return ImageFont.truetype(font_path, min_size)


# ----------------------------
# MAIN FUNCTION
# ----------------------------
def create_post_image(title, image_url, category):

    # Load & prepare image
    bg = load_image(image_url)
    bg = resize_cover(bg, WIDTH, HEIGHT)
    bg = bg.filter(ImageFilter.GaussianBlur(2))
    bg = apply_bottom_gradient(bg)

    draw = ImageDraw.Draw(bg)

    # Fonts
    font_bold_path = os.path.join(BASE_DIR, "fonts/ARIALBD.TTF")
    font_regular_path = os.path.join(BASE_DIR, "fonts/ARIAL.TTF")

    font_page = ImageFont.truetype(font_bold_path, 42)
    font_category = ImageFont.truetype(font_bold_path, 50)

    # ----------------------------
    # PAGE NAME (TOP CENTER)
    # ----------------------------
    page_name = "Follow " + os.getenv("PAGE_NAME")

    bbox = draw.textbbox((0, 0), page_name, font=font_page)
    text_width = bbox[2] - bbox[0]

    x = (WIDTH - text_width) // 2
    y = 30

    draw.text((x+2, y+2), page_name, font=font_page, fill="black")
    draw.text((x, y), page_name, font=font_page, fill="white")

    # ----------------------------
    # TITLE (CENTERED)
    # ----------------------------
    # ----------------------------
    # PREP TEXT
    # ----------------------------
    title = wrap_text(title, 24)

    max_width = WIDTH - 120
    max_total_height = int(HEIGHT * 0.40)

    bottom_padding = 80
    gap = 30

    # ----------------------------
    # FIND BEST TITLE FONT (FILL SPACE)
    # ----------------------------
    best_font = None

    for size in range(90, 30, -2):
        font = ImageFont.truetype(font_bold_path, size)

        title_bbox = draw.multiline_textbbox(
            (0, 0), title, font=font, spacing=12
        )

        title_h = title_bbox[3] - title_bbox[1]

        # estimate category height
        cat_font = ImageFont.truetype(font_bold_path, 50)
        cat_bbox = draw.textbbox((0, 0), category.upper(), font=cat_font)
        cat_h = (cat_bbox[3] - cat_bbox[1]) + 30  # padding

        total_h = title_h + gap + cat_h

        if total_h <= max_total_height:
            best_font = font
            break

    if best_font is None:
        best_font = ImageFont.truetype(font_bold_path, 40)

    # ----------------------------
    # FINAL SIZE CALC
    # ----------------------------
    title_bbox = draw.multiline_textbbox((0, 0), title, font=best_font, spacing=12)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    # CATEGORY
    category_text = category.upper()
    font_category = ImageFont.truetype(font_bold_path, 50)

    cat_bbox = draw.textbbox((0, 0), category_text, font=font_category)
    cat_text_w = cat_bbox[2] - cat_bbox[0]
    cat_text_h = cat_bbox[3] - cat_bbox[1]

    padding_x = 40
    padding_y = 20

    box_w = cat_text_w + padding_x * 2
    box_h = cat_text_h + padding_y * 2

    # ----------------------------
    # BOTTOM ANCHOR POSITIONING
    # ----------------------------
    current_y = HEIGHT - bottom_padding

    # TITLE position
    title_y = current_y - title_h
    title_x = (WIDTH - title_w) // 2

    # CATEGORY position (above title)
    cat_y = title_y - gap - box_h
    cat_x = (WIDTH - box_w) // 2

    # ----------------------------
    # DRAW CATEGORY BOX
    # ----------------------------
    draw.rectangle(
        [cat_x, cat_y, cat_x + box_w, cat_y + box_h],
        fill=(255, 60, 0)
    )

    # ✅ PERFECT CENTER (FIXED)
    text_x = cat_x + (box_w - cat_text_w) // 2
    text_y = cat_y + (box_h - cat_text_h) // 2 - 2   # 👈 micro-adjust

    draw.text(
        (text_x, text_y),
        category_text,
        font=font_category,
        fill="white"
    )

    # ----------------------------
    # DRAW TITLE
    # ----------------------------
    draw.multiline_text(
        (title_x+3, title_y+3),
        title,
        font=best_font,
        fill="black",
        spacing=12,
        align="center"
    )

    draw.multiline_text(
        (title_x, title_y),
        title,
        font=best_font,
        fill="white",
        spacing=12,
        align="center"
    )


    # ----------------------------
    # SAVE IMAGE
    # ----------------------------
    output_path = "generated_posts/post.png"
    os.makedirs("generated_posts", exist_ok=True)

    bg.save(output_path)

    print("✅ IMAGE CREATED:", output_path)

    return output_path