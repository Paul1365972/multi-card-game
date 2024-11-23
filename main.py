import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from icon_gen import render_text, crop_transparency, resize_aspect, render_text2

CARD_WIDTH = 697
CARD_HEIGHT = 1075
OFFSET = 0.1
SUIT_OFFSET = 0.075
TEXT_SIZE = 0.1
SUIT_SIZE = 0.08

RED = (255, 0, 0)
#RED = (224, 32, 32)
BLACK = (0, 0, 0)
#BLACK = (32, 32, 32)

def preprocess_svg_assets():
    """Convert all SVG templates to PNG files if not already cached"""
    # Process SVGs
    for suit in ['diamonds', 'hearts', 'spades', 'clubs']:
        svg_path = f'./assets/suits_svgs/{suit}.svg'
        png_path = f'./assets/suits/{suit}.png'

        if not os.path.exists(png_path):
            print(f"Generating PNG for {suit}...")

            result = subprocess.run([
                'inkscape',
                '--export-type=png',
                f'--export-filename={png_path}',
                f'--export-width=1024',
                f'--export-height=1024',
                svg_path
            ])
            if result.returncode != 0:
                raise Exception("Inkscape failed to run")

            img = Image.open(png_path).convert('RGBA')
            data = [(255, 255, 255, a) for _, _, _, a in list(img.getdata())]
            img.putdata(data)
            img.save(png_path, 'PNG')

def generate_card(rank, suit, font_path):
    """Generate a single playing card"""
    # Create card and load assets
    card = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), 'white')
    draw = ImageDraw.Draw(card)
    color = RED if suit in ['diamonds', 'hearts'] else BLACK

    # Load suit image
    suit_img = Image.open(f'./assets/suits/{suit}.png').resize((int(SUIT_SIZE * CARD_HEIGHT), int(SUIT_SIZE * CARD_HEIGHT)))
    suit_img.putdata([color + (a,) for _,_,_,a in suit_img.getdata()])

    # Create rank image
    text_img = render_text2(rank, font_path, int(TEXT_SIZE * CARD_HEIGHT), color)

    # Add elements to top-left corner
    draw.rounded_rectangle(((0, 0), (CARD_WIDTH, CARD_HEIGHT)), radius=int(CARD_HEIGHT * 0.07), width=3, outline='black')

    card.paste(text_img, (int((OFFSET) * CARD_HEIGHT) - text_img.width // 2, int((OFFSET) * CARD_HEIGHT)- text_img.height // 2), text_img)
    card.paste(suit_img, (int((OFFSET) * CARD_HEIGHT) - suit_img.width // 2, int((OFFSET + SUIT_OFFSET) * CARD_HEIGHT)- suit_img.height // 2), suit_img)

    card.paste(text_img, (CARD_WIDTH - int((OFFSET) * CARD_HEIGHT) - text_img.width // 2, int((OFFSET) * CARD_HEIGHT)- text_img.height // 2), text_img)
    card.paste(suit_img, (CARD_WIDTH - int((OFFSET) * CARD_HEIGHT) - suit_img.width // 2, int((OFFSET + SUIT_OFFSET) * CARD_HEIGHT)- suit_img.height // 2), suit_img)

    # Rotate and add to bottom-right corner
    upper = card.crop((0, 0, CARD_WIDTH, CARD_HEIGHT // 2)).rotate(180)
    card.paste(upper, (0, CARD_HEIGHT - upper.height))

    return card

def compile_to_pdf(card_images, output_path):
    """Compile all cards into a PDF with CMYK conversion"""
    c = canvas.Canvas(output_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))

    # TODO: color_profile = './assets/color_profiles/Coated_Fogra39L_VIGC_300.icc'

    for card in card_images:
        card = card.convert('CMYK')
        card_reader = ImageReader(card)
        c.drawImage(card_reader, 0, 0, width=CARD_WIDTH, height=CARD_HEIGHT)
        c.showPage()

    c.save()

def main():
    # Process assets and generate deck
    print("Preprocessing SVG assets...")
    preprocess_svg_assets()

    font_path = './assets/fonts/Battambang/Battambang-Bold.ttf'
    #font_path = './assets/fonts/Hanuman/Hanuman-Bold.ttf'
    #font_path = 'assets/fonts/Roboto_Slab/static/RobotoSlab-Bold.ttf'

    print("Generating cards...")
    deck = []
    for suit in ['diamonds', 'hearts', 'spades', 'clubs']:
        for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            deck.append(generate_card(rank, suit, font_path))

    print("Compiling PDF...")
    output_pdf = f'./playing_cards_front.pdf'
    compile_to_pdf(deck, output_pdf)
    print(f"PDF created successfully at: {output_pdf}")

if __name__ == "__main__":
    main()
