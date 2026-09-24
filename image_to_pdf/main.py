import os
import sys
import math
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ---------------------------------------------------------------------------
# 1. 로깅 및 작업 디렉토리 설정
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

# 텍스트 위치: 오른쪽 하단 강아지 오른쪽 귀 위쪽 / 컴퓨터 작업자 팔꿈치 부근 (비율 0.0 ~ 1.0)
TEXT_X_RATIO = 0.68
TEXT_Y_RATIO = 0.69

# 화살표 도달 위치: 우측 하단 갈색 강아지
DOG_X_RATIO = 0.83
DOG_Y_RATIO = 0.82

# 스타일 사양 (하얀색 텍스트, 스트로크/배경 없음)
TEXT_COLOR = (255, 255, 255, 255)  # 순백색 (Pure White)
ARROW_COLOR = (255, 255, 255, 255) # 하얀색 곡선 화살표


def load_cursive_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    지정된 cursive.ttf 폰트를 우선 로드하며, 미존재 시 시스템 필기체/표준 폰트로 예외 처리합니다.
    """
    target_font_path = BASE_DIR / "cursive.ttf"
    if target_font_path.exists():
        try:
            logging.info(f"지정 폰트 로드 성공: {target_font_path}")
            return ImageFont.truetype(str(target_font_path), size=font_size)
        except Exception as e:
            logging.warning(f"폰트 파일 로드 실패 ({target_font_path}): {e}")

    # 시스템 대체 폰트 경로
    fallback_paths = [
        # Windows
        "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/malgun.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/GungSeo.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        # Linux
        "/usr/share/fonts/truetype/nanum/NanumPen.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]

    for font_path in fallback_paths:
        if os.path.exists(font_path):
            try:
                logging.info(f"대체 폰트 로드: {font_path}")
                return ImageFont.truetype(font_path, size=font_size)
            except Exception:
                continue

    logging.warning("유효한 폰트를 찾지 못하여 기본 폰트를 적용합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """선명도 및 대비 자동 보정"""
    logging.info("이미지 화질 자동 보정 중 (Sharpness, Contrast)...")
    image = ImageEnhance.Sharpness(image).enhance(1.25)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    return image


def draw_curved_arrow(draw: ImageDraw.ImageDraw, start_pos: tuple, end_pos: tuple, color: tuple, width: int):
    """
    텍스트 위치에서 강아지를 향해 부드럽게 휘어져 내려가는 3차 베지에 곡선(Curved Arrow)을 그립니다.
    """
    p0 = start_pos
    p3 = end_pos

    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]

    # 곡선 제어점 (오른쪽 아래로 완만하게 휘어지는 곡선 생성)
    p1 = (p0[0] + dx * 0.6, p0[1] + dy * 0.1)
    p2 = (p0[0] + dx * 0.9, p0[1] + dy * 0.5)

    steps = 60
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[1]
        curve_points.append((x, y))

    # 곡선 그리기
    draw.line(curve_points, fill=color, width=width, joint="curve")

    # 화살표 머리 (Arrowhead) 각도 계산 및 다각형 렌더링
    last_pt = curve_points[-1]
    prev_pt = curve_points[-4]
    angle = math.atan2(last_pt[1] - prev_pt[1], last_pt[0] - prev_pt[0])

    arrow_size = width * 4.5
    arrow_p1 = (
        last_pt[0] - arrow_size * math.cos(angle - math.pi / 6),
        last_pt[1] - arrow_size * math.sin(angle - math.pi / 6)
    )
    arrow_p2 = (
        last_pt[0] - arrow_size * math.cos(angle + math.pi / 6),
        last_pt[1] - arrow_size * math.sin(angle + math.pi / 6)
    )

    draw.polygon([last_pt, arrow_p1, arrow_p2], fill=color)


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일이 존재하지 않습니다: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 로드 중: {INPUT_PATH.name}")
        doc = fitz.open(INPUT_PATH)

        if len(doc) == 0:
            raise ValueError("PDF 페이지가 비어 있습니다.")

        # 300 DPI 고해상도 픽스맵 변환
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"고해상도 이미지 변환 완료 ({img.width}x{img.height})")

        # 1. 이미지 보정
        img = enhance_image(img)

        # 2. 오버레이 레이어 생성 (배경 박스 없이 투명 레이어 사용)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # 3. 폰트 및 라인 크기 동적 산출
        font_size = max(28, int(img.width * 0.035))
        font = load_cursive_font(font_size)
        line_width = max(3, int(img.width * 0.0025))

        # 4. 좌표 계산
        text_x = img.width * TEXT_X_RATIO
        text_y = img.height * TEXT_Y_RATIO

        dog_x = img.width * DOG_X_RATIO
        dog_y = img.height * DOG_Y_RATIO

        # 5. 흰색 텍스트 렌더링 (배경 박스/외곽선 없음)
        draw.text((text_x, text_y), TAG_TEXT, font=font, fill=TEXT_COLOR)

        # 6. 휘어진 화살표(Curved Arrow) 렌더링 (텍스트 우측 하단 -> 강아지)
        bbox = draw.textbbox((text_x, text_y), TAG_TEXT, font=font)
        arrow_start_x = bbox[2] + int(font_size * 0.15)
        arrow_start_y = text_y + (bbox[3] - bbox[1]) * 0.7

        draw_curved_arrow(
            draw,
            start_pos=(arrow_start_x, arrow_start_y),
            end_pos=(dog_x, dog_y),
            color=ARROW_COLOR,
            width=line_width
        )

        # 7. 이미지 알파 블렌딩 및 고해상도 PDF 저장
        result_img = Image.alpha_composite(img, overlay).convert("RGB")
        logging.info(f"고해상도 PDF 저장 중: {OUTPUT_PATH.name}")
        result_img.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))

        logging.info("성공적으로 모든 작업이 완료되었습니다!")

    except Exception as e:
        logging.error(f"실행 중 에러 발생: {e}", exc_info=True)
        sys.exit(1)

    finally:
        if doc is not None:
            doc.close()


if __name__ == "__main__":
    main()