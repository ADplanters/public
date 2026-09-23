"""
AP 메인 회사 홈페이지용 고퀄리티 파비콘 및 PDF 스펙 문서 생성 스크립트

- 배경: 다크 사이버 테마 (딥 미드나이트 블루 ~ 메탈릭 바이올렛 그라데이션)
- 텍스처: 심플한 사이버 그리드 및 서킷 라인 패턴
- 로고: 선명한 흰색 'AP' 텍스트 + 미세한 사이버 네온 글로우 효과
- 출력: 
  1. favicon.ico (16x16 ~ 256x256 다중 해상도 지원)
  2. favicon_preview.png (1024x1024 고해상도 프리뷰)
  3. favicon_spec.pdf (300 DPI 고해상도 규격 문서)
"""

import os
import math
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 경로 설정 (현재 파일 기준 절대 경로)
BASE_DIR = Path(__file__).resolve().parent
PREVIEW_PATH = BASE_DIR / "favicon_preview.png"
ICO_PATH = BASE_DIR / "favicon.ico"
PDF_PATH = BASE_DIR / "favicon_spec.pdf"

# 고해상도 이미지 크기 및 설정
IMAGE_SIZE = 1024
DPI = 300
ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def create_cyber_background(width: int, height: int) -> Image.Image:
    """딥 사이버 그라데이션 배경을 생성합니다."""
    bg = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(bg)

    # 딥 딥블루/퍼플 테크 그라데이션
    for y in range(height):
        ratio = y / height
        r = int(10 + (35 - 10) * ratio)
        g = int(16 + (12 - 16) * ratio)
        b = int(38 + (75 - 38) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    return bg


def apply_cyber_texture(base_img: Image.Image) -> Image.Image:
    """심플하고 고급스러운 사이버 텍스처(그리드 & 은은한 라인)를 합성합니다."""
    width, height = base_img.size
    texture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(texture)

    # 1. 미세한 사이버 그리드 패턴
    grid_spacing = 48
    grid_color = (0, 210, 255, 15)  # 저농도 은은한 시안 컬러
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 2. 대각선 은은한 대각 테크 라인 포인트
    accent_color = (0, 255, 200, 25)
    draw.line([(0, height * 0.75), (width * 0.75, 0)], fill=accent_color, width=3)
    draw.line([(width * 0.25, height), (width, height * 0.25)], fill=accent_color, width=3)

    return Image.alpha_composite(base_img, texture)


def draw_ap_logo(base_img: Image.Image) -> Image.Image:
    """흰색 AP 글자 및 은은한 글로우 효과를 렌더링합니다."""
    width, height = base_img.size
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    glow_draw = ImageDraw.Draw(glow_layer)
    text_draw = ImageDraw.Draw(text_layer)

    # 폰트로드 시도 (시스템 폰트 선별 사용, 없을 경우 기본 폰트)
    font_size = int(width * 0.48)
    font = None
    font_candidates = ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "Helvetica-Bold.ttf"]
    
    for font_name in font_candidates:
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except OSError:
            continue

    if font is None:
        logger.warning("시스템 정식 폰트를 찾지 못해 기본 폰트를 사용합니다.")
        font = ImageFont.load_default()

    text = "AP"
    
    # 텍스트 중앙 정렬 위치 계산
    bbox = text_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) / 2 - bbox[0]
    y = (height - text_height) / 2 - bbox[1]

    # 1. 사이버 네온 외곽 글로우 효과
    glow_color = (0, 220, 255, 120)
    glow_draw.text((x, y), text, font=font, fill=glow_color)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=20))

    # 2. 메인 순백색 'AP' 텍스트
    text_draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    # 레이어 합성
    combined = Image.alpha_composite(base_img, glow_layer)
    combined = Image.alpha_composite(combined, text_layer)
    
    return combined


def make_rounded_icon(img: Image.Image, radius_ratio: float = 0.22) -> Image.Image:
    """모던한 아이콘을 위해 모서리를 라운딩(Squircle 형태) 처리합니다."""
    width, height = img.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    radius = int(width * radius_ratio)
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)

    output = img.copy()
    output.putalpha(mask)
    return output


def generate_favicon_assets():
    """파비콘 이미지 파일들을 생성합니다."""
    logger.info("고급 사이버 AP 파비콘 이미지 생성 시작...")
    
    # 1. 배경 + 텍스처 + 로고 생성
    bg = create_cyber_background(IMAGE_SIZE, IMAGE_SIZE)
    textured = apply_cyber_texture(bg)
    logo_img = draw_ap_logo(textured)
    final_icon = make_rounded_icon(logo_img)

    # 2. 고해상도 PNG 프리뷰 저장
    final_icon.save(PREVIEW_PATH, format="PNG", dpi=(DPI, DPI))
    logger.info(f"고해상도 프리뷰 저장 완료: {PREVIEW_PATH}")

    # 3. 다중 해상도 .ico 파일 생성
    final_icon.save(
        ICO_PATH,
        format="ICO",
        sizes=ICO_SIZES,
        bitmap_format="png"
    )
    logger.info(f"멀티 사이즈 파비콘(.ico) 저장 완료: {ICO_PATH}")
    
    return final_icon


def generate_pdf_spec(icon_img: Image.Image):
    """300 DPI 고해상도 규격 명세서 PDF를 생성합니다."""
    logger.info("파비콘 명세서 PDF 생성 시작...")
    
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4)
    page_w, page_h = A4

    # 타이틀 섹션
    c.setFont("Helvetica-Bold", 22)
    c.drawString(1 * inch, page_h - 1 * inch, "AP Main Favicon Design Specification")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(1 * inch, page_h - 1.3 * inch, "Concept: Premium Cyber Gradient & Minimalist Texture")
    c.drawString(1 * inch, page_h - 1.5 * inch, f"Resolution Standard: {DPI} DPI / Color Space: RGBA")

    # 고해상도 메인 이미지 삽입
    main_preview_pt = 2.5 * inch
    c.drawImage(
        str(PREVIEW_PATH),
        1 * inch,
        page_h - 4.3 * inch,
        width=main_preview_pt,
        height=main_preview_pt,
        mask="auto"
    )

    # 파비콘 리사이즈 규격표 시각화
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(4 * inch, page_h - 2 * inch, "Browser Icon Sizes (ICO Embedded)")

    y_pos = page_h - 2.4 * inch
    for size_w, size_h in ICO_SIZES:
        # 임시 작은 사이즈 PNG 생성 및 배치
        temp_thumb_path = BASE_DIR / f"temp_{size_w}.png"
        resized_thumb = icon_img.resize((size_w, size_h), Image.LANCZOS)
        resized_thumb.save(temp_thumb_path, format="PNG")

        display_size = max(size_w * 0.8, 16)  # PDF 가독성을 위한 최소 표시 크기
        c.drawImage(str(temp_thumb_path), 4 * inch, y_pos - (display_size / 2), width=display_size, height=display_size, mask="auto")
        
        c.setFont("Helvetica", 10)
        c.drawString(4.8 * inch, y_pos - 4, f"{size_w} x {size_h} px")
        
        y_pos -= 0.45 * inch

        # 임시 파일 삭제
        if temp_thumb_path.exists():
            os.remove(temp_thumb_path)

    # 하단 메타 정보
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(1 * inch, 1.2 * inch, page_w - 1 * inch, 1.2 * inch)
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(1 * inch, 0.9 * inch, "Confidential - Internal Main Company Website Asset")

    c.showPage()
    c.save()
    logger.info(f"PDF 명세서 생성 완료: {PDF_PATH}")


def main():
    try:
        logger.info(f"작업 디렉토리: {BASE_DIR}")
        
        # 파비콘 자산 생성
        icon_img = generate_favicon_assets()
        
        # PDF 규격서 생성
        generate_pdf_spec(icon_img)

        # 리소스 정리
        icon_img.close()
        
        print("\n==================================================")
        print(" 성공적으로 작업이 완료되었습니다!")
        print(f" 1. 파비콘 아이콘: {ICO_PATH.name}")
        print(f" 2. 고해상도 프리뷰: {PREVIEW_PATH.name}")
        print(f" 3. PDF 규격서: {PDF_PATH.name}")
        print("==================================================\n")

    except Exception as e:
        logger.error(f"작업 중 오류가 발생했습니다: {e}", exc_info=True)


if __name__ == "__main__":
    main()