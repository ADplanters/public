import os
import sys
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

# 필수 라이브러리 체크
try:
    import fitz  # PyMuPDF
except ImportError:
    print("[오류] PyMuPDF가 설치되어 있지 않습니다. 'pip install pymupdf'를 실행해주세요.")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="", **kwargs):
        print(f"--> {desc} 작업 진행 중...")
        return iterable

# --- 경로 및 기본 설정 ---
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DPI = 300  # 고해상도 품질 (300 DPI)
INPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_highres.pdf"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PDF = OUTPUT_DIR / f"modified_카드_고리추가_{TIMESTAMP}.pdf"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Image2PDF")


def find_best_font(size: int) -> ImageFont.FreeTypeFont:
    """
    1. 실행 폴더 내에 별도로 추가된 .ttf / .otf 폰트 파일 우선 탐색
    2. OS 시스템 한글 폰트(맑은 고딕 Bold 등) 탐색
    """
    # 1. 스크립트 폴더 내 사용자 지정 폰트 우선 검색
    local_fonts = list(BASE_DIR.glob("*.ttf")) + list(BASE_DIR.glob("*.otf"))
    for font_file in local_fonts:
        try:
            logger.info(f"사용자 폰트 적용: {font_file.name}")
            return ImageFont.truetype(str(font_file), size)
        except Exception:
            continue

    # 2. 시스템 기본 한글 폰트 목록 (두꺼운체 우선)
    system_fonts = [
        "C:/Windows/Fonts/malgunbd.ttf",    # Windows 맑은 고딕 Bold
        "C:/Windows/Fonts/malgun.ttf",      # Windows 맑은 고딕
        "C:/Windows/Fonts/H2GTRM.TTF",      # Windows 한컴고딕
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # macOS
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"  # Linux
    ]

    for font_path in system_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    logger.warning("적절한 한글 폰트를 찾지 못해 기본 폰트로 대체합니다.")
    return ImageFont.load_default()


def draw_styled_arrow(draw: ImageDraw.ImageDraw, start: Tuple[int, int], end: Tuple[int, int],
                      control: Tuple[int, int], line_width: int, outline_width: int):
    """
    '셀럽' 예시 이미지와 동일하게 검은색 두꺼운 테두리가 둘러진 흰색 휘어진 화살표 생성
    """
    # 1. 베지에 곡선(Bezier Curve) 점 생성
    steps = 60
    points = []
    for i in range(steps + 1):
        t = i / float(steps)
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        points.append((x, y))

    total_width = line_width + (outline_width * 2)

    # 2. 곡선 외곽선(검은색) 그리기
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(0, 0, 0, 255), width=total_width)

    # 3. 곡선 내부(흰색) 그리기
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(255, 255, 255, 255), width=line_width)

    # 4. 화살표 머리(Arrowhead) 연산
    p_prev = points[-5]
    p_end = points[-1]
    angle = math.atan2(p_end[1] - p_prev[1], p_end[0] - p_prev[0])

    arrow_length = line_width * 3.8
    arrow_angle = math.pi / 5.5  # 약 32도

    # 외곽 검은색 화살표 삼각형
    p_left_out = (
        p_end[0] - (arrow_length + outline_width) * math.cos(angle - arrow_angle),
        p_end[1] - (arrow_length + outline_width) * math.sin(angle - arrow_angle)
    )
    p_right_out = (
        p_end[0] - (arrow_length + outline_width) * math.cos(angle + arrow_angle),
        p_end[1] - (arrow_length + outline_width) * math.sin(angle + arrow_angle)
    )
    draw.polygon([p_end, p_left_out, p_right_out], fill=(0, 0, 0, 255))

    # 내부 흰색 화살표 삼각형
    p_left_in = (
        p_end[0] - arrow_length * math.cos(angle - arrow_angle),
        p_end[1] - arrow_length * math.sin(angle - arrow_angle)
    )
    p_right_in = (
        p_end[0] - arrow_length * math.cos(angle + arrow_angle),
        p_end[1] - arrow_length * math.sin(angle + arrow_angle)
    )
    draw.polygon([p_end, p_left_in, p_right_in], fill=(255, 255, 255, 255))


def add_gori_nametag(image: Image.Image) -> Image.Image:
    """'셀럽' 예시 이미지 표지 형태를 정교하게 재현하여 '고리' 이름표 합성"""
    img_w, img_h = image.size
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 해상도 기반 크기 자동 조절
    font_size = int(img_h * 0.052)  # 글자 크기
    font = find_best_font(font_size)
    stroke_width = max(3, int(font_size * 0.11))  # 두꺼운 검은 테두리 비율

    text = "고리"
    
    # 오른쪽 하단 강아지 머리 상단 우측 위치 계산
    text_x = int(img_w * 0.76)
    text_y = int(img_h * 0.69)

    # 1. '고리' 텍스트 렌더링 (흰색 글씨 + 두꺼운 검은 테두리)
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0, 255)
    )

    # 2. '고리' 밑에서 강아지 머리를 향해 곡선으로 휘어지는 화살표 좌표 계산
    arrow_start = (text_x + int(font_size * 1.15), text_y + int(font_size * 0.95))
    arrow_end = (text_x + int(font_size * 0.35), text_y + int(font_size * 2.2))
    arrow_control = (text_x + int(font_size * 1.55), text_y + int(font_size * 1.75))

    # 화살표 그리기
    draw_styled_arrow(
        draw,
        start=arrow_start,
        end=arrow_end,
        control=arrow_control,
        line_width=int(stroke_width * 1.2),
        outline_width=stroke_width
    )

    return Image.alpha_composite(image.convert("RGBA"), overlay)


def process():
    if not INPUT_PDF.exists():
        logger.error(f"입력 PDF 파일이 없습니다: {INPUT_PDF}")
        sys.exit(1)

    logger.info("PDF 로딩 및 고해상도 변환 처리 중...")

    try:
        doc = fitz.open(INPUT_PDF)
        processed_images = []
        page_sizes = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            zoom = DPI / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_sizes.append((page.rect.width, page.rect.height))

            if page_num == 0:  # 첫 페이지(카드)에 '고리' 이름표 반영
                img = add_gori_nametag(img).convert("RGB")

            processed_images.append(img)

        doc.close()

    except Exception as e:
        logger.error(f"PDF 처리 중 오류 발생: {e}")
        sys.exit(1)

    # 고해상도 PDF 합성 및 저장
    logger.info(f"결과 PDF 생성 중: {OUTPUT_PDF}")
    temp_img_paths = []

    try:
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
        logger.info("작업 성공적으로 완료!")
        print(f"\n최종 결과물 저장 완료: {OUTPUT_PDF}")

    finally:
        for tp in temp_img_paths:
            if tp.exists():
                os.remove(tp)


if __name__ == "__main__":
    process()