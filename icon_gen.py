from PIL import Image, ImageDraw, ImageFont
import numpy as np

def render_text(text, font_path, color=(0, 0, 0)):
    # Create initial image (large enough to fit text)
    font = ImageFont.truetype(font_path, 100)
    # Get approximate size first (not always accurate but good starting point)
    bbox = font.getbbox(text)
    # Make image twice as large to be safe
    img = Image.new('RGBA', (bbox[2] * 2, bbox[3] * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw text in center
    text_bbox = draw.textbbox((0, 0), text, font=font)
    x = (img.width - (text_bbox[2] - text_bbox[0])) // 2
    y = (img.height - (text_bbox[3] - text_bbox[1])) // 2
    draw.text((x, y), text, font=font, fill=color)

    return crop_transparency(img)

def render_text2(text, font_path, font_size, color=(0, 0, 0)):
    # Create initial image (large enough to fit text)
    font = ImageFont.truetype(font_path, font_size)
    # Get approximate size first (not always accurate but good starting point)
    bbox = font.getbbox(text)
    # Make image twice as large to be safe
    img = Image.new('RGBA', (bbox[2] * 2, bbox[3] * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw text in center
    draw.text((img.width / 2, img.height / 2), text, font=font, fill=color, anchor='mm')

    data = np.array(img)
    alpha = data[..., 3]
    non_empty_columns = np.where(alpha.max(axis=0) > 0)[0]
    offset = -((min(non_empty_columns) - 0) - (img.width - max(non_empty_columns))) // 2

    weights = alpha.sum(axis=0)
    extra_offset = img.width // 2 - int(np.sum(np.arange(img.width) * weights) / weights.sum())

    img.paste(img, (offset + int(extra_offset * 0.0), 0))
    return img

def get_horizontal_offset(text, font_path, font_size):
    # Create initial image (large enough to fit text)
    font = ImageFont.truetype(font_path, font_size)
    # Get approximate size first (not always accurate but good starting point)
    bbox = font.getbbox(text)
    # Make image twice as large to be safe
    img = Image.new('RGBA', (bbox[2] * 2, bbox[3] * 2), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw text in center
    draw.text((img.width / 2, img.height / 2), text, font=font, fill='black', anchor='mm')

    data = np.array(img)
    alpha = data[..., 3]

    # Find non-transparent pixels
    non_empty_columns = np.where(alpha.max(axis=0) > 0)[0]

    # Crop to content
    return (min(non_empty_columns) - 0) - (img.width - max(non_empty_columns))


def crop_transparency(img):
        # Convert to numpy array for faster processing
    data = np.array(img)

    # Get alpha channel
    alpha = data[..., 3]

    # Find non-transparent pixels
    non_empty_columns = np.where(alpha.max(axis=0) > 0)[0]
    non_empty_rows = np.where(alpha.max(axis=1) > 0)[0]

    # If image is empty, return a 1x1 transparent pixel
    if len(non_empty_columns) == 0 or len(non_empty_rows) == 0:
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))

    # Crop to content
    cropBox = (min(non_empty_columns),
              min(non_empty_rows),
              max(non_empty_columns) + 1,
              max(non_empty_rows) + 1)
    return img.crop(cropBox)

def resize_aspect(img, height):
    return img.resize((int(height * img.width / img.height), height))
