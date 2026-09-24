import os
import sys
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

# 의존성 모듈 체크 및 예외 처리
try:
    import fitz  # PyMuPDF (Poppler 없이 PDF를 고해상도 이미지로 변환)
except ImportError:
    print("[Error] PyMuPDF가 설치되지 않았습니다. 터미널에 'pip install pymupdf'를 입력하세요.")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="", **kwargs):
        print(f"--> {desc} 진행 중...")
        return iterable

# --- 기본 경로 및 설정 ---
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300  # 고해상도 품질 유지 (300 DPI)
INPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_highres.pdf"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PDF = OUTPUT_DIR / f"modified_카드_{TIMESTAMP}.pdf"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Image2PDF")


def get_korean_font(size: int) -> ImageFont.FreeTypeFont:
    """Windows/macOS 시스템 내 한글 폰트를 자동 탐색합니다."""
    font_candidates = [
        "C:/Windows/Fonts/malgun.ttf",       # Windows 맑은 고딕
        "C:/Windows/Fonts/malgunbd.ttf",     # Windows 맑은 고딕 Bold
        "C:/Windows/Fonts/batang.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # macOS
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"     # Linux
    ]
    
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
                
    logger.warning("시스템 한글 폰트를 찾지 못해 기본 폰트로 대체합니다.")
    return ImageFont.load_default()


def draw_curved_arrow_with_outline(draw: ImageDraw.ImageDraw, start: Tuple[int, int], end: Tuple[int, int], 
                                   control: Tuple[int, int], fill_color: Tuple[int, int, int, int], 
                                   outline_color: Tuple[int, int, int, int], width: int = 8, outline_width: int = 3):
    """예시 이미지 스타일의 검은 테두리가 있는 흰색 휘어진 화살표 생성"""
    points = []
    num_steps = 50
    for i in range(num_steps + 1):
        t = i / float(num_steps)
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        points.append((x, y))

    total_w = width + outline_width * 2
    
    # 1. 검은색 테두리 선
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=outline_color, width=total_w)

    # 2. 내부 흰색 채움 선
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=fill_color, width=width)

    # 3. 화살표 머리(Arrowhead) 생성
    p_prev = points[-4]
    p_end = points[-1]
    angle = math.atan2(p_end[1] - p_prev[1], p_end[0] - p_prev[0])

    arrow_len = width * 3.5
    arrow_angle = math.pi / 5  # 36도

    p_left = (p_end[0] - arrow_len * math.cos(angle - arrow_angle), p_end[1] - arrow_len * math.sin(angle - arrow_angle))
    p_right = (p_end[0] - arrow_len * math.cos(angle + arrow_angle), p_end[1] - arrow_len * math.sin(angle + arrow_angle))

    # 외각 테두리 머리
    draw.polygon([p_end, p_left, p_right], fill=outline_color)
    
    # 내부 흰색 머리
    inner_len = max(1.0, arrow_len - outline_width)
    p_left_in = (p_end[0] - inner_len * math.cos(angle - arrow_angle), p_end[1] - inner_len * math.sin(angle - arrow_angle))
    p_right_in = (p_end[0] - inner_len * math.cos(angle + arrow_angle), p_end[1] - inner_len * math.sin(angle + arrow_angle))
    draw.polygon([p_end, p_left_in, p_right_in], fill=fill_color)


def add_gori_nametag(image: Image.Image) -> Image.Image:
    """예시 이미지('셀럽') 스타일: 흰색 글씨 + 검은 테두리 + 휘어진 화살표"""
    img_w, img_h = image.size
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 이미지 해상도 비례 폰트 및 테두리 크기 계산
    font_size = int(img_h * 0.05)
    font = get_korean_font(font_size)
    stroke_w = max(3, int(font_size * 0.09))
    
    # 위치 지정 (우측 하단 강아지 머리 상단 우측)
    text = "고리"
    text_x = int(img_w * 0.77)
    text_y = int(img_h * 0.70)
    
    # 1. '고리' 글자 그리기 (흰색 fill + 두꺼운 검은색 stroke)
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke_w,
        stroke_fill=(0, 0, 0, 255)
    )
    
    # 2. 강아지 머리를 가리키는 휘어진 화살표 생성
    arrow_start = (text_x + int(font_size * 1.1), text_y + int(font_size * 0.95))
    arrow_end = (text_x + int(font_size * 0.4), text_y + int(font_size * 2.1))
    arrow_control = (text_x + int(font_size * 1.5), text_y + int(font_size * 1.7))
    
    draw_curved_arrow_with_outline(
        draw,
        start=arrow_start,
        end=arrow_end,
        control=arrow_control,
        fill_color=(255, 255, 255, 255),
        outline_color=(0, 0, 0, 255),
        width=int(stroke_w * 1.8),
        outline_width=stroke_w
    )

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def process():
    if not INPUT_PDF.exists():
        logger.error(f"입력 PDF 파일이 존재하지 않습니다: {INPUT_PDF}")
        sys.exit(1)

    logger.info("PyMuPDF를 사용해 PDF 로딩 및 고해상도 변환 중...")
    
    try:
        doc = fitz.open(INPUT_PDF)
        processed_images = []
        page_sizes = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # 300 DPI 기준 스케일링
            zoom = DPI / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_sizes.append((page.rect.width, page.rect.height))

            if page_num == 0:  # 첫 페이지 카드 작업
                img = add_gori_nametag(img).convert("RGB")
            
            processed_images.append(img)
            
        doc.close()

    except Exception as e:
        logger.error(f"PDF 처리 중 오류 발생: {e}")
        sys.exit(1)

    # 결과 PDF 생성
    logger.info(f"결과 고해상도 PDF 저장 중: {OUTPUT_PDF}")
    temp_img_paths = []
    
    try:
        # 원본 PDF 페이지 크기 유지
        first_page_size = page_sizes[0]
        c = canvas.Canvas(str(OUTPUT_PDF), pagesize=first_page_size)
        
        for idx, (p_img, (p_w, p_h)) in enumerate(zip(processed_images, page_sizes)):
            temp_path = OUTPUT_DIR / f"temp_page_{idx}.png"
            p_img.save(temp_path, "PNG", dpi=(DPI, DPI))
            temp_img_paths.append(temp_path)
            
            c.setPageSize((p_w, p_h))
            c.drawImage(str(temp_path), 0, 0, width=p_w, height=p_h)
            c.showPage()
            
        c.save()
        logger.info("작업이 성공적으로 완료되었습니다!")
        print(f"\n생성 완료된 파일 위치: {OUTPUT_PDF}")
        
    finally:
        for tp in temp_img_paths:
            if tp.exists():
                os.remove(tp)


if __name__ == "__main__":
    process()