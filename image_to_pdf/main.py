# =============================================================================
# [실행 전 필요 패키지 설치 안내]
# 터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치해 주세요.
# pip install Pillow reportlab requests
# =============================================================================

import os
import logging
import urllib.request
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.units import Inch

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

# 파일 경로 설정 (절대 경로 기준)
INPUT_IMAGE_NAME = "애드플랜터스_추석_인사_카드_highres_page-0001.jpg"
OUTPUT_IMAGE_NAME = "temp_processed_image.png" # PDF 변환용 임시 저장 이미지
OUTPUT_PDF_NAME = "애드플랜터스_추석_인사_카드_고리수정.pdf"
# 폰트: 필기체 느낌을 위해 네이버 나눔손글씨 붓 폰트 사용
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
    """
    한글 필기체 폰트가 작업 폴더에 없으면 자동으로 다운로드합니다.
    """
    if not FONT_PATH.exists():
        logging.info("필기체 폰트가 없습니다. 나눔손글씨 붓 폰트를 다운로드합니다...")
        # 네이버 나눔글꼴 다운로드 링크
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumbrushscript/NanumBrushScript-Regular.ttf"
        try:
            req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
            logging.info("폰트 다운로드 완료.")
        except Exception as e:
            logging.error(f"폰트 다운로드 실패 (인터넷 연결 확인 필요): {e}")
            raise

# -----------------------------------------------------------------------------
# 3. 메인 이미지 처리 로직
# -----------------------------------------------------------------------------
def process_image():
    logging.info(f"작업을 시작합니다. 입력 파일: {INPUT_IMAGE_NAME}")

    # 리소스 확인
    ensure_resources()

    if not INPUT_IMAGE_PATH.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다: {INPUT_IMAGE_PATH}")
        logging.error("파일명이 정확한지, main.py와 같은 폴더에 있는지 확인해 주세요.")
        return False

    try:
        # 1) 원본 이미지 로드 (고해상도 유지)
        with Image.open(INPUT_IMAGE_PATH) as img:
            logging.info(f"원본 이미지 로드 완료 ({img.size[0]}x{img.size[1]})")
            
            # CMYK 등이 섞여있을 수 있으므로 안전하게 RGB로 변환하여 작업
            working_img = img.convert("RGB")
            
            # 2) 화질 개선: 부자연스럽거나 끊긴 픽셀을 부드럽게 연결 (SMOOTH_MORE 필터 적용)
            # 이는 고해상도 출력 시 계단 현상을 줄여줍니다.
            logging.info("이미지 픽셀 평활화(Smoothening) 작업을 수행 중...")
            smoothed_img = working_img.filter(ImageFilter.SMOOTH_MORE)
            
            # 3) 편집용 Draw 객체 생성
            draw = ImageDraw.Draw(smoothed_img)
            width, height = smoothed_img.size
            
            # 4) 스타일 및 위치 설정
            # 폰트 크기: 고해상도(약 5000px 너비 가정)에 맞춰 크게 설정
            font_size = int(width * 0.03) # 이미지 너비의 3% 크기
            font = ImageFont.truetype(str(FONT_PATH), font_size)
            
            # 텍스트 내용 및 색상 (흰색)
            text_content = "고리"
            text_color = (255, 255, 255) # White
            
            # 강아지 위치 (원본 이미지에서 강아지가 있는 대략적인 우측 하단 영역)
            # 실제 강아지의 정확한 좌표(px)로 튜닝 필요. 아래는 예시 비율 기반 위치입니다.
            # 사용자가 제공한 원본 이미지를 볼 수 없으므로, 중앙 하단으로 가정한 후 튜닝 가이드 제공
            dog_center_x = int(width * 0.75) # 우측에서 25% 지점
            dog_top_y = int(height * 0.65)   # 위에서 65% 지점 (강아지 머리 위)

            # 5) '돼지꼬리표' (말풍선/지시선) 그리기
            # 직책명 스타일처럼 구현하기 위해 흰색 선으로 강아지를 지칭하는 부드러운 곡선/원을 그립니다.
            
            # 텍스트 크기 계산하여 중앙 정렬
            text_bbox = draw.textbbox((0, 0), text_content, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            text_x = dog_center_x - (text_w / 2)
            text_y = dog_top_y - text_h - int(height * 0.05) # 강아지 머리에서 위로 5% 띄움

            # 돼지꼬리 스타일 지시선 (텍스트 아래에서 강아지 쪽으로 둥글게)
            # 고해상도이므로 선 두께(width)를 두껍게 설정
            line_width = int(width * 0.002) 
            if line_width < 3: line_width = 3

            # 둥근 원호 그리기 (돼지꼬리 느낌)
            arc_coords = [
                (dog_center_x - text_w, text_y + text_h), # 시작점
                (dog_center_x + text_w, dog_top_y)        # 끝점
            ]
            draw.arc(arc_coords, start=150, end=390, fill=text_color, width=line_width)
            
            # 화살표 촉 또는 작은 원 추가 (강아지를 정확히 가리킴)
            dot_radius = line_width * 2
            draw.ellipse(
                (dog_center_x - dot_radius, dog_top_y - dot_radius, 
                 dog_center_x + dot_radius, dog_top_y + dot_radius),
                fill=text_color
            )

            # 6) 필기체 텍스트 '고리' 그리기
            draw.text((text_x, text_y), text_content, font=font, fill=text_color)
            logging.info("강아지 위에 '고리' 돼지꼬리표 및 필기체 텍스트 추가 완료.")

            # 7) 고해상도 유지하여 임시 저장 (DPI 설정 포함, 손실 압축 없는 PNG 사용)
            smoothed_img.save(OUTPUT_IMAGE_PATH, format="PNG", dpi=(DPI, DPI))
            logging.info(f"편집된 고해상도 이미지 임시 저장 완료: {OUTPUT_IMAGE_NAME}")
            
        return True

    except Exception as e:
        logging.error(f"이미지 처리 중 오류 발생: {e}")
        return False

# -----------------------------------------------------------------------------
# 4. PDF 변환 로직 (고해상도 출력용)
# -----------------------------------------------------------------------------
def convert_to_pdf():
    logging.info("최종 PDF 변환 작업을 시작합니다...")
    
    if not OUTPUT_IMAGE_PATH.exists():
        logging.error("임시 저장된 이미지를 찾을 수 없어 PDF 변환을 진행할 수 없습니다.")
        return

    try:
        # 처리된 이미지의 실제 픽셀 크기 확인
        with Image.open(OUTPUT_IMAGE_PATH) as img:
            img_width, img_height = img.size

        # DPI 기반으로 물리적 크기 계산 (인치)
        phys_width_inch = img_width / DPI
        phys_height_inch = img_height / DPI
        
        # ReportLab은 포인트를 기본 단위로 사용 (1인치 = 72포인트)
        page_width = phys_width_inch * 72
        page_height = phys_height_inch * 72

        # 1) PDF 캔버스 생성 (이미지 크기에 맞춘 커스텀 페이지 크기)
        c = canvas.Canvas(str(OUTPUT_PDF_PATH), pagesize=(page_width, page_height))
        
        # 2) 고해상도 이미지를 PDF 페이지에 그리기
        # 위치 (0,0)에서 시작하여 페이지 전체 크기로 꽉 차게 그림
        c.drawImage(str(OUTPUT_IMAGE_PATH), 0, 0, width=page_width, height=page_height, mask='auto')
        
        # 3) PDF 저장
        c.showPage()
        c.save()
        
        logging.info(f"★성공★ 고해상도 PDF 출력 완료: {OUTPUT_PDF_PATH}")
        
        # 4) 임시 파일 정리
        if OUTPUT_IMAGE_PATH.exists():
            os.remove(OUTPUT_IMAGE_PATH)
            logging.info("임시 이미지 파일 삭제 완료.")

    except Exception as e:
        logging.error(f"PDF 변환 중 오류 발생: {e}")

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