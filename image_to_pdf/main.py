import os
import sys
import math
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ---------------------------------------------------------------------------
# 1. 로깅 및 환경 설정
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 절대 경로 기준 상대 위치 계산 (image_to_pdf 폴더 내 실행 보장)
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres_tagged.pdf"

INPUT_PATH = BASE_DIR / INPUT_FILENAME
OUTPUT_PATH = BASE_DIR / OUTPUT_FILENAME

# ---------------------------------------------------------------------------
# 2. 디자인 및 위치 설정 (우측 하단 강아지 타겟)
# ---------------------------------------------------------------------------
TARGET_DPI = 300
TAG_TEXT = "고리"

# 타겟(강아지) 위치: 오른쪽 하단
TARGET_X_RATIO = 0.85
TARGET_Y_RATIO = 0.85

# 텍스트(시작점) 위치: 강아지보다 약간 왼쪽 위
TEXT_X_RATIO = 0.70
TEXT_Y_RATIO = 0.70


def get_cursive_korean_font(size: int) -> ImageFont.FreeTypeFont:
    """필기체 느낌을 살릴 수 있는 궁서체, 붓글씨 계열의 한글 폰트를 로드합니다."""
    font_paths = [
        # Windows (궁서체, 맑은고딕)
        "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/H2GTRM.TTF",
        "C:/Windows/Fonts/malgun.ttf",
        # macOS (궁서체, 애플명조)
        "/System/Library/Fonts/Supplemental/GungSeo.ttf",
        "/System/Library/Fonts/Supplemental/AppleMyungjo.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        # Linux (나눔펜, 나눔붓, 돋움)
        "/usr/share/fonts/truetype/nanum/NanumPen.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBrush.ttf",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                logging.info(f"적용 폰트: {font_path}")
                return ImageFont.truetype(font_path, size=size)
            except Exception as e:
                logging.warning(f"폰트 로드 실패 ({font_path}): {e}")

    logging.warning("시스템에 적합한 한글 필기체 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """고해상도 이미지의 몽환적이고 선명한 느낌을 위해 품질을 보정합니다."""
    logging.info("이미지 선명도 및 대비 자동 보정 진행 중...")
    
    # 선명도 30% 향상
    image = ImageEnhance.Sharpness(image).enhance(1.3)
    # 대비 15% 향상 (조금 더 선명하고 깊이감 있게)
    image = ImageEnhance.Contrast(image).enhance(1.15)
    # 색도 10% 향상 (풍부한 색감)
    image = ImageEnhance.Color(image).enhance(1.1)
    
    return image


def draw_squiggly_arrow_with_text(image: Image.Image, text: str, 
                                  start_ratio: tuple, target_ratio: tuple) -> Image.Image:
    """
    텍스트를 배치하고, 텍스트에서 타겟(강아지)을 향하는 '꼬부랑(곡선) 화살표'를 그립니다.
    """
    logging.info("텍스트 및 꼬부랑 화살표 합성 중...")

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    width, height = image.size
    
    # 해상도 비례 폰트 크기 및 두께 계산
    font_size = max(30, int(width * 0.035))
    font = get_cursive_korean_font(font_size)
    line_width = max(3, int(width * 0.003))

    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. 텍스트 위치 및 렌더링
    text_x = width * start_ratio[0]
    text_y = height * start_ratio[1]
    
    # 텍스트 그림자(가독성 향상) 및 본문 그리기
    shadow_offset = max(1, int(font_size * 0.05))
    text_color = (40, 40, 40, 255)
    shadow_color = (255, 255, 255, 200)

    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill=shadow_color, font=font)
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # 텍스트 바운딩 박스를 기준으로 화살표 시작점 계산 (텍스트 우측 하단 즈음)
    bbox = draw.textbbox((text_x, text_y), text, font=font)
    p0_x = bbox[2] + 10
    p0_y = bbox[3] - (bbox[3] - bbox[1]) // 2  # 텍스트 높이의 중간쯤

    # 2. 꼬부랑(Bezier Curve) 화살표 그리기
    p3_x = width * target_ratio[0]
    p3_y = height * target_ratio[1]

    # 3차 베지에 곡선 제어점 (S자 형태의 꼬부랑 느낌을 주기 위한 제어점 설정)
    # 첫 번째 제어점은 위로 살짝 뜨게, 두 번째 제어점은 타겟 전에 아래로 쳐지게 설정
    p1_x = p0_x + (p3_x - p0_x) * 0.3
    p1_y = p0_y - (height * 0.05)
    
    p2_x = p0_x + (p3_x - p0_x) * 0.7
    p2_y = p3_y + (height * 0.05)

    # 베지에 곡선 포인트 계산 알고리즘
    steps = 100
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        # Cubic Bezier 공식
        x = (1-t)**3 * p0_x + 3*(1-t)**2 * t * p1_x + 3*(1-t) * t**2 * p2_x + t**3 * p3_x
        y = (1-t)**3 * p0_y + 3*(1-t)**2 * t * p1_y + 3*(1-t) * t**2 * p2_y + t**3 * p3_y
        curve_points.append((x, y))

    # 부드러운 곡선 그리기
    draw.line(curve_points, fill=text_color, width=line_width, joint="curve")

    # 3. 화살표 머리 (Arrowhead) 그리기
    # 곡선 마지막 두 점을 이용해 각도 계산
    last_pt = curve_points[-1]
    prev_pt = curve_points[-5]  # 방향성을 위해 살짝 이전 점 선택
    
    angle = math.atan2(last_pt[1] - prev_pt[1], last_pt[0] - prev_pt[0])
    arrow_size = font_size * 0.6

    # 화살표 머리 다각형 계산
    arrow_pt1 = last_pt
    arrow_pt2 = (
        last_pt[0] - arrow_size * math.cos(angle - math.pi / 6),
        last_pt[1] - arrow_size * math.sin(angle - math.pi / 6)
    )
    arrow_pt3 = (
        last_pt[0] - arrow_size * math.cos(angle + math.pi / 6),
        last_pt[1] - arrow_size * math.sin(angle + math.pi / 6)
    )

    draw.polygon([arrow_pt1, arrow_pt2, arrow_pt3], fill=text_color)

    # 알파 블렌딩 합성
    composite = Image.alpha_composite(image, overlay)
    return composite.convert("RGB")


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 파일 로드 중: {INPUT_PATH.name}")
        doc = fitz.open(INPUT_PATH)
        
        if len(doc) == 0:
            raise ValueError("빈 PDF 파일입니다.")

        # 고해상도(300 DPI) 이미지 렌더링
        page = doc[0]
        zoom_factor = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # PIL Image 객체 생성
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"이미지 추출 완료 (고해상도: {img.width}x{img.height})")

        # 1. 이미지 보정 (선명도, 대비, 색도)
        img = enhance_image(img)

        # 2. 텍스트 및 꼬부랑 화살표 레이아웃 합성
        img_result = draw_squiggly_arrow_with_text(
            img, 
            TAG_TEXT, 
            start_ratio=(TEXT_X_RATIO, TEXT_Y_RATIO), 
            target_ratio=(TARGET_X_RATIO, TARGET_Y_RATIO)
        )

        # 3. 해상도 유지하며 PDF 저장
        logging.info("고해상도 PDF 생성 중...")
        img_result.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))
        
        logging.info(f"작업이 성공적으로 완료되었습니다! 저장 경로: {OUTPUT_PATH}")

    except Exception as e:
        logging.error(f"작업 중 예상치 못한 오류가 발생했습니다: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # 리소스 메모리 해제 보장
        if doc is not None:
            doc.close()


if __name__ == "__main__":
    main()