# =============================================================================
# [실행 전 필요 패키지 설치 안내]
# 터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치해 주세요.
# pip install Pillow reportlab requests
# =============================================================================

import os
import logging
import urllib.request
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# 1. 로깅 및 환경 설정
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 현재 스크립트가 위치한 절대 경로를 기반으로 작업 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent

# 파일 경로 설정
INPUT_IMAGE_NAME = "애드플랜터스_추석_인사_카드_highres_page-0001.jpg"
OUTPUT_IMAGE_NAME = "temp_processed_image.png" # PDF 변환용 임시 저장 이미지
OUTPUT_PDF_NAME = "애드플랜터스_추석_인사_카드_고리수정.pdf"
FONT_NAME = "NanumBrush.ttf"

INPUT_IMAGE_PATH = BASE_DIR / INPUT_IMAGE_NAME
OUTPUT_IMAGE_PATH = BASE_DIR / OUTPUT_IMAGE_NAME
OUTPUT_PDF_PATH = BASE_DIR / OUTPUT_PDF_NAME
FONT_PATH = BASE_DIR / FONT_NAME

# 이미지 해상도 설정 (고해상도 출력용 300 DPI)
DPI = 300

# -----------------------------------------------------------------------------
# 2. 필수 리소스 다운로드 유틸리티
# -----------------------------------------------------------------------------
def ensure_resources():
    """한글 필기체 폰트(나눔손글씨 붓)가 없으면 자동으로 다운로드합니다."""
    if not FONT_PATH.exists():
        logging.info("필기체 폰트가 없습니다. 나눔손글씨 붓 폰트를 다운로드합니다...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumbrushscript/NanumBrushScript-Regular.ttf"
        try:
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
            logging.info("폰트 다운로드 완료.")
        except Exception as e:
            logging.error(f"폰트 다운로드 실패: {e}")
            raise

# -----------------------------------------------------------------------------
# 3. 메인 이미지 처리 로직
# -----------------------------------------------------------------------------
def process_image():
    logging.info(f"작업을 시작합니다. 입력 파일: {INPUT_IMAGE_NAME}")

    try:
        ensure_resources()
    except Exception:
        return False

    if not INPUT_IMAGE_PATH.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다: {INPUT_IMAGE_PATH}")
        return False

    try:
        # 1) 원본 이미지 로드
        with Image.open(INPUT_IMAGE_PATH) as img:
            working_img = img.convert("RGB")
            
            # 2) 화질 개선 (계단 현상 완화)
            logging.info("이미지 픽셀 평활화(Smoothening) 작업 진행 중...")
            smoothed_img = working_img.filter(ImageFilter.SMOOTH_MORE)
            
            draw = ImageDraw.Draw(smoothed_img)
            width, height = smoothed_img.size
            
            # 3) 스타일 설정
            font_size = int(width * 0.03) # 이미지 너비의 3% 크기
            font = ImageFont.truetype(str(FONT_PATH), font_size)
            
            text_content = "고리"
            text_color = (255, 255, 255) # 흰색
            
            # 강아지 위치 추정 (정확한 위치는 이 변수들의 값을 수정하여 맞출 수 있습니다)
            dog_center_x = int(width * 0.75) 
            dog_top_y = int(height * 0.65)   
            
            # 텍스트 크기 계산
            text_bbox = draw.textbbox((0, 0), text_content, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            text_x = dog_center_x - (text_w / 2)
            text_y = dog_top_y - text_h - int(height * 0.05) 

            # 4) 돼지꼬리표 그리기
            line_width = max(3, int(width * 0.002)) 

            # 둥근 원호 (돼지꼬리 느낌의 곡선)
            arc_coords = [
                (dog_center_x - text_w, text_y + text_h),
                (dog_center_x + text_w, dog_top_y)
            ]
            draw.arc(arc_coords, start=150, end=390, fill=text_color, width=line_width)
            
            # 지시선 끝점 (강아지 머리 방향 원형 포인트)
            dot_radius = line_width * 2
            draw.ellipse(
                (dog_center_x - dot_radius, dog_top_y - dot_radius, 
                 dog_center_x + dot_radius, dog_top_y + dot_radius),
                fill=text_color
            )

            # 5) 필기체 텍스트 그리기
            draw.text((text_x, text_y), text_content, font=font, fill=text_color)
            logging.info("강아지 위에 '고리' 돼지꼬리표 및 텍스트 추가 완료.")

            # 6) 임시 파일로 저장 (고해상도 PNG)
            smoothed_img.save(OUTPUT_IMAGE_PATH, format="PNG", dpi=(DPI, DPI))
            logging.info("임시 고해상도 이미지 저장 완료.")
            
        return True

    except MemoryError:
        logging.error("메모리가 부족합니다. 이미지가 너무 크거나 시스템 리소스가 부족합니다.")
        return False
    except Exception as e:
        logging.error(f"이미지 처리 중 오류 발생: {e}")
        return False

# -----------------------------------------------------------------------------
# 4. PDF 변환 로직
# -----------------------------------------------------------------------------
def convert_to_pdf():
    logging.info("고해상도 PDF 변환을 시작합니다...")
    
    if not OUTPUT_IMAGE_PATH.exists():
        logging.error("임시 저장된 이미지가 없어 PDF 변환을 취소합니다.")
        return

    try:
        with Image.open(OUTPUT_IMAGE_PATH) as img:
            img_width, img_height = img.size

        # 물리적 포인트 크기 계산 (1인치 = 72포인트)
        page_width = (img_width / DPI) * 72
        page_height = (img_height / DPI) * 72

        # ReportLab 캔버스 생성 및 이미지 삽입
        c = canvas.Canvas(str(OUTPUT_PDF_PATH), pagesize=(page_width, page_height))
        c.drawImage(str(OUTPUT_IMAGE_PATH), 0, 0, width=page_width, height=page_height, mask='auto')
        c.showPage()
        c.save()
        
        logging.info(f"성공적으로 고해상도 PDF가 생성되었습니다: {OUTPUT_PDF_PATH}")

    except Exception as e:
        logging.error(f"PDF 변환 중 오류 발생: {e}")
    finally:
        # 리소스 정리 (임시 파일 삭제)
        if OUTPUT_IMAGE_PATH.exists():
            try:
                os.remove(OUTPUT_IMAGE_PATH)
                logging.info("임시 이미지 파일 정리 완료.")
            except Exception as cleanup_err:
                logging.warning(f"임시 파일 삭제 실패: {cleanup_err}")

# -----------------------------------------------------------------------------
# 메인 실행부
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        if process_image():
            convert_to_pdf()
    except KeyboardInterrupt:
        logging.warning("\n사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        logging.critical(f"심각한 오류 발생: {e}")