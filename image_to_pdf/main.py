# =============================================================================
# [실행 전 필요 패키지 설치 안내]
# 터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치해 주세요.
# pip install Pillow requests
# =============================================================================

import os
import json
import logging
import urllib.request
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 1. 로깅 및 환경 설정
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 현재 스크립트가 위치한 절대 경로를 기반으로 작업 디렉토리 설정 (image_to_pdf 폴더 내부 기준)
BASE_DIR = Path(__file__).resolve().parent

# 파일 경로 설정
INPUT_IMAGE_NAME = "애드플랜터스_추석_인사_카드_highres_page-0001.jpg"
SHIBA_IMAGE_NAME = "shiba.png"
OUTPUT_PDF_NAME = "output_highres.pdf"
FONT_NAME = "NanumGothicBold.ttf"

INPUT_IMAGE_PATH = BASE_DIR / INPUT_IMAGE_NAME
SHIBA_IMAGE_PATH = BASE_DIR / SHIBA_IMAGE_NAME
OUTPUT_PDF_PATH = BASE_DIR / OUTPUT_PDF_NAME
FONT_PATH = BASE_DIR / FONT_NAME

# =============================================================================
# [직책명 스타일 커스텀 설정] - 원본 이미지의 사람 직책명 스타일에 맞게 수정하세요!
# =============================================================================
TITLE_BG_COLOR = "#333333"    # 직책명 배경색 (예: 어두운 회색. 필요시 흰색 "#FFFFFF" 등으로 변경)
TITLE_TEXT_COLOR = "#FFFFFF"  # 직책명 글자색 (예: 흰색. 배경이 밝으면 "#000000" 으로 변경)
TITLE_BORDER_COLOR = "#333333"# 직책명 테두리색 (배경과 같게 하거나 특정 색상 지정)
TITLE_BORDER_WIDTH = 2        # 직책명 테두리 두께
TITLE_RADIUS = 8              # 상자 모서리 둥근 정도 (0이면 완전한 직사각형, 커질수록 둥글어짐)
TITLE_FONT_SIZE = 45          # 직책명 폰트 크기
# =============================================================================

# -----------------------------------------------------------------------------
# 2. 리소스 자동 다운로드 (한글 폰트 및 시바견 이미지)
# -----------------------------------------------------------------------------
def ensure_korean_font():
    """직책명 텍스트를 위한 무료 한글 폰트(나눔고딕 볼드) 다운로드"""
    if not FONT_PATH.exists():
        logging.info("로컬에 한글 폰트가 없어 다운로드합니다...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_PATH)
            logging.info("폰트 다운로드 완료.")
        except Exception as e:
            logging.error(f"폰트 다운로드 실패: {e}")
            raise

def ensure_shiba_image():
    """시바견 이미지가 없으면 무료 API(dog.ceo)에서 자동 다운로드"""
    if not SHIBA_IMAGE_PATH.exists():
        logging.info("시바견 이미지가 없어 무료 API에서 사진을 다운로드합니다...")
        try:
            req = urllib.request.Request(
                "https://dog.ceo/api/breed/shiba/images/random",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                img_url = data['message']
            urllib.request.urlretrieve(img_url, SHIBA_IMAGE_PATH)
            logging.info("시바견 이미지 다운로드 완료.")
        except Exception as e:
            logging.error(f"시바견 이미지 다운로드 실패: {e}")
            raise

# -----------------------------------------------------------------------------
# 3. 메인 이미지 처리 및 PDF 변환 로직
# -----------------------------------------------------------------------------
def main():
    logging.info("고해상도 이미지 처리 및 직책명(고리) 부착 작업을 시작합니다.")

    if not INPUT_IMAGE_PATH.exists():
        logging.error(f"입력 이미지를 찾을 수 없습니다: {INPUT_IMAGE_PATH}")
        return

    try:
        ensure_korean_font()
        ensure_shiba_image()
        
        font = ImageFont.truetype(str(FONT_PATH), size=TITLE_FONT_SIZE) 

        # 1) 원본 이미지 로드
        with Image.open(INPUT_IMAGE_PATH) as base_img:
            base_img = base_img.convert("RGB")
            bg_width, bg_height = base_img.size
            logging.info(f"원본 해상도: {bg_width} x {bg_height}")

            # 2) 고해상도 품질 유지 및 픽셀 깨짐(계단현상) 방지를 위한 슈퍼 샘플링
            logging.info("픽셀을 자연스럽게 잇기 위한 슈퍼 샘플링 및 스무딩을 진행합니다...")
            # 이미지를 2배 확대 (Lanczos 알고리즘으로 품질 보존)
            supersampled = base_img.resize((bg_width * 2, bg_height * 2), Image.Resampling.LANCZOS)
            # 픽셀 경계 부드럽게 처리
            supersampled = supersampled.filter(ImageFilter.SMOOTH_MORE)
            # 원래 크기로 복원 (계단 현상이 매우 부드러워짐)
            smoothed_img = supersampled.resize((bg_width, bg_height), Image.Resampling.LANCZOS)

            # 3) 시바견 이미지 로드 및 합성
            with Image.open(SHIBA_IMAGE_PATH) as shiba_img:
                shiba_img = shiba_img.convert("RGBA")
                
                # 강아지 이미지를 원본 배경의 약 15% 크기로 설정
                target_width = int(bg_width * 0.15)
                shiba_resized = shiba_img.resize((target_width, target_width), Image.Resampling.LANCZOS)
                
                # 깔끔한 원형으로 오려내기 (사람들 프로필과 비슷하게 연출)
                mask = Image.new("L", (target_width, target_width), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, target_width, target_width), fill=255)
                
                # 우측 하단 여백 설정
                margin = 80
                paste_x = bg_width - target_width - margin
                paste_y = bg_height - target_width - margin
                
                smoothed_img.paste(shiba_resized, (paste_x, paste_y), mask=mask)
                logging.info("시바견 이미지 우측 하단 합성 완료.")

                # 4) 직책명 스타일 이름표('고리') 추가
                draw = ImageDraw.Draw(smoothed_img)
                name_text = "고리"
                
                # 텍스트가 차지하는 영역 계산
                bbox = draw.textbbox((0, 0), name_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 직책명 박스의 여백(Padding) 설정
                padding_x, padding_y = 25, 12
                box_width = text_width + (padding_x * 2)
                box_height = text_height + (padding_y * 2)
                
                # 직책명 박스 위치 (시바견 상단 중앙)
                box_x0 = paste_x + (target_width - box_width) // 2
                box_y0 = paste_y - box_height - 15 
                box_x1 = box_x0 + box_width
                box_y1 = box_y0 + box_height
                
                # 직책명 스타일 박스 그리기 (상단 설정 변수 반영)
                draw.rounded_rectangle(
                    [box_x0, box_y0, box_x1, box_y1], 
                    radius=TITLE_RADIUS, 
                    fill=TITLE_BG_COLOR,
                    outline=TITLE_BORDER_COLOR,
                    width=TITLE_BORDER_WIDTH
                )
                
                # 박스 중앙에 텍스트 그리기
                text_x = box_x0 + padding_x
                # 폰트 베이스라인 조정을 위해 살짝 위로(-5) 올림
                text_y = box_y0 + padding_y - 5 
                draw.text((text_x, text_y), name_text, font=font, fill=TITLE_TEXT_COLOR)
                logging.info("직책명 스타일 텍스트('고리') 부착 완료.")

            # 5) 고해상도 PDF 출력
            logging.info("고해상도 PDF 파일로 변환하여 저장을 시작합니다...")
            # 해상도 손실 방지를 위해 resolution 300 지정
            smoothed_img.save(
                OUTPUT_PDF_PATH, 
                "PDF", 
                resolution=300.0, 
                save_all=True
            )
            logging.info(f"성공적으로 고해상도 PDF가 생성되었습니다: {OUTPUT_PDF_PATH}")

    except MemoryError:
        logging.error("메모리 부족: 이미지가 너무 큽니다. 작업 환경의 가상 메모리를 확인하세요.")
    except Exception as e:
        logging.error(f"작업 중 예기치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()