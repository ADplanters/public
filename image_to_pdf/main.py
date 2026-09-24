"""
# Requirements
# pip install Pillow

# Directory Structure
# image_to_pdf/
#  ├── main.py
#  ├── image_56c6ff.jpg
#  └── 애드플랜터스-로고_PNG.png
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_font(size: int, is_bold: bool = False) -> ImageFont.FreeTypeFont:
    """시스템 기본 폰트 중 한글을 지원하는 폰트를 안전하게 불러옵니다."""
    font_names = ["malgun.ttf", "malgunbd.ttf", "AppleGothic.ttf", "NanumGothic.ttf"]
    for font_name in font_names:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    logging.warning("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다. 한글이 깨질 수 있습니다.")
    return ImageFont.load_default()

def draw_tag_with_arrow(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.FreeTypeFont):
    """얼굴을 가리지 않도록 머리 위(y)에 꼬리표와 화살표(삼각형)를 그립니다."""
    try:
        # 텍스트 크기 계산
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        pad_x, pad_y = 15, 10
        
        # 꼬리표 본체 (둥근 사각형) 좌표
        rect_left = x - (tw / 2) - pad_x
        rect_top = y - th - pad_y * 2
        rect_right = x + (tw / 2) + pad_x
        rect_bottom = y
        
        # 화살표(역삼각형) 좌표
        arrow_width = 12
        arrow_height = 10
        point1 = (x - arrow_width / 2, rect_bottom)
        point2 = (x + arrow_width / 2, rect_bottom)
        point3 = (x, rect_bottom + arrow_height)
        
        # 그리기 (배경: 반투명 검은색, 테두리: 흰색)
        bg_color = (30, 30, 30, 200)
        draw.polygon([point1, point2, point3], fill=bg_color)
        draw.rounded_rectangle([rect_left, rect_top, rect_right, rect_bottom], radius=10, fill=bg_color, outline=(255, 255, 255, 255), width=2)
        
        # 흰색 직책 텍스트
        text_x = x - (tw / 2)
        text_y = rect_top + pad_y - 2
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
    except Exception as e:
        logging.error(f"꼬리표 렌더링 오류 ({text}): {e}")

def process_image():
    base_dir = Path(__file__).parent.resolve()
    input_img_path = base_dir / "image_56c6ff.jpg"
    logo_path = base_dir / "애드플랜터스-로고_PNG.png"
    output_pdf_path = base_dir / "output_high_res.pdf"

    if not input_img_path.exists():
        logging.error(f"입력 이미지를 찾을 수 없습니다: {input_img_path}")
        return

    logging.info("이미지 편집 및 합성 작업을 시작합니다...")

    try:
        with Image.open(input_img_path) as img:
            img = img.convert("RGBA")
            W, H = img.size

            # ---------------------------------------------------------
            # 1. 인물 위치 교체 (카메라 앞 여자 <-> 서있는 남자)
            # ---------------------------------------------------------
            # 좌측 카메라 앞 인물(여)과 우측 서있는 인물(남)의 영역 크롭
            box_woman_cam = (int(W * 0.02), int(H * 0.52), int(W * 0.20), int(H * 0.95))
            box_man_stand = (int(W * 0.61), int(H * 0.52), int(W * 0.77), int(H * 0.95))
            
            region_woman = img.crop(box_woman_cam)
            region_man = img.crop(box_man_stand)
            
            # 크기 상호 조정 및 붙여넣기 (스왑)
            region_woman_resized = region_woman.resize((box_man_stand[2]-box_man_stand[0], box_man_stand[3]-box_man_stand[1]), Image.Resampling.LANCZOS)
            region_man_resized = region_man.resize((box_woman_cam[2]-box_woman_cam[0], box_woman_cam[3]-box_woman_cam[1]), Image.Resampling.LANCZOS)
            
            img.paste(region_man_resized, box_woman_cam)
            img.paste(region_woman_resized, box_man_stand)
            logging.info("카메라 앞 인물과 남성의 위치 교체가 완료되었습니다.")

            # ---------------------------------------------------------
            # 2. 하늘 색상 변경 (보라색 -> 파란색)
            # ---------------------------------------------------------
            # 파란색 오버레이 생성 후 하늘 영역(상단 45%)에만 그라데이션 적용
            blue_overlay = Image.new('RGBA', img.size, (0, 70, 180, 100))
            mask = Image.new('L', img.size)
            draw_mask = ImageDraw.Draw(mask)
            for y in range(int(H * 0.45)):
                alpha = int(255 * (1 - y / (H * 0.45)))
                draw_mask.line([(0, y), (W, y)], fill=alpha)
            img.paste(blue_overlay, (0, 0), mask)
            
            # ---------------------------------------------------------
            # 3. 메인 텍스트 변경 (즐거운 한가위 보내세요 -> 해피메리추석)
            # ---------------------------------------------------------
            draw = ImageDraw.Draw(img, "RGBA")
            # 기존 텍스트 덮기 (하늘색과 유사한 다크블루)
            text_bg_box = [W * 0.15, H * 0.35, W * 0.85, H * 0.45]
            # 블러 느낌을 내기 위해 여러 번 겹쳐 칠함
            draw.rectangle(text_bg_box, fill=(20, 25, 60, 255)) 
            
            # 새 텍스트 작성
            title_font = get_font(int(W * 0.08), is_bold=True)
            text_str = "해피메리추석"
            # 텍스트 중앙 정렬을 위한 계산
            t_bbox = draw.textbbox((0, 0), text_str, font=title_font)
            t_w = t_bbox[2] - t_bbox[0]
            draw.text((W/2 - t_w/2, H * 0.36), text_str, font=title_font, fill=(255, 255, 255, 255))

            # ---------------------------------------------------------
            # 4. 직책 꼬리표 화살표 배치 (얼굴을 가리지 않게 좌표 계산)
            # ---------------------------------------------------------
            # 폰트 사이즈 설정 (해상도 비례)
            tag_font = get_font(max(int(W * 0.025), 18))
            
            # 구성: 남자(웹기획자, 촬영감독, 마케터), 여자(셀럽A, 셀럽B)
            # y_ratio를 인물의 머리보다 높게(-0.08) 설정하여 얼굴을 가리지 않음
            positions = [
                ("촬영감독", 0.11, 0.50),  # 스왑된 남자 (카메라 앞)
                ("셀럽A", 0.33, 0.53),     # 태블릿 든 여자
                ("CEO", 0.55, 0.58),       # 중앙 가리키는 남자
                ("셀럽B", 0.69, 0.50),     # 스왑된 여자 (서 있는 위치)
                ("마케터", 0.90, 0.68),    # 노트북 하는 남자 (웹기획자/마케터)
                ("웹기획자", 0.79, 0.56)   # 우측 서포트 남성(또는 남은 역할 할당) - 사용자 요청 인원에 맞춰 배치
            ]

            for role, x_ratio, y_ratio in positions:
                draw_tag_with_arrow(draw, W * x_ratio, H * y_ratio, role, tag_font)

            # ---------------------------------------------------------
            # 5. 로고 투명 PNG 교체 반영
            # ---------------------------------------------------------
            if logo_path.exists():
                # 기존 로고 위치 배경색 덮기
                logo_box = [W * 0.30, H * 0.93, W * 0.70, H * 0.99]
                draw.rectangle(logo_box, fill=(15, 12, 25, 255))
                
                # 투명 PNG 로고 붙여넣기
                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    # 로고 리사이징
                    lw_max = int(logo_box[2] - logo_box[0])
                    lh_max = int(logo_box[3] - logo_box[1])
                    logo.thumbnail((lw_max, lh_max), Image.Resampling.LANCZOS)
                    
                    # 중앙 정렬
                    paste_x = int(logo_box[0] + (lw_max - logo.width) / 2)
                    paste_y = int(logo_box[1] + (lh_max - logo.height) / 2)
                    
                    # 흰색 배경 없이 투명(Alpha) 값을 살려서 합성
                    img.paste(logo, (paste_x, paste_y), mask=logo)
            else:
                logging.warning("새로운 로고 이미지가 없어 로고 교체를 건너뜁니다.")

            # ---------------------------------------------------------
            # 6. 고해상도 PDF 출력
            # ---------------------------------------------------------
            logging.info("고해상도 PDF로 변환 중입니다...")
            rgb_img = img.convert("RGB")
            # dpi 300으로 설정하여 디테일과 화질을 보존
            rgb_img.save(output_pdf_path, "PDF", resolution=300.0, save_all=True)
            logging.info(f"작업 완료! PDF 파일 생성됨: {output_pdf_path}")

    except Exception as e:
        logging.error(f"이미지 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    process_image()