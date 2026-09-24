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

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_고리추가_highres_tagged.pdf"

INPUT_PATH = BASE_DIR / INPUT_FILENAME
OUTPUT_PATH = BASE_DIR / OUTPUT_FILENAME

# ---------------------------------------------------------------------------
# 2. 디자인 및 위치 설정 (사용자 맞춤형)
# ---------------------------------------------------------------------------
TARGET_DPI = 300
TAG_TEXT = "고리"

# [중요] 화살표 끝부분(강아지 머리 위 정확한 타겟 포인트)의 위치 비율
# 이미지 전체 폭/높이 대비 비율입니다. (0.0 ~ 1.0)
# 필요시 강아지의 정확한 위치에 맞게 미세 조정하세요.
TARGET_X_RATIO = 0.65  # 가로 위치 (오른쪽으로 치우친 위치)
TARGET_Y_RATIO = 0.55  # 세로 위치 (강아지 머리 위쪽 타겟)


def get_korean_font(size: int) -> ImageFont.FreeTypeFont:
    """운영체제별 한글 폰트를 탐색하여 로드 (고해상도 텍스트 렌더링용)"""
    font_paths = [
        # Windows
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
        # Linux
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception as e:
                logging.warning(f"폰트 로드 실패 ({font_path}): {e}")

    logging.warning("시스템 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다. (한글이 깨질 수 있습니다)")
    return ImageFont.load_default()


def enhance_image(image: Image.Image) -> Image.Image:
    """고해상도 이미지의 선명도와 대비를 자연스럽게 보정합니다."""
    logging.info("이미지 선명도 및 대비 자동 보정 진행 중...")
    
    # 선명도 (Sharpness) 30% 향상
    enhancer_sharp = ImageEnhance.Sharpness(image)
    image = enhancer_sharp.enhance(1.3)
    
    # 대비 (Contrast) 10% 향상
    enhancer_contrast = ImageEnhance.Contrast(image)
    image = enhancer_contrast.enhance(1.1)
    
    return image


def draw_note_arrow_tag(image: Image.Image, text: str, target_x: float, target_y: float) -> Image.Image:
    """
    강아지 머리를 정확히 가리키는 말풍선(지시선, Note Arrow) 스타일을 그립니다.
    사람들 머리 위의 기존 디자인 톤(깔끔한 박스와 하단 화살표)을 모방합니다.
    """
    logging.info(f"지시선(Note Arrow) 스타일 렌더링 중... (타겟 좌표: X={int(target_x)}, Y={int(target_y)})")

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 해상도 비례 폰트 및 디자인 요소 크기 계산
    font_size = max(20, int(image.width * 0.025))
    font = get_korean_font(font_size)
    
    # 투명 오버레이 레이어 생성
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 텍스트 크기 측정
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 박스 및 화살표 크기 설정
    padding_x = int(font_size * 0.8)
    padding_y = int(font_size * 0.5)
    box_width = text_width + (padding_x * 2)
    box_height = text_height + (padding_y * 2)
    
    arrow_width = int(font_size * 1.2)
    arrow_height = int(font_size * 0.8)
    
    # 도형 기하학적 좌표 계산 (타겟 포인트를 기준으로 위로 쌓아올림)
    # 화살표 끝점 (타겟)
    tip_x, tip_y = target_x, target_y
    
    # 박스 하단 Y 좌표
    box_bottom = tip_y - arrow_height
    # 박스 상단 Y 좌표
    box_top = box_bottom - box_height
    # 박스 좌우 X 좌표 (타겟 X를 기준으로 중앙 정렬)
    box_left = tip_x - (box_width / 2)
    box_right = tip_x + (box_width / 2)

    # Note Arrow 다각형 꼭짓점 좌표 (시계 방향: 좌상 -> 우상 -> 우하 -> 화살표 우측 -> 화살표 끝 -> 화살표 좌측 -> 좌하)
    polygon_points = [
        (box_left, box_top),                             # 1. 좌상단
        (box_right, box_top),                            # 2. 우상단
        (box_right, box_bottom),                         # 3. 우하단
        (tip_x + (arrow_width / 2), box_bottom),         # 4. 화살표 우측 시작점
        (tip_x, tip_y),                                  # 5. 화살표 끝점 (강아지 가리킴)
        (tip_x - (arrow_width / 2), box_bottom),         # 6. 화살표 좌측 시작점
        (box_left, box_bottom)                           # 7. 좌하단
    ]

    # 스타일 설정 (기존 이미지의 깔끔한 텍스트 스타일 톤 매너)
    fill_color = (255, 255, 255, 240)    # 약간 투명한 깔끔한 흰색 배경
    outline_color = (30, 30, 30, 255)    # 짙은 회색/검정 테두리
    text_color = (30, 30, 30, 255)       # 짙은 텍스트 색상
    line_width = max(2, int(image.width * 0.002)) # 해상도 비례 테두리 두께

    # 1. 그림자 효과 (옵션: 입체감을 위해 살짝 우측 하단에 어두운 폴리곤 추가)
    shadow_offset = max(2, int(font_size * 0.1))
    shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in polygon_points]
    draw.polygon(shadow_points, fill=(0, 0, 0, 50))

    # 2. 메인 말풍선(지시선) 그리기
    draw.polygon(polygon_points, fill=fill_color, outline=outline_color, width=line_width)

    # 3. 텍스트 중앙 정렬 및 렌더링
    # 박스 내부의 정확한 중앙 좌표 계산
    text_x = box_left + (box_width - text_width) / 2 - bbox[0]
    text_y = box_top + (box_height - text_height) / 2 - bbox[1]
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # 알파 블렌딩 합성
    composite = Image.alpha_composite(image, overlay)
    return composite.convert("RGB")


def main():
    if not INPUT_PATH.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다. 파일명과 경로를 확인하세요: {INPUT_PATH}")
        sys.exit(1)

    doc = None
    try:
        logging.info(f"PDF 파일 로드 중: {INPUT_PATH}")
        doc = fitz.open(INPUT_PATH)
        
        if len(doc) == 0:
            raise ValueError("빈 PDF 파일입니다.")

        # 고해상도 이미지 추출 (DPI 기반 Matrix 스케일링)
        page = doc[0]
        zoom = TARGET_DPI / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # PyMuPDF 픽스맵을 PIL Image로 변환
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        logging.info(f"이미지 추출 성공 (초고해상도: {img.width}x{img.height})")

        # 1. 전반적인 이미지 품질(선명도, 대비) 보정
        img = enhance_image(img)

        # 2. 강아지를 가리키는 정확한 좌표 산출
        target_pos_x = img.width * TARGET_X_RATIO
        target_pos_y = img.height * TARGET_Y_RATIO

        # 3. Note Arrow 스타일 텍스트 합성
        img_result = draw_note_arrow_tag(img, TAG_TEXT, target_pos_x, target_pos_y)

        # 4. 품질 저하 없이 고해상도 PDF로 저장
        logging.info(f"결과물을 PDF로 저장하는 중... (경로: {OUTPUT_PATH})")
        img_result.save(OUTPUT_PATH, "PDF", resolution=float(TARGET_DPI))
        
        logging.info(f"작업 완료! 파일이 성공적으로 생성되었습니다: {OUTPUT_PATH.name}")

    except Exception as e:
        logging.error(f"처리 중 오류가 발생했습니다: {e}", exc_info=True)
        sys.exit(1)
        
    finally:
        # 리소스 메모리 해제 보장
        if doc is not None:
            doc.close()

if __name__ == "__main__":
    main()