# =============================================================================
# [실행 전 필수 패키지 설치 안내]
# 현재 활성화된 가상환경(.venv) 터미널에서 아래 명령어를 반드시 실행해 주세요.
# pip install Pillow PyMuPDF
# =============================================================================

import os
import sys
import logging
import urllib.request
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. 의존성 패키지 동적 로드 및 예외 처리
# -----------------------------------------------------------------------------
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("\n[오류] Pillow 라이브러리가 설치되지 않았습니다.")
    print("터미널에 아래 명령어를 입력하여 설치해 주세요:\n> pip install Pillow\n")
    sys.exit(1)

try:
    import fitz  # PyMuPDF 라이브러리 (PDF 읽기 및 고해상도 렌더링용)
except ImportError:
    print("\n[오류] PyMuPDF 라이브러리가 설치되지 않았습니다. ('fitz' 모듈 없음)")
    print("터미널에 아래 명령어를 입력하여 설치해 주세요:\n> pip install PyMuPDF\n")
    sys.exit(1)

# -----------------------------------------------------------------------------
# 2. 로깅 및 환경 설정
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 현재 스크립트가 위치한 절대 경로 설정 (GitHub 레포지토리 image_to_pdf 기준)
BASE_DIR = Path(__file__).resolve().parent

# 파일 경로 설정
INPUT_FILE_BASE = "애드플랜터스_추석_인사_카드_고리수정"
OUTPUT_PDF_NAME = f"{INPUT_FILE_BASE}_최종출력.pdf"
FONT_NAME = "NanumGothicBold.ttf"

OUTPUT_PDF_PATH = BASE_DIR / OUTPUT_PDF_NAME
FONT_PATH = BASE_DIR / FONT_NAME

# =============================================================================
# [직책명표 스타일 커스텀 설정] 
# 원본 이미지의 직책명표 디자인(흰색 상자, 둥근 모서리 등)
# =============================================================================
TAG_BG_COLOR = "#FFFFFF"       # 직책명표 배경색 (흰색)
TAG_TEXT_COLOR = "#333333"     # 직책명표 글자색 (진한 회색/검정)
TAG_BORDER_COLOR = "#CCCCCC"   # 직책명표 테두리색
TAG_BORDER_WIDTH = 6           # 테두리 두께 (초고해상도이므로 두껍게 설정)
TAG_RADIUS = 25                # 상자 모서리 둥근 정도
# =============================================================================

# -----------------------------------------------------------------------------
# 3. 리소스 다운로드 유틸리티 (폰트)
# -----------------------------------------------------------------------------
def ensure_font():
    """직책명 텍스트를 위한 무료 한글 폰트(나눔고딕 볼드) 자동 다운로드"""
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
# 4. 메인 처리 로직 (고해상도 렌더링 -> 편집 -> PDF 출력)
# -----------------------------------------------------------------------------
def process_document():
    logging.info(f"작업을 시작합니다. 대상 파일: {INPUT_FILE_BASE}")

    try:
        ensure_font()
    except Exception:
        return

    # 입력 파일 탐색 (.pdf, .jpg, .png 모두 호환되도록 탐색)
    input_pdf_path = BASE_DIR / f"{INPUT_FILE_BASE}.pdf"
    input_img_path_jpg = BASE_DIR / f"{INPUT_FILE_BASE}.jpg"
    input_img_path_png = BASE_DIR / f"{INPUT_FILE_BASE}.png"

    target_path = None
    file_type = None

    if input_pdf_path.exists():
        target_path = input_pdf_path
        file_type = "pdf"
    elif input_img_path_jpg.exists():
        target_path = input_img_path_jpg
        file_type = "img"
    elif input_img_path_png.exists():
        target_path = input_img_path_png
        file_type = "img"
    else:
        logging.error(f"입력 파일을 찾을 수 없습니다: {INPUT_FILE_BASE}.(pdf/jpg/png)")
        logging.info("main.py와 같은 폴더에 파일이 존재하는지, 파일명이 정확한지 확인해 주세요.")
        return

    working_img = None
    doc = None

    try:
        if file_type == "pdf":
            logging.info(f"PDF 문서를 감지했습니다. 초고해상도로 렌더링을 시작합니다: {target_path.name}")
            doc = fitz.open(target_path)
            page = doc[0]  # 첫 번째 페이지 기준
            
            # 해상도를 극대화하기 위해 확대 비율 설정 (초고해상도 인쇄용)
            zoom = 4.0 
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PyMuPDF 픽셀 데이터를 Pillow 이미지 객체로 변환
            working_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        else:
            logging.info(f"이미지 문서를 감지했습니다: {target_path.name}")
            img_open = Image.open(target_path)
            working_img = img_open.convert("RGB")
            img_open.close()

        width, height = working_img.size
        logging.info(f"이미지 준비 완료 (작업 해상도: {width} x {height})")

        # -------------------------------------------------------------------------
        # 이미지 편집 (직책명표 그리기)
        # -------------------------------------------------------------------------
        draw = ImageDraw.Draw(working_img)
        
        # 해상도에 비례하여 폰트 크기 동적 계산 (화면 너비의 약 2.5%)
        font_size = int(width * 0.025)
        if font_size < 20: font_size = 20
        font = ImageFont.truetype(str(FONT_PATH), size=font_size)
        
        name_text = "고리"
        
        # 텍스트가 차지하는 물리적 크기 계산
        bbox = draw.textbbox((0, 0), name_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 직책명표(상자) 내부 여백 설정
        padding_x = int(font_size * 0.8)
        padding_y = int(font_size * 0.4)
        box_width = text_width + (padding_x * 2)
        box_height = text_height + (padding_y * 2)
        
        # [위치 조정 안내] 강아지 위치 (현재 우측 15%, 하단 20% 지점으로 추정)
        # 🌟 실제 강아지 위치와 맞지 않으면 아래 0.85와 0.80 비율을 약간씩 수정해 주세요.
        dog_x = int(width * 0.85)
        dog_y = int(height * 0.80)
        
        # 상자 좌표 계산 (강아지 머리 위 중앙 정렬)
        box_x0 = dog_x - (box_width // 2)
        box_y0 = dog_y - box_height
        box_x1 = box_x0 + box_width
        box_y1 = box_y0 + box_height
        
        # 1) 직책명표 배경 상자 그리기
        draw.rounded_rectangle(
            [box_x0, box_y0, box_x1, box_y1], 
            radius=TAG_RADIUS, 
            fill=TAG_BG_COLOR,
            outline=TAG_BORDER_COLOR,
            width=TAG_BORDER_WIDTH
        )
        
        # 2) 직책명표 텍스트 쓰기
        text_x = box_x0 + padding_x
        text_y = box_y0 + padding_y - int(font_size * 0.1)  # 시각적 수직 중앙 정렬 보정
        draw.text((text_x, text_y), name_text, font=font, fill=TAG_TEXT_COLOR)
        
        logging.info("강아지 위에 '고리' 직책명표 합성 완료.")

        # -------------------------------------------------------------------------
        # 고해상도 PDF 저장
        # -------------------------------------------------------------------------
        logging.info("최대 해상도 PDF 파일로 저장을 시작합니다...")
        
        # 해상도 손실이 없도록 DPI(600)와 품질(100)을 최고치로 강제 설정
        working_img.save(
            OUTPUT_PDF_PATH, 
            "PDF", 
            resolution=600.0, 
            quality=100, 
            save_all=True
        )
        logging.info(f"★성공★ 초고해상도 PDF 문서가 생성되었습니다: {OUTPUT_PDF_PATH}")

    except MemoryError:
        logging.error("메모리 부족: PDF 렌더링 해상도가 너무 높습니다. 시스템 리소스를 확인하세요.")
    except PermissionError:
        logging.error(f"권한 오류: '{OUTPUT_PDF_NAME}' 파일이 뷰어 등에 열려있습니다. 닫은 후 다시 실행해 주세요.")
    except Exception as e:
        logging.error(f"작업 중 예기치 못한 오류 발생: {e}")
    finally:
        # 리소스 메모리 반환
        if working_img:
            working_img.close()
        if doc:
            doc.close()

if __name__ == "__main__":
    try:
        process_document()
    except KeyboardInterrupt:
        logging.warning("\n사용자에 의해 작업이 중단되었습니다.")
    except Exception as e:
        logging.critical(f"심각한 오류 발생: {e}")