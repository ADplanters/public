"""
# Requirements
# pip install Pillow

# Directory Structure (GitHub Public Repo)
# image_to_pdf/
#  ├── main.py
#  ├── image_56c6ff.jpg
#  ├── 애드플랜터스-로고_PNG.png
#  └── (옵션) cursive.ttf (원하는 흰색 필기체 폰트 파일)
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 로깅 설정 (터미널 진행률 및 에러 확인용)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_font(base_dir: Path, size: int) -> ImageFont.FreeTypeFont:
    """필기체 폰트를 불러옵니다. 없으면 시스템 기본 폰트를 사용합니다."""
    # 폰트 파일이 있다면 사용 (예: cursive.ttf)
    font_path = base_dir / "cursive.ttf"
    try:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        
        # 윈도우/맥 기본 폰트 폴백 (Fallback) 처리
        if os.name == 'nt':
            return ImageFont.truetype("malgun.ttf", size)
        else:
            return ImageFont.truetype("AppleGothic.ttf", size)
    except IOError:
        logging.warning("폰트를 찾을 수 없어 기본 폰트를 사용합니다. (영문만 지원될 수 있음)")
        return ImageFont.load_default()

def draw_tag(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.FreeTypeFont):
    """지정된 좌표 중심에 반투명 꼬리표와 흰색 텍스트를 그립니다."""
    try:
        # 텍스트 크기 계산
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        # 꼬리표 배경 좌표 계산 (중앙 정렬)
        pad_x, pad_y = 12, 8
        left = x - (tw / 2) - pad_x
        top = y - (th / 2) - pad_y
        right = x + (tw / 2) + pad_x
        bottom = y + (th / 2) + pad_y
        
        # 반투명 검은색 꼬리표 배경
        draw.rounded_rectangle([left, top, right, bottom], radius=8, fill=(0, 0, 0, 160))
        # 흰색 필기체 텍스트
        draw.text((x - (tw / 2), y - (th / 2) - 2), text, font=font, fill=(255, 255, 255, 255))
    except Exception as e:
        logging.error(f"'{text}' 꼬리표 렌더링 중 오류 발생: {e}")

def process_image_to_pdf():
    base_dir = Path(__file__).parent.resolve()
    input_img_path = base_dir / "image_56c6ff.jpg"
    logo_path = base_dir / "애드플랜터스-로고_PNG.png"
    output_pdf_path = base_dir / "output_high_res.pdf"

    if not input_img_path.exists():
        logging.error(f"입력 이미지를 찾을 수 없습니다: {input_img_path}")
        return

    logging.info("이미지 처리를 시작합니다...")

    try:
        # 1. 고해상도 처리를 위해 원본 이미지 로드 (메모리 누수 방지를 위한 with 구문)
        with Image.open(input_img_path) as img:
            # 투명도가 포함된 작업을 위해 RGBA로 변환
            img = img.convert("RGBA")
            draw = ImageDraw.Draw(img, "RGBA")
            W, H = img.size
            
            # 해상도 비례 폰트 사이즈 (이미지 가로 폭의 약 2.5%)
            font_size = max(int(W * 0.025), 16) 
            font = get_font(base_dir, font_size)

            # 2. 인원 역할 및 위치 배치 (x_ratio, y_ratio)
            # 이미지 비율을 기준으로 머리 위쪽에 꼬리표가 달리도록 설정
            positions = [
                ("웹기획자", 0.15, 0.72),  # 좌측 앉아있는 인물
                ("셀럽A", 0.33, 0.58),    # 좌측 서있는 인물
                ("CEO", 0.55, 0.65),      # 중앙 앉아있는 인물 (가리키는 남성)
                ("촬영감독", 0.68, 0.55), # 우측 서있는 인물 (카메라)
                ("셀럽B", 0.82, 0.58),    # 우측 서있는 인물 (노트)
                ("마케터", 0.90, 0.75),   # 우측 앉아있는 인물 (노트북)
            ]

            for role, x_ratio, y_ratio in positions:
                draw_tag(draw, W * x_ratio, H * y_ratio, role, font)
                
            # 3. 하단 기존 로고 삭제(배경색 덮기) 및 새 로고 얹기
            if logo_path.exists():
                # 기존 "Noah Universe Company" 로고 위치 추정 박스
                logo_box = [W * 0.35, H * 0.93, W * 0.65, H * 0.99]
                
                # 배경색과 비슷한 어두운 색으로 기존 로고 가리기
                draw.rectangle(logo_box, fill=(20, 15, 30, 255))
                
                # 새 로고 로드 및 리사이징 (LANCZOS 고품질 리샘플링)
                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    lw_max = int(logo_box[2] - logo_box[0])
                    lh_max = int(logo_box[3] - logo_box[1])
                    
                    logo.thumbnail((lw_max, lh_max), Image.Resampling.LANCZOS)
                    
                    # 로고 중앙 정렬 좌표 계산
                    paste_x = int(logo_box[0] + (lw_max - logo.width) / 2)
                    paste_y = int(logo_box[1] + (lh_max - logo.height) / 2)
                    
                    # 로고 내 검은 글씨 가시성을 위해 반투명 흰색 배경 깔기 (선택적)
                    draw.rounded_rectangle(
                        [paste_x - 10, paste_y - 5, paste_x + logo.width + 10, paste_y + logo.height + 5], 
                        radius=5, fill=(255, 255, 255, 220)
                    )
                    
                    # 로고 합성 (alpha 채널을 마스크로 사용)
                    img.paste(logo, (paste_x, paste_y), logo)
            else:
                logging.warning("새로운 로고 이미지를 찾을 수 없어 로고 교체를 건너뜁니다.")

            # 4. 최종 결과물을 고해상도 PDF로 저장
            logging.info("고해상도 PDF 생성을 진행 중입니다...")
            rgb_img = img.convert("RGB")
            # dpi=300, resolution 옵션으로 고해상도 보장
            rgb_img.save(output_pdf_path, "PDF", resolution=300.0, save_all=True)
            
            logging.info(f"성공적으로 완료되었습니다. PDF 저장 경로: {output_pdf_path}")

    except Exception as e:
        logging.error(f"이미지 처리 중 치명적인 오류 발생: {e}")

if __name__ == "__main__":
    process_image_to_pdf()