# Dependencies: pip install pillow reportlab pdf2image opencv-python numpy tqdm pathlib
# Also requires system package: poppler-utils (on Linux, use `sudo apt install poppler-utils`)

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from tqdm import tqdm
import pdf2image

# --- Configuration & Styling (Adjust as needed) ---
# High Resolution Settings
DPI = 600
SAVE_QUALITY = 95
PDF_SAVE_OPTIONS = {'optimize': True}

# Font (MUST be provided by user or set to a system font, 
# e.g., on macOS 'AppleGothic', on Windows 'Malgun Gothic', on Linux 'NanumGothic')
# A characterful Korean font matching the 'cellup' reference is recommended.
# Recommended: An open-source hand-written style font, e.g., 'Maplestory-Bold.ttf' or similar.
KOREAN_FONT_PATH = "korean_font.ttf"  # Set path to a .ttf file in the same directory
DEFAULT_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf" # Fallback, no Korean

# Tag Positioning & Design (Tweaking may be necessary for perfect alignment)
TAG_TEXT = "고리"
TAG_FONT_SIZE = 48 # High-res points
TAG_COLOR = (255, 255, 255)  # White text
TAG_BG_COLOR = (240, 240, 240, 230) # Light grey, slight transparency
TAG_PADDING = 15
TAG_CORNER_RADIUS = 10

# Based on a standard card layout, position dog's head vicinity. Adjust percentages.
DOG_HEAD_POS_ESTIMATE = (0.72, 0.78) # (x, y) relative to PDF image width and height
CONNECTOR_COLOR = (210, 210, 210) # Light grey connector
CONNECTOR_THICKNESS = 4
CONNECTOR_WOBBLE = 2 # Pixels of wobble for hand-drawn effect
CONNECTOR_POINTS_COUNT = 5 # For a smooth curve

# File Paths (relative to script root)
INPUT_PDF_FILENAME = "애드플랜터스_추석_인사_카드_highres.pdf"
REFERENCE_TAG_IMAGE = "20260924_200936.jpg" # Style reference
OUTPUT_DIR_NAME = "output"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
MODIFIED_PDF_FILENAME = f"modified_{INPUT_PDF_FILENAME.replace('.pdf', '')}_{TIMESTAMP}.pdf"

# --- Main Script ---
def setup_logger(log_file: Path) -> logging.Logger:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)])
    return logging.getLogger("gori_name_tag")

def create_gori_tag(font_path: str, size: int, text: str, 
                   color: Tuple[int, int, int], bg_color: Tuple[int, int, int, int], 
                   padding: int, radius: int) -> Image.Image:
    """Creates a stylized name tag based on parameters."""
    try:
        font = ImageFont.truetype(font_path, size)
    except IOError:
        logging.warning(f"Could not load font at {font_path}, using fallback.")
        font = ImageFont.load_default()
    
    # Calculate text size
    dummy_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_w, text_h = draw.textsize(text, font=font)
    
    # Calculate box size with padding
    box_w = text_w + 2 * padding
    box_h = text_h + 2 * padding
    
    # Create tag image
    tag_img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    draw = ImageDraw.Draw(tag_img)
    
    # Draw rounded rectangle background
    draw.rounded_rectangle([(0,0), (box_w, box_h)], radius, fill=bg_color)
    
    # Center and draw text
    text_x = (box_w - text_w) // 2
    text_y = (box_h - text_h) // 2
    draw.text((text_x, text_y), text, font=font, fill=color)
    
    return tag_img

def process_pdf():
    # Setup
    script_root = Path(__file__).parent
    output_dir = script_root / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / f"log_{TIMESTAMP}.txt"
    logger = setup_logger(log_file)
    logger.info("Starting processing...")

    # Validate inputs
    input_pdf_path = script_root / INPUT_PDF_FILENAME
    reference_image_path = script_root / REFERENCE_TAG_IMAGE
    
    if not input_pdf_path.exists():
        logger.error(f"Input PDF not found at {input_pdf_path}. Exiting.")
        sys.exit(1)
    if not reference_image_path.exists():
        logger.warning(f"Reference tag image not found at {reference_image_path}. Tag style will be generic.")

    final_modified_pdf_path = output_dir / MODIFIED_PDF_FILENAME

    try:
        # 1. Load PDF pages as high-res images
        logger.info(f"Converting PDF {INPUT_PDF_FILENAME} at {DPI} DPI...")
        with tqdm(desc="PDF conversion", unit="page") as pbar:
            images = pdf2image.convert_from_path(input_pdf_path, dpi=DPI, thread_count=os.cpu_count(), fmt="png")
            pbar.update(len(images))
        
        if not images:
            logger.error("No pages converted.")
            sys.exit(1)

        main_image = images[0] # Assuming single page card
        main_img_w, main_img_h = main_image.size
        logger.info(f"Loaded page image size: {main_img_w}x{main_img_h}")

        # 2. Create the "고리" tag
        logger.info(f"Generating tag for '{TAG_TEXT}'...")
        font_path = script_root / KOREAN_FONT_PATH
        if not font_path.exists():
            font_path = Path(DEFAULT_FONT_PATH)
            logger.warning(f"Custom Korean font not found at {script_root / KOREAN_FONT_PATH}. Using fallback {DEFAULT_FONT_PATH}. Korean text will likely be broken or standard Arial.")
            
        gori_tag_image = create_gori_tag(str(font_path), TAG_FONT_SIZE, TAG_TEXT, TAG_COLOR, TAG_BG_COLOR, TAG_PADDING, TAG_CORNER_RADIUS)
        tag_w, tag_h = gori_tag_image.size
        logger.info(f"Tag image generated: {tag_w}x{tag_h}")

        # 3. Placement calculation and final image composite
        logger.info("Compositing tag onto card...")
        
        # Estimate dog position and tag placement. 
        # Position slightly to the right and above the dog's head.
        dog_head_x = int(DOG_HEAD_POS_ESTIMATE[0] * main_img_w)
        dog_head_y = int(DOG_HEAD_POS_ESTIMATE[1] * main_img_h)
        
        tag_x_final = dog_head_x + 100
        tag_y_final = dog_head_y - tag_h - 150
        
        # Ensure tag is on screen
        tag_x_final = max(0, min(main_img_w - tag_w, tag_x_final))
        tag_y_final = max(0, min(main_img_h - tag_h, tag_y_final))

        # Composite the tag
        main_image_rgba = main_image.convert("RGBA")
        combined_image = Image.alpha_composite(main_image_rgba, Image.new("RGBA", main_image_rgba.size, (0,0,0,0)))
        combined_image.paste(gori_tag_image, (tag_x_final, tag_y_final), gori_tag_image)
        
        # 4. Draw connecting curve (inspired by 'cellup' reference)
        logger.info("Drawing hand-drawn style connecting curve...")
        
        # Define the path of the curve, adding jitter for wobble
        control_points = [
            (dog_head_x - 10, dog_head_y + 10), # Start near head
            (dog_head_x + 50, dog_head_y - 30),
            (tag_x_final - 30, tag_y_final + tag_h + 30),
            (tag_x_final, tag_y_final + tag_h + 10) # End near tag
        ]
        
        # Generate wobbly line segments
        path = []
        for i in range(len(control_points) - 1):
            p1 = control_points[i]
            p2 = control_points[i+1]
            
            # Subdivide and add noise
            t = np.linspace(0, 1, CONNECTOR_POINTS_COUNT)
            xs = (1-t) * p1[0] + t * p2[0]
            ys = (1-t) * p1[1] + t * p2[1]
            
            # Add jitter to internal points
            xs[1:-1] += np.random.randint(-CONNECTOR_WOBBLE, CONNECTOR_WOBBLE + 1, size=len(xs)-2)
            ys[1:-1] += np.random.randint(-CONNECTOR_WOBBLE, CONNECTOR_WOBBLE + 1, size=len(ys)-2)
            
            segment_path = [(x, y) for x, y in zip(xs, ys)]
            path.extend(segment_path[1:] if path else segment_path)

        draw_combined = ImageDraw.Draw(combined_image)
        # Draw varied-width small circles and connect for a continuous hand-drawn line
        for j in range(len(path)-1):
            radius = np.random.randint(CONNECTOR_THICKNESS-1, CONNECTOR_THICKNESS+1)
            pt = path[j]
            draw_combined.ellipse([pt[0]-radius, pt[1]-radius, pt[0]+radius, pt[1]+radius], fill=CONNECTOR_COLOR)
            
        # Draw final endpoint circle
        radius = np.random.randint(CONNECTOR_THICKNESS-1, CONNECTOR_THICKNESS+1)
        pt = control_points[-1]
        draw_combined.ellipse([pt[0]-radius, pt[1]-radius, pt[0]+radius, pt[1]+radius], fill=CONNECTOR_COLOR)

        # 5. Save final modified page to high-res PDF
        logger.info(f"Saving modified high-resolution PDF at {final_modified_pdf_path}...")
        c = canvas.Canvas(str(final_modified_pdf_path), pagesize=A4) 
        width, height = A4
        
        # Calculate scaling to fit A4 while maintaining aspect ratio
        img_w, img_h = combined_image.size
        aspect_ratio = img_w / img_h
        if aspect_ratio > (width / height):
            draw_w = width
            draw_h = width / aspect_ratio
        else:
            draw_h = height
            draw_w = height * aspect_ratio
        
        x_centered = (width - draw_w) / 2
        y_centered = (height - draw_h) / 2

        # Convert PIL image to a ReportLab-usable temporary image
        img_data = combined_image.convert("RGB")
        img_buffer = os.path.join(output_dir, "temp_composite.png")
        img_data.save(img_buffer, format="PNG", quality=SAVE_QUALITY, **PDF_SAVE_OPTIONS)
        c.drawImage(img_buffer, x_centered, y_centered, width=draw_w, height=draw_h)
        c.showPage()
        c.save()
        os.remove(img_buffer) # Clean temp file

        # 6. Final success message and cleanup
        logger.info("Process complete.")
        for img in images:
             if hasattr(img, 'filename') and img.filename:
                 img.close()
        print(f"\nSuccessfully created modified PDF: {final_modified_pdf_path}\nMake sure to provide 'korean_font.ttf' in the script directory for proper Korean text rendering.\nAdjust DOG_HEAD_POS_ESTIMATE and control_points if perfect positioning is needed.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_pdf()