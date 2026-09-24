import os
import sys
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

# 현재 스크립트가 위치한 디렉토리(image_to_pdf)를 절대 경로로 계산
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres_tagged.pdf"

INPUT_PATH = BASE_DIR / INPUT_FILENAME
OUTPUT_PATH = BASE_DIR / OUTPUT_FILENAME

# ---------------------------------------------------------------------------
# 2. 고정밀 렌더링 및 레이아웃 설정
# ---------------------------------------------------------------------------
TARGET_DPI = 300
TAG_TEXT = "고리"

# 오른쪽 하단 강아지 머리 위 타겟 좌표 (이미지 전체 너비/높이 대비 비율)
# 필요에 따라 미세 조정 가능 (0.0 ~ 1.0)
TARGET_X_RATIO = 0.85  # 오른쪽
TARGET_Y_RATIO = 0.82  # 하단


def get_standard_korean_font(size: int) -> ImageFont.FreeTypeFont:
    """직책명 텍스트에 주로 쓰이는 깔끔한 고딕/산세리프 계열 한글 폰트를 로드합니다."""
    font_paths = [
        # Windows (맑은 고딕)
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        # macOS (애플 고딕)
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        # Linux (나눔고딕, 본고딕)
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                logging.info(f"적용 폰트: {font_path}")
                return ImageFont.truetype(font_path, size=size)
            except Exception as e:
                logging.warning(f"폰트 로드 실패 ({font_path}): {e}")

    logging.warning("시스템 한글 폰트를 찾을 수 없어 기본 폰트로 대체합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """전체적인 이미지 품질(선명도, 대비)을 자연스럽게 향상시킵니다."""
    logging.info("이미지 선명도 및 자동 보정 진행 중...")
    image = ImageEnhance.Sharpness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    return image


def draw_clean_note_arrow(image: Image.Image, text: str, target_x: float, target_y: float) -> Image.Image:
    """
    기존 사람들의 직책명 스타일(말풍선/Note Arrow)과 동일한 톤앤매너로 이름표를 생성합니다.
    """
    logging.info("직책명 스타일(Note Arrow) 텍스트 렌더링 중...")

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 해상도에 맞춘 폰트 및 디자인 스케일 계산
    font_size = max(24, int(image.width * 0.025))
    font = get_standard_korean_font(font_size)
    
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 텍스트 바운딩 박스 크기 측정
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 박스(말풍선) 크기 및 여백 설정
    padding_x = int(font_size * 0.8)
    padding_y = int(font_size * 0.5)
    box_width = text_width + (padding_x * 2)
    box_height = text_height + (padding_y * 2)
    
    # 하단 화살표(꼬리) 크기
    arrow_width = int(font_size * 0.8)
    arrow_height = int(font_size * 0.6)
    
    # 도형 좌표 계산 (타겟 포인트를 화살표 끝으로 설정하고 위로 쌓음)
    tip_x, tip_y = target_x, target_y
    box_bottom = tip_y - arrow_height
    box_top = box_bottom - box_height
    box_left = tip_x - (box_width / 2)
    box_right = tip_x + (box_width / 2)

    # Note Arrow 전체 다각형 꼭짓점
    polygon_points = [
        (box_left, box_top),                             # 1. 좌상단
        (box_right, box_top),                            # 2. 우상단
        (box_right, box_bottom),                         # 3. 우하단
        (tip_x + (arrow_width / 2), box_bottom),         # 4. 화살표 우측 시작점
        (tip_x, tip_y),                                  # 5. 화살표 끝점 (강아지 머리를 정확히 가리킴)
        (tip_x - (arrow_width / 2), box_bottom),         # 6. 화살표 좌측 시작점
        (box_left, box_bottom)                           # 7. 좌하단
    ]

    # 기존 스타일 모방 (깔끔한 흰색 바탕 + 짙은 회색 테두리 및 텍스트)
    bg_color = (255, 255, 255, 245)      # 거의 불투명한 흰색
    border_color = (60, 60, 60, 255)     # 짙은 회색 테두리
    text_color = (40, 40, 40, 255)       # 진한 텍스트 색상
    border_width = max(2, int(image.width * 0.002))

    # 1. 시인성을 위한 옅은 그림자
    shadow_offset = int(font_size * 0.1)
    shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in polygon_points]
    draw.polygon(shadow_points, fill=(0, 0, 0, 40))

    # 2. 메인 말풍선 그리기
    draw.polygon(polygon_points, fill=bg_color, outline=border_color, width=border_width)

    # 3. 텍스트 중앙 렌더링
    text_x = box_left + (box_width - text_width) / 2 - bbox[0]
    text_y = box_top + (box_height - text_height) / 2 - bbox[1]
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # 원본 이미지와 겹치기
    composite = Image.alpha_composite(image, overlay)
    return composite.convert("RGB")


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일이 존재하지 않습니다. 경로를 확인하세요: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 파일 로드 중: {INPUT_PATH.name}")
        doc = fitz.open(INPUT_PATH)
        
        if len(doc) == 0:
            raise ValueError("PDF 파일에 페이지가 없습니다.")

        # 고해상도(300 DPI 기준) 스케일링으로 이미지 추출
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"이미지 추출 완료 (해상도: {img.width}x{img.height})")

        # 1. 이미지 화질 보정
        img = enhance_image(img)

        # 2. 우측 하단 강아지 위치 계산
        target_pos_x = img.width * TARGET_X_RATIO
        target_pos_y = img.height * TARGET_Y_RATIO

        # 3. 직책명 스타일 이름표 합성
        img_result = draw_clean_note_arrow(img, TAG_TEXT, target_pos_x, target_pos_y)

        # 4. 고해상도 PDF로 저장
        logging.info("합성된 이미지를 고해상도 PDF로 저장 중...")
        img_result.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))
        
        logging.info(f"작업 완료! 파일이 성공적으로 생성되었습니다: {OUTPUT_PATH.name}")

    except Exception as e:
        logging.error(f"작업 중 오류가 발생했습니다: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # 리소스 메모리 안전 해제
        if doc is not None:
            doc.close()


if __name__ == "__main__":
    main()