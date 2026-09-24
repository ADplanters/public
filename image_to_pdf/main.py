import os
import sys
import math
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# ---------------------------------------------------------------------------
# 1. 로깅 및 환경 설정
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

TARGET_DPI = 300
TAG_TEXT = "고리"

# ---------------------------------------------------------------------------
# 2. 정밀 좌표 설정 (비율 기준 0.0 ~ 1.0)
# ---------------------------------------------------------------------------
# 컴퓨터 하는 남자의 팔꿈치 위치 (텍스트 시작 위치)
TEXT_X_RATIO = 0.65
TEXT_Y_RATIO = 0.68

# 오른쪽 아래 강아지 위치 (화살표 도달 위치)
DOG_X_RATIO = 0.85
DOG_Y_RATIO = 0.82


def load_custom_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    요청하신 cursive.ttf 폰트를 우선적으로 로드하고, 
    파일이 없을 경우 시스템 내 대체 필기체/표준 폰트를 탐색합니다.
    """
    # 1. 현재 폴더 내 cursive.ttf 최우선 확인
    custom_font_path = BASE_DIR / "cursive.ttf"
    if custom_font_path.exists():
        try:
            logging.info(f"지정 폰트 로드 성공: {custom_font_path}")
            return ImageFont.truetype(str(custom_font_path), size=font_size)
        except Exception as e:
            logging.warning(f"지정 폰트({custom_font_path}) 로드 실패: {e}")

    # 2. 운영체제별 필기체/기본 폰트 폴백(Fallback)
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
                logging.info(f"대체 폰트 사용: {font_path}")
                return ImageFont.truetype(font_path, size=font_size)
            except Exception as e:
                logging.warning(f"폰트 로드 실패 ({font_path}): {e}")

    logging.warning("적절한 폰트를 찾지 못해 기본 폰트를 사용합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """고해상도 이미지 보정 (선명도 및 대비)"""
    logging.info("이미지 선명도 및 대비 자동 보정 중...")
    image = ImageEnhance.Sharpness(image).enhance(1.3)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    return image


def draw_curved_arrow(draw: ImageDraw.ImageDraw, p0: tuple, p3: tuple, color: tuple, width: int):
    """
    p0(텍스트)에서 p3(강아지)까지 자연스럽게 우하향하며 휘어지는 3차 베지에 곡선 화살표를 그립니다.
    """
    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]

    # 곡선 휘어짐 제어점 (S자/C자 형태의 부드러운 꼬부랑 곡선)
    p1 = (p0[0] + dx * 0.5, p0[1] + dy * 0.1)  # 우측으로 먼저 완만하게 이동
    p2 = (p0[0] + dx * 0.9, p0[1] + dy * 0.6)  # 아래로 곡선을 그리며 떨어짐

    # 베지에 곡선 좌표 생성
    steps = 60
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[1]
        curve_points.append((x, y))

    # 곡선 그리기
    draw.line(curve_points, fill=color, width=width, joint="curve")

    # 화살표 머리(Arrowhead) 정밀 계산
    last_pt = curve_points[-1]
    prev_pt = curve_points[-4]  # 접선 방향 추출
    angle = math.atan2(last_pt[1] - prev_pt[1], last_pt[0] - prev_pt[0])
    
    arrow_length = width * 4.5
    arrow_p1 = (
        last_pt[0] - arrow_length * math.cos(angle - math.pi / 6),
        last_pt[1] - arrow_length * math.sin(angle - math.pi / 6)
    )
    arrow_p2 = (
        last_pt[0] - arrow_length * math.cos(angle + math.pi / 6),
        last_pt[1] - arrow_length * math.sin(angle + math.pi / 6)
    )

    draw.polygon([last_pt, arrow_p1, arrow_p2], fill=color)


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 PDF 파일이 없습니다: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 파일 읽는 중: {INPUT_PATH.name}")
        doc = fitz.open(INPUT_PATH)
        
        if len(doc) == 0:
            raise ValueError("PDF에 페이지가 없습니다.")

        # 고해상도(300 DPI) 이미지 추출
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"이미지 추출 완료 (해상도: {img.width}x{img.height})")

        # 1. 이미지 화질 보정
        img = enhance_image(img)

        # 2. 텍스트 및 오버레이 레이어 준비 (RGBA)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # 3. 해상도 맞춤 크기 계산
        font_size = max(28, int(img.width * 0.038))
        font = load_custom_font(font_size)
        line_width = max(3, int(img.width * 0.0025))

        # 4. 좌표 계산
        # 남자의 팔꿈치 위치 (텍스트 배치)
        text_x = img.width * TEXT_X_RATIO
        text_y = img.height * TEXT_Y_RATIO

        # 강아지 위치 (화살표 타겟)
        dog_x = img.width * DOG_X_RATIO
        dog_y = img.height * DOG_Y_RATIO

        # 5. 흰색 박스 없이 가독성을 높이는 외곽선/후광 텍스트 렌더링
        text_color = (45, 30, 20, 255)       # 진한 밤색/검정
        halo_color = (255, 255, 255, 220)    # 부드러운 흰색 후광

        # 가독성을 위한 은은한 외곽선 처리 (박스는 전혀 없음)
        halo_radius = max(2, int(font_size * 0.06))
        for offset_x in range(-halo_radius, halo_radius + 1):
            for offset_y in range(-halo_radius, halo_radius + 1):
                if offset_x**2 + offset_y**2 <= halo_radius**2:
                    draw.text((text_x + offset_x, text_y + offset_y), TAG_TEXT, font=font, fill=halo_color)

        # 본 텍스트 렌더링
        draw.text((text_x, text_y), TAG_TEXT, font=font, fill=text_color)

        # 6. 텍스트에서 강아지로 향하는 휘어진 화살표 그리기
        bbox = draw.textbbox((text_x, text_y), TAG_TEXT, font=font)
        text_right_center = (bbox[2] + int(font_size * 0.2), text_y + (bbox[3] - bbox[1]) / 2)
        dog_target = (dog_x, dog_y)

        draw_curved_arrow(draw, text_right_center, dog_target, color=text_color, width=line_width)

        # 7. 이미지 합성 및 고해상도 PDF 저장
        composite = Image.alpha_composite(img, overlay).convert("RGB")
        logging.info(f"결과 PDF 생성 중: {OUTPUT_PATH.name}")
        composite.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))

        logging.info("성공적으로 작업이 완료되었습니다!")

    except Exception as e:
        logging.error(f"작업 실행 중 에러가 발생했습니다: {e}", exc_info=True)
        sys.exit(1)

    finally:
        if doc is not None:
            doc.close()


if __name__ == "__main__":
    main()