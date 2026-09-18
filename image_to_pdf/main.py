"""
# main.py for image_to_pdf project
# Production-Ready High-Precision YouTube Shorts Thumbnail & PDF Generator

Required Dependencies:
pip install pillow reportlab python-dotenv

requirements.txt:
pillow>=10.0.0
reportlab>=4.0.0
python-dotenv>=1.0.0
"""

import os
import sys
import logging
import urllib.request
import ssl
from pathlib import Path

# 환경변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 이미지 및 PDF 처리 라이브러리
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install dependencies: pip install pillow reportlab python-dotenv")
    sys.exit(1)

# --- 1. 로깅 및 경로 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ShortsThumbnailPrecision")

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
OUTPUT_IMG_PATH = BASE_DIR / 'shorts_thumbnail.png'
OUTPUT_PDF_PATH = BASE_DIR / 'shorts_thumbnail.pdf'
FONT_PATH = BASE_DIR / 'NanumGothicBold.ttf'

# --- 2. 한글 폰트 자동 확보 ---
def ensure_korean_font():
    """고해상도 텍스트 렌더링을 위한 나눔고딕 Bold 폰트 다운로드"""
    if not FONT_PATH.exists():
        logger.info("Downloading NanumGothic Bold font...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
            logger.info("Font downloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download font: {e}")
            return None
    return str(FONT_PATH)

# --- 3. 입력 이미지 자동 탐색 ---
def find_input_image():
    """image_21.jpg, image_21.png 등 로컬 이미지 자동 검색"""
    possible_names = ['image_21.jpg', 'image_21.png', 'image_21.jpeg', 'image_dfd981.jpg']
    for name in possible_names:
        candidate = BASE_DIR / name
        if candidate.exists():
            logger.info(f"Found target input image: {candidate.name}")
            return candidate
            
    # 폴더 내 가용 이미지 탐색
    for file in BASE_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            if 'thumbnail' not in file.name and 'banner' not in file.name:
                logger.info(f"Auto-selected image: {file.name}")
                return file
    return None

# --- 4. 텍스트 너비 자동 맞춤 (글자 잘림 차단) ---
def get_fitted_font(font_path, text, max_width, initial_size, min_size=18):
    """지정한 가로 너비(max_width)를 넘지 않도록 폰트 크기를 자동 조절"""
    size = initial_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            return font, w, bbox[3] - bbox[1]
        size -= 2
    font = ImageFont.truetype(font_path, min_size)
    bbox = font.getbbox(text)
    return font, bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_text_with_stroke_and_shadow(draw, pos, text, font, fill_color, stroke_color, stroke_width=5):
    """그림자 + 외곽선이 적용된 고가독성 텍스트 그리기"""
    x, y = pos
    # 그림자 (Shadow)
    draw.text((x + 4, y + 4), text, font=font, fill=(0, 0, 0, 180))
    # 외곽선 (Stroke)
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # 메인 텍스트
    draw.text((x, y), text, font=font, fill=fill_color)

# --- 5. 쇼츠 썸네일 생성 메인 함수 ---
def generate_precision_thumbnail(font_path, input_img_path):
    logger.info("Generating precision-fitted Shorts Thumbnail...")
    
    try:
        with Image.open(input_img_path) as base_img:
            base_img = base_img.convert('RGB')
            width, height = base_img.size
            logger.info(f"Image Resolution: {width}x{height}")

            # 가로 여백 안전선 (좌우 7% 여백 확보하여 잘림 원천 차단)
            max_text_w = int(width * 0.86)

            # 1. 배경 어두운 그라데이션 적용 (기존 배경 글자 가림 및 가독성 확보)
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # 상단 50% 영역에 어두운 그래디언트 딥 차단막 적용
            gradient_height = int(height * 0.52)
            for i in range(gradient_height):
                alpha = int(220 * (1 - (i / gradient_height) ** 1.5))
                overlay_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))

            base_img = Image.alpha_composite(base_img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(base_img)

            # 2. 상단 긴급 진단 뱃지 (배경 글자 완전 마스킹)
            badge_text = "🔥 매장 매출 정체 긴급 진단"
            badge_font, bw, bh = get_fitted_font(font_path, badge_text, max_text_w - 40, int(height * 0.034))
            
            pad_x, pad_y = 28, 16
            bx = (width - bw) // 2
            by = int(height * 0.05)

            # 주황색 라운드 뱃지 박스
            badge_box = [bx - pad_x, by - pad_y, bx + bw + pad_x, by + bh + pad_y]
            draw.rectangle(badge_box, fill=(235, 95, 25))
            draw.text((bx, by - 2), badge_text, fill=(255, 255, 255), font=badge_font)

            # 3. 메인 타이틀 (3줄 분할로 가로 압박 해제 및 임팩트 극대화)
            title_lines = [
                ("우리 매장만", (255, 220, 0)),        # 노란색 강조
                ("손님이 없는", (255, 255, 255)),     # 흰색
                ("진짜 이유?!", (255, 220, 0))       # 노란색 강조
            ]

            start_y = by + bh + int(height * 0.045)
            line_gap = int(height * 0.015)
            stroke_w = max(3, int(width * 0.008))

            curr_y = start_y
            for line_text, color in title_lines:
                # 각 줄마다 좌우 박스 범위를 절대 넘지 않도록 자동 스케일링
                line_font, lw, lh = get_fitted_font(font_path, line_text, max_text_w, int(height * 0.065))
                lx = (width - lw) // 2
                draw_text_with_stroke_and_shadow(
                    draw, (lx, curr_y), line_text, line_font, color, (0, 0, 0), stroke_width=stroke_w
                )
                curr_y += lh + line_gap

            # 4. 하단 서브 키워드 뱃지
            sub_text = "📍 플레이스 마케팅 전문"
            sub_font, sw, sh = get_fitted_font(font_path, sub_text, max_text_w, int(height * 0.036))
            sx = (width - sw) // 2
            sy = curr_y + int(height * 0.015)
            
            draw_text_with_stroke_and_shadow(
                draw, (sx, sy), sub_text, sub_font, (220, 240, 255), (0, 0, 0), stroke_width=max(2, stroke_w - 2)
            )

            # 고해상도 저장
            base_img.save(OUTPUT_IMG_PATH, format="PNG", quality=100)
            logger.info(f"High-Precision Thumbnail Image saved: {OUTPUT_IMG_PATH}")
            return OUTPUT_IMG_PATH

    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}", exc_info=True)
        return None

# --- 6. PDF 변환 ---
def compile_pdf(image_path, output_path):
    """고해상도 PDF 변환"""
    if not image_path or not image_path.exists():
        return False
        
    logger.info("Converting Thumbnail image to PDF...")
    try:
        c = canvas.Canvas(str(output_path), pagesize=A4)
        a4_w, a4_h = A4
        
        with Image.open(image_path) as img:
            img_w, img_h = img.size
            
            margin = 0.4 * inch
            avail_w = a4_w - (2 * margin)
            avail_h = a4_h - (2 * margin)
            
            scale = min(avail_w / img_w, avail_h / img_h)
            draw_w = img_w * scale
            draw_h = img_h * scale
            
            x_centered = (a4_w - draw_w) / 2
            y_centered = (a4_h - draw_h) / 2
            
            c.drawImage(str(image_path), x_centered, y_centered, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
            c.showPage()
            
        c.save()
        logger.info(f"PDF successfully created: {output_path}")
        return True
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return False

# --- 7. 메인 실행 흐름 ---
if __name__ == "__main__":
    logger.info("=== Starting Precision Shorts Thumbnail Pipeline ===")
    
    font_path = ensure_korean_font()
    input_img_path = find_input_image()
    
    if not input_img_path:
        logger.critical("Input image file not found. Please ensure image_21.jpg exists in folder.")
        sys.exit(1)
        
    if font_path and input_img_path:
        out_img = generate_precision_thumbnail(font_path, input_img_path)
        if out_img:
            success = compile_pdf(out_img, OUTPUT_PDF_PATH)
            if success:
                logger.info("=== Pipeline Completed Successfully! ===")
                logger.info(f"Generated Image: {out_img.name}")
                logger.info(f"Generated PDF: {OUTPUT_PDF_PATH.name}")
            else:
                logger.error("PDF Compilation Failed.")
        else:
            logger.critical("Thumbnail Generation Failed.")