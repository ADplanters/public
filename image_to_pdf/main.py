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

# 현재 스크립트가 위치한 절대 경로를 기반으로 작업 디렉토리 설정 (GitHub Repository 내 image_to_pdf 기준)
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

# -----------------------------------------------------------------------------
# 2. 리소스 자동 다운로드 (한글 폰트 및 시바견 이미지)
# -----------------------------------------------------------------------------
def ensure_korean_font():
    """나눔고딕 볼드 폰트 다운로드 (이름표 가독성을 위해 굵은 폰트 사용)"""
    if not FONT_PATH.exists():
        logging.info("로컬에 한글 폰트가 없습니다. 나눔고딕 볼드 폰트를 다운로드합니다...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        try:
            urllib.request.urlretrieve(font_url, FONT_PATH)
            logging.info("폰트 다운로드 완료.")
        except Exception as e:
            logging.error(f"폰트 다운로드 실패: {e}")
            raise

def ensure_shiba_image():
    """무료 API를 통해 귀여운 시바견 이미지를 자동으로 다운로드합니다."""
    if not SHIBA_IMAGE_PATH.exists():
        logging.info("시바견 이미지가 없습니다. 무료 API에서 귀여운 시바견 사진을 다운로드합니다...")
        try:
            # dog.ceo API를 사용하여 시바견(shiba) 랜덤 이미지 URL 가져오기
            req = urllib.request.Request(
                "https://dog.ceo/api/breed/shiba/images/random",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                img_url = data['message']
            
            # 이미지 다운로드
            urllib.request.urlretrieve(img_url, SHIBA_IMAGE_PATH)
            logging.info("시바견 이미지 다운로드 완료.")
        except Exception as e:
            logging.error(f"시바견 이미지 다운로드 실패: {e}")
            raise

# -----------------------------------------------------------------------------
# 3. 메인 이미지 처리 및 PDF 변환 로직
# -----------------------------------------------------------------------------
def main():
    logging.info("고해상도 이미지 처리 및 꼬리표 부착 작업을 시작합니다.")

    # 1) 입력 파일 존재 여부 확인
    if not INPUT_IMAGE_PATH.exists():
        logging.error(f"입력 이미지를 찾을 수 없습니다: {INPUT_IMAGE_PATH}")
        logging.info("파일명과 경로가 정확한지 확인해주세요.")
        return

    try:
        ensure_korean_font()
        ensure_shiba_image()
        
        # 폰트 객체 생성 (이미지 해상도에 비례하도록 넉넉한 크기 설정)
        font = ImageFont.truetype(str(FONT_PATH), size=45) 

        # 2) 원본 이미지 로드
        with Image.open(INPUT_IMAGE_PATH) as base_img:
            base_img = base_img.convert("RGB")
            bg_width, bg_height = base_img.size
            logging.info(f"원본 이미지 해상도: {bg_width} x {bg_height}")

            # 3) 픽셀 깨짐 및 부자연스러움 해결 (슈퍼 샘플링 안티앨리어싱 기법)
            logging.info("픽셀을 부드럽게 잇기 위해 슈퍼 샘플링(2배 확대 후 스무딩 및 축소)을 진행합니다...")
            # 2배로 부드럽게 늘린 후
            supersampled = base_img.resize((bg_width * 2, bg_height * 2), Image.Resampling.BICUBIC)
            # 노이즈를 다듬고
            supersampled = supersampled.filter(ImageFilter.SMOOTH_MORE)
            # 다시 고품질로 원본 크기로 축소 (계단 현상이 크게 완화됨)
            smoothed_img = supersampled.resize((bg_width, bg_height), Image.Resampling.LANCZOS)

            # 4) 시바견 이미지 로드 및 합성 준비
            with Image.open(SHIBA_IMAGE_PATH) as shiba_img:
                shiba_img = shiba_img.convert("RGBA")
                
                # 강아지 이미지를 원본 배경의 약 15% 크기로 설정
                target_width = int(bg_width * 0.15)
                # 시바견 이미지를 정사각형으로 리사이즈 (원형 마스크를 씌우기 위함)
                shiba_resized = shiba_img.resize((target_width, target_width), Image.Resampling.LANCZOS)
                
                # 배경이 있는 다운로드 이미지를 깔끔하게 원형으로 오려내기 위한 마스크 생성
                mask = Image.new("L", (target_width, target_width), 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, target_width, target_width), fill=255)
                
                # 우측 하단 배치 좌표 계산 (여백 80px)
                margin = 80
                paste_x = bg_width - target_width - margin
                paste_y = bg_height - target_width - margin
                
                # 부드러워진 메인 이미지 위에 시바견을 원형으로 붙여넣기
                smoothed_img.paste(shiba_resized, (paste_x, paste_y), mask=mask)
                logging.info("시바견 이미지 우측 하단에 합성 완료.")

                # 5) '고리' 꼬리표(이름표) 그리기
                draw = ImageDraw.Draw(smoothed_img)
                tag_text = "고리"
                
                # 텍스트 크기 계산
                bbox = draw.textbbox((0, 0), tag_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 이름표(둥근 사각형)의 크기 및 위치 계산 (시바견 바로 위 중앙)
                padding_x, padding_y = 30, 15
                tag_width = text_width + (padding_x * 2)
                tag_height = text_height + (padding_y * 2)
                
                tag_x0 = paste_x + (target_width - tag_width) // 2
                tag_y0 = paste_y - tag_height - 20 # 시바견 위 20px 띄움
                tag_x1 = tag_x0 + tag_width
                tag_y1 = tag_y0 + tag_height
                
                # 예쁜 노란색 꼬리표 바탕 그리기 (테두리 포함)
                draw.rounded_rectangle(
                    [tag_x0, tag_y0, tag_x1, tag_y1], 
                    radius=20, 
                    fill="#FFD700",       # 노란색
                    outline="#DAA520",    # 어두운 노란색 테두리
                    width=4
                )
                
                # 이름표 중앙에 '고리' 텍스트 쓰기
                text_x = tag_x0 + padding_x
                # 폰트에 따른 수직 정렬 미세조정
                text_y = tag_y0 + padding_y - 5 
                draw.text((text_x, text_y), tag_text, font=font, fill="#333333")
                logging.info("'고리' 이름표 부착 완료.")

            # 6) 고해상도 PDF 출력
            logging.info("고해상도 PDF 파일로 변환하여 저장을 시작합니다...")
            # resolution=300 옵션으로 인쇄 시에도 고해상도 유지
            smoothed_img.save(
                OUTPUT_PDF_PATH, 
                "PDF", 
                resolution=300.0, 
                save_all=True
            )
            logging.info(f"성공적으로 고해상도 PDF가 생성되었습니다: {OUTPUT_PDF_PATH}")

    except MemoryError:
        logging.error("메모리 부족 오류 발생: 이미지가 너무 큽니다. 가상 메모리를 늘리거나 시스템 상태를 확인하세요.")
    except PermissionError:
        logging.error(f"파일 쓰기 권한 없음: {OUTPUT_PDF_PATH} 파일이 열려있는지 확인하세요.")
    except Exception as e:
        logging.error(f"작업 중 예기치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()