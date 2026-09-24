import os
import sys
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# tqdm 미설치 시 기본 print 함수로 대체
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

DPI = 300  # 고해상도 출력 설정
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
        # 로컬 시스템 한글 폰트 목록
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


def draw_curved_arrow(draw: ImageDraw.ImageDraw, start: Tuple[int, int], end: Tuple[int, int], 
                      control: Tuple[int, int], color: Tuple[int, int, int, int], width: int = 6):
    """베지에 곡선(Bezier Curve) 기반의 휘어진 손그림 스타일 화살표 생성"""
    points = []
    # 곡선 점 생성
    for t in [i / 50.0 for i in range(51)]:
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        points.append((x, y))
        
    # 곡선 그리기
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=width)
        
    # 화살표 머리(Arrowhead) 생성
    p1 = points[-2]
    p2 = points[-1]
    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    
    arrow_length = width * 3.5
    arrow_angle = math.pi / 6  # 30도
    
    left_x = p2[0] - arrow_length * math.cos(angle - arrow_angle)
    left_y = p2[1] - arrow_length * math.sin(angle - arrow_angle)
    right_x = p2[0] - arrow_length * math.cos(angle + arrow_angle)
    right_y = p2[1] - arrow_length * math.sin(angle + arrow_angle)
    
    draw.polygon([p2, (left_x, left_y), (right_x, right_y)], fill=color)


def add_gori_nametag(image: Image.Image) -> Image.Image:
    """예시 이미지('셀럽') 스타일을 반영하여 흰색 텍스트+검은 테두리, 휘어진 화살표 추가"""
    img_w, img_h = image.size
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 폰트 사이즈 (이미지 해상도 비례)
    font_size = int(img_h * 0.045)
    font = get_korean_font(font_size)
    
    # 위치 지정 (오른쪽 하단 강아지 머리 근처)
    # x: 72~85%, y: 70~85% 영역 기준
    text = "고리"
    text_x = int(img_w * 0.78)
    text_y = int(img_h * 0.72)
    
    # 1. '고리' 글자 추가 (흰색 글자 + 두꺼운 검은색 테두리)
    stroke_w = max(2, int(font_size * 0.08))
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke_w,
        stroke_fill=(0, 0, 0, 255)
    )
    
    # 2. 휘어진 화살표 추가 ('고리' 오른쪽 하단에서 강아지 머리를 향하도록)
    arrow_start = (text_x + int(font_size * 1.2), text_y + int(font_size * 0.9))
    arrow_end = (text_x + int(font_size * 0.5), text_y + int(font_size * 2.2))
    arrow_control = (text_x + int(font_size * 1.5), text_y + int(font_size * 1.8))
    
    # 테두리 검은색 화살표 (두껍게)
    draw_curved_arrow(draw, arrow_start, arrow_end, arrow_control, color=(0, 0, 0, 255), width=stroke_w * 3)
    # 내부 흰색 화살표
    draw_curved_arrow(draw, arrow_start, arrow_end, arrow_control, color=(255, 255, 255, 255), width=stroke_w * 2)

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def process():
    if not INPUT_PDF.exists():
        logger.error(f"입력 파일이 존재하지 않습니다: {INPUT_PDF}")
        sys.exit(1)

    logger.info("PDF 로딩 및 고해상도 변환 중...")
    
    try:
        import pdf2image
        images = pdf2image.convert_from_path(INPUT_PDF, dpi=DPI)
    except Exception as e:
        logger.error(f"PDF를 이미지로 변환하는 중 오류 발생 (poppler 설치 여부 확인 필요): {e}")
        sys.exit(1)

    processed_images = []
    for i, img in enumerate(tqdm(images, desc="이름표 합성 작업")):
        if i == 0:  # 첫 페이지 카드 작업
            img_with_tag = add_gori_nametag(img)
            processed_images.append(img_with_tag.convert("RGB"))
        else:
            processed_images.append(img)

    # 고해상도 PDF 출력 저장
    logger.info(f"결과 저장 중: {OUTPUT_PDF}")
    temp_img_paths = []
    
    try:
        c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
        a4_w, a4_h = A4
        
        for idx, p_img in enumerate(processed_images):
            temp_path = OUTPUT_DIR / f"temp_page_{idx}.png"
            p_img.save(temp_path, "PNG", dpi=(DPI, DPI))
            temp_img_paths.append(temp_path)
            
            # 비율 맞춤 A4 렌더링
            c.drawImage(str(temp_path), 0, 0, width=a4_w, height=a4_h)
            c.showPage()
            
        c.save()
        logger.info("작업 완료!")
    finally:
        # 임시 이미지 정리
        for tp in temp_img_paths:
            if tp.exists():
                os.remove(tp)


if __name__ == "__main__":
    process()