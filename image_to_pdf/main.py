import os
import sys
import math
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ---------------------------------------------------------------------------
# 1. 환경 및 로깅 설정
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres_tagged.pdf"

INPUT_PATH = BASE_DIR / INPUT_FILENAME
OUTPUT_PATH = BASE_DIR / OUTPUT_FILENAME

# ---------------------------------------------------------------------------
# 2. 고해상도 및 텍스트/화살표 스타일 설정
# ---------------------------------------------------------------------------
TARGET_DPI = 300
TAG_TEXT = "고리"

# 텍스트 위치: 오른쪽 하단 갈색 강아지의 우측 귀 바로 위
TEXT_X_RATIO = 0.81
TEXT_Y_RATIO = 0.73

# 화살표 도달 위치: 갈색 강아지 머리
DOG_X_RATIO = 0.84
DOG_Y_RATIO = 0.80

# 스타일: 순백색 텍스트 & 순백색 굵은 화살표 (Stroke/Box 없음)
WHITE_COLOR = (255, 255, 255, 255)


def load_cursive_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    지정된 cursive.ttf 폰트를 최우선 로드하며, 미존재 시 시스템 필기체/표준 폰트로 예외 처리합니다.
    """
    target_font_path = BASE_DIR / "cursive.ttf"
    if target_font_path.exists():
        try:
            logging.info(f"지정 폰트 로드 성공: {target_font_path}")
            return ImageFont.truetype(str(target_font_path), size=font_size)
        except Exception as e:
            logging.warning(f"지정 폰트 로드 실패 ({target_font_path}): {e}")

    # 시스템 대체 폰트 경로
    fallback_paths = [
        # Windows
        "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/malgunbd.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/GungSeo.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        # Linux
        "/usr/share/fonts/truetype/nanum/NanumPen.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    ]

    for font_path in fallback_paths:
        if os.path.exists(font_path):
            try:
                logging.info(f"대체 폰트 로드: {font_path}")
                return ImageFont.truetype(font_path, size=font_size)
            except Exception:
                continue

    logging.warning("유효한 폰트를 찾지 못해 기본 폰트를 적용합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """고해상도 이미지 선명도 및 대비 자동 보정"""
    logging.info("이미지 화질 보정 진행 중...")
    image = ImageEnhance.Sharpness(image).enhance(1.25)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    return image


def draw_short_thick_curved_arrow(draw: ImageDraw.ImageDraw, start_pos: tuple, end_pos: tuple, color: tuple, width: int):
    """
    텍스트에서 강아지를 향해 내려가는 짧고 굵은 곡선 화살표(Curved Arrow)를 그립니다.
    """
    p0 = start_pos
    p3 = end_pos

    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]

    # 거리 비례 제어점 설정 (짧고 자연스러운 곡률 형성)
    p1 = (p0[0] + dx * 0.4 + width * 1.5, p0[1] + dy * 0.2)
    p2 = (p0[0] + dx * 0.8 + width * 1.5, p0[1] + dy * 0.7)

    steps = 40
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[1]
        curve_points.append((x, y))

    # 굵은 곡선 그리기
    draw.line(curve_points, fill=color, width=width, joint="round")

    # 선 두께에 맞춘 굵은 화살표 머리(Arrowhead) 렌더링
    last_pt = curve_points[-1]
    prev_pt = curve_points[-3]
    angle = math.atan2(last_pt[1] - prev_pt[1], last_pt[0] - prev_pt[0])

    arrow_size = width * 3.2
    arrow_p1 = (
        last_pt[0] - arrow_size * math.cos(angle - math.pi / 5),
        last_pt[1] - arrow_size * math.sin(angle - math.pi / 5)
    )
    arrow_p2 = (
        last_pt[0] - arrow_size * math.cos(angle + math.pi / 5),
        last_pt[1] - arrow_size * math.sin(angle + math.pi / 5)
    )

    draw.polygon([last_pt, arrow_p1, arrow_p2], fill=color)


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일이 없습니다: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 파일 로드 중: {INPUT_PATH.name}")
        doc = fitz.open(INPUT_PATH)

        if len(doc) == 0:
            raise ValueError("PDF에 페이지가 존재하지 않습니다.")

        # 300 DPI 고해상도 변환
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"고해상도 이미지 변환 완료 ({img.width}x{img.height})")

        # 1. 화질 보정
        img = enhance_image(img)

        # 2. 오버레이 레이어 준비
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # 3. 크기 계산 (폰트 및 화살표 두께)
        font_size = max(32, int(img.width * 0.038))
        font = load_cursive_font(font_size)
        
        # '짧고 굵은' 화살표를 위해 라인 두께를 기존 대비 크게 설정
        line_width = max(7, int(img.width * 0.005))

        # 4. 좌표 계산
        text_x = img.width * TEXT_X_RATIO
        text_y = img.height * TEXT_Y_RATIO

        dog_x = img.width * DOG_X_RATIO
        dog_y = img.height * DOG_Y_RATIO

        # 5. 순백색 텍스트 렌더링 (배경 박스 및 stroke 없음)
        draw.text((text_x, text_y), TAG_TEXT, font=font, fill=WHITE_COLOR)

        # 6. 짧고 굵은 휘어진 화살표 렌더링 (텍스트 하단 -> 강아지)
        bbox = draw.textbbox((text_x, text_y), TAG_TEXT, font=font)
        arrow_start_x = text_x + (bbox[2] - bbox[0]) * 0.5
        arrow_start_y = bbox[3] + int(font_size * 0.1)

        draw_short_thick_curved_arrow(
            draw,
            start_pos=(arrow_start_x, arrow_start_y),
            end_pos=(dog_x, dog_y),
            color=WHITE_COLOR,
            width=line_width
        )

        # 7. 알파 블렌딩 및 고해상도 PDF 저장
        result_img = Image.alpha_composite(img, overlay).convert("RGB")
        logging.info(f"결과 PDF 생성 중: {OUTPUT_PATH.name}")
        result_img.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))

        logging.info("성공적으로 완벽하게 작업이 완료되었습니다!")

    except Exception as e:
        logging.error(f"실행 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)

    finally:
        if doc is not None:
            doc.close()


if __name__ == "__main__":
    main()