# =============================================================================
# [실행 전 필요 패키지 설치 안내]
# 터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치해 주세요.
# pip install Pillow
# =============================================================================

import os
import logging
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -----------------------------------------------------------------------------
# 1. 로깅 및 환경 설정
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 현재 스크립트가 위치한 절대 경로를 기반으로 작업 디렉토리 설정 (GitHub public 구조 대응)
BASE_DIR = Path(__file__).resolve().parent

# 파일 경로 설정 (사용자 요청 파일명 반영)
# ※ 주의: PIL은 이미지 파일(jpg, png 등)을 직접 다루는 데 최적화되어 있습니다. 
# 만약 입력 파일이 PDF라면 이미지(jpg/png)로 먼저 변환 후 사용하시길 권장합니다.
INPUT_IMAGE_NAME = "애드플랜터스_추석_인사_카드_고리수정.jpg" # 또는 .png
OUTPUT_PDF_NAME = "애드플랜터스_추석_인사_카드_고리수정_최종출력.pdf"
FONT_NAME = "NanumGothicBold.ttf"

INPUT_IMAGE_PATH = BASE_DIR / INPUT_IMAGE_NAME
OUTPUT_PDF_PATH = BASE_DIR / OUTPUT_PDF_NAME
FONT_PATH = BASE_DIR / FONT_NAME

# 최대 해상도 출력 설정
DPI = 600.0  # 인쇄용 초고해상도 지원

# =============================================================================
# [직책명표 스타일 커스텀 설정] 
# 원본 이미지 내 다른 사람들의 직책명 스타일과 동일하게 색상을 맞춰주세요.
# =============================================================================
TAG_BG_COLOR = "#FFFFFF"       # 직책명표 배경색 (예: 흰색)
TAG_TEXT_COLOR = "#1A1A1A"     # 직책명표 글자색 (예: 진한 검정/회색)
TAG_BORDER_COLOR = "#CCCCCC"   # 직책명표 테두리색
TAG_BORDER_WIDTH = 5           # 테두리 두께 (고해상도에 맞춰 두껍게 설정)
TAG_RADIUS = 20                # 상자 모서리 둥근 정도 (0이면 직각, 커질수록 둥글어짐)
# =============================================================================

# -----------------------------------------------------------------------------
# 2. 리소스 자동 다운로드 (단정하고 가독성 높은 고딕 폰트)
# -----------------------------------------------------------------------------
def ensure_resources():
    """직책명 텍스트를 위한 무료 한글 폰트(나눔고딕 볼드) 다운로드"""
    if not FONT_PATH.exists():
        logging.info("로컬에 한글 폰트가 없어 다운로드합니다...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        try:
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
            logging.info("폰트 다운로드 완료.")
        except Exception as e:
            logging.error(f"폰트 다운로드 실패: {e}")
            raise

# -----------------------------------------------------------------------------
# 3. 메인 이미지 처리 및 고해상도 PDF 변환 로직
# -----------------------------------------------------------------------------
def process_and_save_to_pdf():
    logging.info(f"작업을 시작합니다. 대상 파일: {INPUT_IMAGE_NAME}")

    try:
        ensure_resources()
    except Exception:
        return

    # 입력 파일 존재 여부 확인 (확장자 유연성 제공)
    input_path = INPUT_IMAGE_PATH
    if not input_path.exists():
        # 확장자가 다를 경우를 대비한 체크
        alt_path_png = BASE_DIR / f"{INPUT_IMAGE_PATH.stem}.png"
        alt_path_jpeg = BASE_DIR / f"{INPUT_IMAGE_PATH.stem}.jpeg"
        if alt_path_png.exists(): input_path = alt_path_png
        elif alt_path_jpeg.exists(): input_path = alt_path_jpeg
        else:
            logging.error(f"입력 파일을 찾을 수 없습니다: {INPUT_IMAGE_NAME}")
            logging.error("파일이 main.py와 같은 폴더에 있고, 확장자가 jpg 또는 png인지 확인해주세요.")
            return

    try:
        # 1) 원본 고해상도 이미지 로드 및 리소스 관리
        with Image.open(input_path) as base_img:
            # 안전한 처리를 위해 RGB 모드로 변환 (알파 채널 제거)
            working_img = base_img.convert("RGB")
            width, height = working_img.size
            logging.info(f"원본 이미지 로드 완료 (해상도: {width} x {height})")

            # 고해상도 품질 유지를 위한 스무딩 처리 (픽셀 튀는 현상 완화)
            working_img = working_img.filter(ImageFilter.SMOOTH)

            # 2) 직책명표 디자인 설정
            draw = ImageDraw.Draw(working_img)
            
            # 해상도에 비례하여 직책명 폰트 크기 동적 할당 (너비의 약 2.5%)
            font_size = int(width * 0.025)
            if font_size < 20: font_size = 20
            font = ImageFont.truetype(str(FONT_PATH), size=font_size)
            
            name_text = "고리"
            
            # 텍스트가 차지하는 영역(Bounding Box) 계산
            bbox = draw.textbbox((0, 0), name_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 3) 직책명표(상자)의 크기와 여백 설정
            padding_x = int(font_size * 0.8) # 좌우 여백
            padding_y = int(font_size * 0.4) # 상하 여백
            box_width = text_width + (padding_x * 2)
            box_height = text_height + (padding_y * 2)
            
            # 4) 직책명표 위치 계산 (우측 하단 강아지 머리 위로 추정)
            # 🎯 [중요] 강아지의 정확한 위치에 맞추려면 아래 비율(0.85, 0.80)을 수정하세요.
            # 0.85는 우측에서 15% 떨어진 곳, 0.80은 하단에서 20% 떨어진 곳을 의미합니다.
            dog_x = int(width * 0.85)
            dog_y = int(height * 0.80)
            
            box_x0 = dog_x - (box_width // 2)
            box_y0 = dog_y - box_height
            box_x1 = box_x0 + box_width
            box_y1 = box_y0 + box_height
            
            # 5) 직책명표 배경 상자 그리기 (둥근 모서리 직사각형)
            draw.rounded_rectangle(
                [box_x0, box_y0, box_x1, box_y1], 
                radius=TAG_RADIUS, 
                fill=TAG_BG_COLOR,
                outline=TAG_BORDER_COLOR,
                width=TAG_BORDER_WIDTH
            )
            
            # 6) 직책명표 중앙에 텍스트 그리기
            text_x = box_x0 + padding_x
            text_y = box_y0 + padding_y - int(font_size * 0.1) # 시각적 중앙 정렬을 위한 미세 조정
            
            draw.text((text_x, text_y), name_text, font=font, fill=TAG_TEXT_COLOR)
            logging.info("강아지 위에 '고리' 직책명표 부착 완료.")

            # 7) 최대 해상도 PDF로 출력
            logging.info("초고해상도(최대 화질) PDF 파일 저장을 시작합니다...")
            # quality=100 및 높은 DPI(600)를 명시하여 화질 손실 방지
            working_img.save(
                OUTPUT_PDF_PATH, 
                "PDF", 
                resolution=DPI, 
                quality=100, 
                save_all=True
            )
            logging.info(f"★성공★ 고해상도 PDF 생성 완료: {OUTPUT_PDF_PATH}")

    except MemoryError:
        logging.error("메모리 부족: 처리하려는 이미지의 해상도가 너무 높습니다. 시스템 리소스를 확인하세요.")
    except PermissionError:
        logging.error(f"권한 오류: '{OUTPUT_PDF_NAME}' 파일이 이미 열려있는지 확인하고 종료 후 다시 실행하세요.")
    except Exception as e:
        logging.error(f"작업 중 예기치 못한 오류 발생: {e}")

# -----------------------------------------------------------------------------
# 메인 실행부
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        process_and_save_to_pdf()
    except KeyboardInterrupt:
        logging.warning("\n사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        logging.critical(f"심각한 오류 발생: {e}")