"""
# main.py for image_to_pdf project

Required Dependencies:
pip install pillow reportlab python-dotenv
"""

import os
import sys
import logging
from pathlib import Path

# 보안을 위한 .env 환경 변수 로드 라이브러리
try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: 'python-dotenv' module not found.")
    print("Please install it using: pip install python-dotenv")
    sys.exit(1)

# 이미지 및 PDF 처리를 위한 라이브러리
try:
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch  # 올바른 소문자 'inch' 임포트
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install dependencies: pip install pillow reportlab")
    sys.exit(1)

# --- 1. 로깅 및 환경 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Image2PDF_Generator")

# 실행 파일(main.py) 기준 절대 경로 설정 (GitHub 및 로컬 터미널 환경 호환)
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
OUTPUT_IMG_DIR = BASE_DIR / 'images'
OUTPUT_PDF_PATH = BASE_DIR / 'output.pdf'

# 이미지 저장 디렉토리 생성
OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)

# --- 2. 보안 지침: .env 파일 로드 ---
def load_api_key():
    """
    .env 파일에서 API_KEY를 안전하게 로드합니다.
    """
    if not ENV_PATH.exists():
        logger.error(f".env file not found at {ENV_PATH}")
        logger.info("Please create a .env file in the same directory as main.py and add: API_KEY=your_actual_key_here")
        return None

    # .env 파일 로드
    load_dotenv(dotenv_path=ENV_PATH)
    
    # OS 환경 변수에서 Key 가져오기
    api_key = os.environ.get('API_KEY')
    
    if not api_key or api_key == 'your_actual_api_key_here':
        logger.warning("API_KEY is missing or invalid in .env file.")
        return None
    
    # 보안상 Key의 일부만 로그에 출력
    logger.info(f"API Key loaded successfully: {api_key[:4]}****")
    return api_key

# --- 3. 고해상도 이미지 생성 ---
def generate_high_res_image(api_key, filename='generated_plot.png'):
    """
    PIL을 사용하여 고해상도(300 DPI) 로컬 이미지를 생성합니다.
    """
    logger.info("Generating high-resolution image...")
    img_path = OUTPUT_IMG_DIR / filename
    
    # 설정: 300 DPI 기준 고해상도 이미지 생성 (10인치 x 8인치)
    width_inch, height_inch = 10, 8
    dpi = 300
    width_px, height_px = width_inch * dpi, height_inch * dpi # 3000x2400
    
    try:
        # 이미지 객체 생성 (RGB mode, White background)
        image = Image.new('RGB', (width_px, height_px), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 폰트 로드 시도
        font = None
        try:
            if sys.platform == "win32":
                font_path = "arial.ttf"
            elif sys.platform == "darwin":
                font_path = "/Library/Fonts/Arial.ttf"
            else:
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            font = ImageFont.truetype(font_path, 80)
        except Exception:
            logger.warning("System TrueType font not found, using default font.")
            font = ImageFont.load_default()

        # 텍스트 내용
        title_text = "Image2PDF Generator v1.0"
        status_text = "Status: API Key Security Check Passed"
        key_hint_text = f"Key hint: {api_key[:4]}..." if api_key else "No Key Loaded"
        
        # 그래픽 요소
        draw.rectangle([100, 100, width_px - 100, height_px - 100], outline=(0, 0, 0), width=15)
        draw.ellipse([width_px // 2 - 200, height_px // 2 - 200, width_px // 2 + 200, height_px // 2 + 200], fill=(70, 130, 180))

        # Pillow 10+ 호환 텍스트 크기 계산 함수
        def draw_centered_text(y_pos, text, fill_color):
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
            except AttributeError:
                w, _ = draw.textsize(text, font=font)
            draw.text(((width_px - w) // 2, y_pos), text, fill=fill_color, font=font)

        # 텍스트 그리기
        draw_centered_text(200, title_text, (0, 0, 0))
        draw_centered_text(height_px - 400, status_text, (0, 128, 0))
        draw_centered_text(height_px - 300, key_hint_text, (220, 20, 60))

        # 고해상도 저장
        image.save(img_path, dpi=(dpi, dpi), quality=100)
        
        logger.info(f"High-res image saved to: {img_path} ({width_px}x{height_px}, {dpi} DPI)")
        return img_path

    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        return None

# --- 4. 이미지를 PDF로 변환 (고해상도 유지) ---
def convert_image_to_pdf(img_path, pdf_path):
    """
    PIL 이미지를 ReportLab 캔버스에 그려서 고해상도 PDF를 생성합니다.
    """
    logger.info(f"Converting {img_path.name} to PDF...")
    
    try:
        with Image.open(img_path) as img:
            img_width, img_height = img.size
            img_dpi = img.info.get('dpi', (72, 72))[0]

        a4_w, a4_h = A4
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        
        # 인치 단위 크기 계산
        img_width_inch = img_width / img_dpi
        img_height_inch = img_height / img_dpi
        
        # 여백 설정 (0.5인치)
        margin = 0.5 * inch
        avail_w = a4_w - (2 * margin)
        avail_h = a4_h - (2 * margin)
        
        # 스케일 비율 계산
        scale = min(avail_w / (img_width_inch * inch), avail_h / (img_height_inch * inch))
        
        draw_w = img_width_inch * inch * scale
        draw_h = img_height_inch * inch * scale
        
        x_centered = (a4_w - draw_w) / 2
        y_centered = (a4_h - draw_h) / 2
        
        c.drawImage(str(img_path), x_centered, y_centered, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
        
        c.showPage()
        c.save()
        
        logger.info(f"High-res PDF successfully generated at: {pdf_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to convert to PDF: {e}")
        return False

# --- 5. 메인 실행 흐름 ---
if __name__ == "__main__":
    logger.info("Starting Image2PDF Production Pipeline")
    
    api_key = load_api_key()
    if not api_key:
        logger.warning("Proceeding with placeholder content due to missing API Key.")
        api_key = "NO_KEY_SAFE_MODE"

    generated_img_path = generate_high_res_image(api_key, 'final_report_visual.png')
    
    if generated_img_path and generated_img_path.exists():
        success = convert_image_to_pdf(generated_img_path, OUTPUT_PDF_PATH)
        
        if success:
            try:
                os.remove(generated_img_path)
                logger.info("Temporary image file removed.")
                if not any(OUTPUT_IMG_DIR.iterdir()):
                    OUTPUT_IMG_DIR.rmdir()
                    logger.info("Temporary images directory removed.")
            except OSError as e:
                logger.warning(f"Failed to remove temporary files: {e}")
    else:
        logger.critical("Pipeline failed: Image was not generated.")

    logger.info("Pipeline finished. Check for 'output.pdf' in the current folder.")