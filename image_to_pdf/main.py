import os
import sys
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# ---------------------------------------------------------------------------
# 로깅 설정
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ---------------------------------------------------------------------------
# 경로 및 기본 설정
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres_tagged.pdf"

INPUT_PATH = BASE_DIR / INPUT_FILENAME
OUTPUT_PATH = BASE_DIR / OUTPUT_FILENAME

# 고해상도 처리를 위한 DPI 설정
TARGET_DPI = 300

# 이름표 설정
TAG_TEXT = "고리"

# 강아지 머리 위 오른쪽 위치 비율 (이미지 크기 대비 X: 0.65, Y: 0.25)
# 사용자의 이미지 구도에 맞게 필요시 비율을 조정할 수 있습니다.
POSITION_RATIO_X = 0.65
POSITION_RATIO_Y = 0.25


def get_korean_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """운영체제별 한글 폰트를 탐색하여 로드하고, 없을 경우 기본 폰트로 폴백합니다."""
    font_paths = [
        # Windows
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        # macOS
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        # Linux (Ubuntu/Debian)
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception as e:
                logging.warning(f"폰트 로드 실패 ({font_path}): {e}")

    logging.warning("시스템 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """선명도 및 대비를 조절하여 이미지 품질을 보정합니다."""
    logging.info("이미지 선명도 및 대비 보정 중...")
    
    # 선명도(Sharpness) 향상
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.3)
    
    # 대비(Contrast) 미세 향상
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.05)
    
    return image


def draw_nametag(image: Image.Image, text: str, pos_x: int, pos_y: int) -> Image.Image:
    """
    추석 카드 컨셉에 어울리는 소프트하고 고급스러운 이름표 뱃지를 생성하여 이미지에 합성합니다.
    """
    logging.info(f"'{text}' 이름표 추가 중 (좌표: X={pos_x}, Y={pos_y})...")
    
    # 원본 이미지가 RGBA가 아닐 경우 변환
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 캔버스 크기 기준 폰트 크기 동적 계산 (너비의 약 3%)
    font_size = max(24, int(image.width * 0.03))
    font = get_korean_font(font_size)

    # 텍스트 바운딩 박스 계산
    dummy_draw = ImageDraw.Draw(image)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 여백 및 뱃지 크기 설정
    padding_x = int(font_size * 0.8)
    padding_y = int(font_size * 0.4)
    badge_width = text_width + (padding_x * 2)
    badge_height = text_height + (padding_y * 2)

    # 이름표 오버레이 레이어 생성
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 뱃지 영역 정의 (둥근 사각형)
    left = pos_x - (badge_width // 2)
    top = pos_y - (badge_height // 2)
    right = left + badge_width
    bottom = top + badge_height
    corner_radius = badge_height // 3

    # 1. 그림자 효과 (Soft Shadow)
    shadow_offset = int(font_size * 0.15)
    shadow_box = [left + shadow_offset, top + shadow_offset, right + shadow_offset, bottom + shadow_offset]
    draw.rounded_rectangle(shadow_box, radius=corner_radius, fill=(0, 0, 0, 60))
    
    # 그림자 블러 처리
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=shadow_offset // 2))
    draw = ImageDraw.Draw(overlay)

    # 2. 메인 뱃지 배경 (추석 카드와 조화로운 따뜻한 크림 베이지 톤)
    badge_bg_color = (255, 248, 238, 235)  # Soft Cream Gold
    border_color = (212, 160, 89, 255)    # Traditional Gold Line
    border_width = max(2, int(font_size * 0.06))

    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=corner_radius,
        fill=badge_bg_color,
        outline=border_color,
        width=border_width
    )

    # 3. 텍스트 중앙 배치 및 렌더링
    text_x = left + (badge_width - text_width) // 2 - bbox[0]
    text_y = top + (badge_height - text_height) // 2 - bbox[1]
    text_color = (74, 44, 23, 255)  # Deep Warm Brown

    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # 원본 이미지와 알파 합성
    composite = Image.alpha_composite(image, overlay)
    return composite.convert("RGB")


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일이 존재하지 않습니다: {INPUT_PATH}")
        sys.exit(1)

    try:
        logging.info(f"PDF 파일 읽는 중: {INPUT_PATH}")
        doc = fitz.open(INPUT_PATH)
        
        if len(doc) == 0:
            raise ValueError("PDF 파일에 페이지가 없습니다.")

        # 첫 번째 페이지 추출 및 고해상도 이미지 변환 (300 DPI)
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # PIL Image 변환
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"이미지 추출 완료 (해상도: {img.width}x{img.height})")

        # 1. 이미지 선명도/대비 보정
        img = enhance_image(img)

        # 2. 지정된 위치(강아지 머리 위 오른쪽) 좌표 계산
        target_x = int(img.width * POSITION_RATIO_X)
        target_y = int(img.height * POSITION_RATIO_Y)

        # 3. 컨셉에 맞춘 이름표 렌더링
        img_tagged = draw_nametag(img, TAG_TEXT, target_x, target_y)

        # 4. 고해상도 PDF로 재저장
        logging.info(f"결과 PDF 생성 중: {OUTPUT_PATH}")
        img_tagged.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))
        
        doc.close()
        logging.info(f"성공적으로 완료되었습니다! 파일 저장 위치: {OUTPUT_PATH}")

    except Exception as e:
        logging.error(f"작업 중 오류가 발생했습니다: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()