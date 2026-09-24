"""
image_to_pdf/main.py

Requirements:
Pillow
"""

import os
import glob
import logging
import urllib.request
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_input_image_path(base_dir: Path) -> Path:
    """
    폴더 내 원본 이미지를 자동으로 탐색합니다.
    (20260924_183847.jpg, image_56c6ff.jpg 등 사용자가 새로 올린 이미지 파일명을 우선 자동 감지)
    """
    priority_names = ["20260924_183847.jpg", "image_56c6ff.jpg"]
    for name in priority_names:
        p = base_dir / name
        if p.exists():
            return p
            
    # 우선 지정 이름이 없으면 폴더 내 첫 번째 jpg/png 이미지 탐색 (로고 제외)
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        for file_path in base_dir.glob(ext):
            if "로고" not in file_path.name and "output" not in file_path.name:
                return file_path
                
    return base_dir / "20260924_183847.jpg"

def ensure_cursive_font(base_dir: Path) -> ImageFont.FreeTypeFont:
    """나눔펜스크립트 필기체 폰트를 자동 확보하여 로드합니다."""
    font_path = base_dir / "cursive.ttf"
    if not font_path.exists():
        logging.info("선명한 필기체(나눔펜스크립트) 폰트를 다운로드합니다...")
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/NanumPenScript-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            logging.warning(f"폰트 다운로드 실패: {e}")
            
    try:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), 50)
        for name in ["malgun.ttf", "AppleGothic.ttf", "NanumGothic.ttf"]:
            try:
                return ImageFont.truetype(name, 50)
            except IOError:
                continue
    except Exception as e:
        logging.error(f"폰트 로드 실패: {e}")
    return ImageFont.load_default()

def draw_pigtail_pointer(draw: ImageDraw.ImageDraw, text_pos: tuple, head_pos: tuple, text: str, font: ImageFont.FreeTypeFont, scale_factor: float = 1.0):
    """
    네모 박스를 완전히 제거하고, 흰색 필기체 글씨와 부드러운 돼지꼬리 곡선(Pigtail Curve)으로 머리를 가리킵니다.
    """
    tx, ty = text_pos
    hx, hy = head_pos
    
    # 돼지꼬리 회전 곡선 제어점 계산
    mid_x = (tx + hx) / 2
    mid_y = (ty + hy) / 2
    ctrl1 = (mid_x + 30 * scale_factor, ty - 15 * scale_factor)
    ctrl2 = (mid_x - 20 * scale_factor, hy + 20 * scale_factor)
    
    # 곡선 궤적 포인트 생성
    curve_points = []
    steps = 30
    for i in range(steps + 1):
        t = i / float(steps)
        # 3차 베지에 곡선식 (부드러운 S자/돼지꼬리 라인)
        bx = (1-t)**3 * tx + 3*(1-t)**2 * t * ctrl1[0] + 3*(1-t) * t**2 * ctrl2[0] + t**3 * hx
        by = (1-t)**3 * ty + 3*(1-t)**2 * t * ctrl1[1] + 3*(1-t) * t**2 * ctrl2[1] + t**3 * hy
        curve_points.append((bx, by))
        
    # 선 두께 및 라인 렌더링
    line_width = max(int(3 * scale_factor), 2)
    draw.line(curve_points, fill=(255, 255, 255, 240), width=line_width)
    
    # 머리 지점 포인트 점
    r = int(5 * scale_factor)
    draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 255, 255, 255))
    
    # 흰색 필기체 텍스트 (그림자로 가독성 확보)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    text_x = tx - (tw / 2)
    text_y = ty - th - (10 * scale_factor)
    
    # 그림자 및 필기체 본체
    shadow_offset = max(int(2 * scale_factor), 1)
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=(0, 0, 0, 200))
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

def process_image_to_pdf():
    base_dir = Path(__file__).parent.resolve()
    input_img_path = get_input_image_path(base_dir)
    logo_path = base_dir / "애드플랜터스-로고_PNG.png"
    
    # 덮어쓰기 방지를 위한 타임스탬프 기반 고유 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf_path = base_dir / f"output_{timestamp}.pdf"

    if not input_img_path.exists():
        logging.error(f"입력 이미지를 찾을 수 없습니다: {input_img_path}")
        return

    logging.info(f"작업 대상 이미지: {input_img_path.name}")
    logging.info("고화질 자연스러운 그래픽 수정 및 PDF 출력을 시작합니다...")

    try:
        with Image.open(input_img_path) as img:
            img = img.convert("RGBA")
            W, H = img.size
            scale_factor = W / 1000.0

            # 1. 인물 위치 스왑 (카메라 앞 여자 <-> 서 있는 남자) & 경계선 깨짐 방지 패더링
            box_cam = (int(W * 0.02), int(H * 0.50), int(W * 0.22), int(H * 0.95))
            box_stand = (int(W * 0.60), int(H * 0.50), int(W * 0.78), int(H * 0.95))
            
            crop_cam = img.crop(box_cam)
            crop_stand = img.crop(box_stand)
            
            # 경계선 소프트 블렌딩 마스크
            mask_cam = Image.new('L', crop_cam.size, 255).filter(ImageFilter.GaussianBlur(10))
            mask_stand = Image.new('L', crop_stand.size, 255).filter(ImageFilter.GaussianBlur(10))

            crop_cam_resized = crop_cam.resize((box_stand[2] - box_stand[0], box_stand[3] - box_stand[1]), Image.Resampling.LANCZOS)
            mask_cam_resized = mask_cam.resize((box_stand[2] - box_stand[0], box_stand[3] - box_stand[1]), Image.Resampling.LANCZOS)

            crop_stand_resized = crop_stand.resize((box_cam[2] - box_cam[0], box_cam[3] - box_cam[1]), Image.Resampling.LANCZOS)
            mask_stand_resized = mask_stand.resize((box_cam[2] - box_cam[0], box_cam[3] - box_cam[1]), Image.Resampling.LANCZOS)

            img.paste(crop_stand_resized, (box_cam[0], box_cam[1]), mask_stand_resized)
            img.paste(crop_cam_resized, (box_stand[0], box_stand[1]), mask_cam_resized)

            # 2. 하늘 영역 은은한 푸른 빛 오버레이
            sky_overlay = Image.new('RGBA', (W, H), (10, 70, 170, 0))
            sky_draw = ImageDraw.Draw(sky_overlay)
            for y in range(int(H * 0.42)):
                alpha = int(120 * (1 - (y / (H * 0.42))))
                sky_draw.line([(0, y), (W, y)], fill=(10, 80, 190, alpha))
            img = Image.alpha_composite(img, sky_overlay)

            # 3. 기존 문구 박스 흔적 제거 및 '해피메리추석 ♡' 필기체 적용
            draw = ImageDraw.Draw(img, "RGBA")
            title_region = (int(W * 0.15), int(H * 0.33), int(W * 0.85), int(H * 0.46))
            
            sky_sample = img.crop((title_region[0], int(H * 0.05), title_region[2], int(H * 0.18)))
            sky_sample = sky_sample.resize((title_region[2] - title_region[0], title_region[3] - title_region[1]))
            sky_sample = sky_sample.filter(ImageFilter.GaussianBlur(20))
            
            patch_mask = Image.new('L', sky_sample.size, 255).filter(ImageFilter.GaussianBlur(15))
            img.paste(sky_sample, (title_region[0], title_region[1]), patch_mask)

            # 메인 필기체 폰트
            base_font = ensure_cursive_font(base_dir)
            main_font = ImageFont.truetype(str(base_dir / "cursive.ttf"), int(80 * scale_factor)) if (base_dir / "cursive.ttf").exists() else base_font
            tag_font = ImageFont.truetype(str(base_dir / "cursive.ttf"), int(38 * scale_factor)) if (base_dir / "cursive.ttf").exists() else base_font

            main_text = "해피메리추석 ♡"
            tb = draw.textbbox((0, 0), main_text, font=main_font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx_pos = (W - tw) / 2
            ty_pos = H * 0.35

            draw.text((tx_pos + 3, ty_pos + 3), main_text, font=main_font, fill=(0, 0, 0, 180))
            draw.text((tx_pos, ty_pos), main_text, font=main_font, fill=(255, 255, 255, 255))

            # 4. 박스 없는 필기체 직책 & 돼지꼬리 곡선 연결
            people_targets = [
                ((W * 0.11, H * 0.48), (W * 0.11, H * 0.53), "촬영감독"),
                ((W * 0.33, H * 0.51), (W * 0.33, H * 0.56), "셀럽A"),
                ((W * 0.55, H * 0.57), (W * 0.58, H * 0.62), "CEO"),
                ((W * 0.69, H * 0.48), (W * 0.69, H * 0.53), "셀럽B"),
                ((W * 0.79, H * 0.53), (W * 0.79, H * 0.58), "웹기획자"),
                ((W * 0.90, H * 0.63), (W * 0.91, H * 0.68), "마케터")
            ]

            for t_pos, h_pos, role_name in people_targets:
                draw_pigtail_pointer(draw, t_pos, h_pos, role_name, tag_font, scale_factor)

            # 5. 하단 투명 PNG 로고 합성
            if logo_path.exists():
                logo_area = (int(W * 0.30), int(H * 0.92), int(W * 0.70), int(H * 0.99))
                bg_patch = Image.new('RGBA', (logo_area[2] - logo_area[0], logo_area[3] - logo_area[1]), (12, 10, 20, 255))
                bg_mask = Image.new('L', bg_patch.size, 255).filter(ImageFilter.GaussianBlur(10))
                img.paste(bg_patch, (logo_area[0], logo_area[1]), bg_mask)

                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    lw, lh = logo_area[2] - logo_area[0], logo_area[3] - logo_area[1]
                    logo.thumbnail((lw, lh), Image.Resampling.LANCZOS)

                    px = logo_area[0] + (lw - logo.width) // 2
                    py = logo_area[1] + (lh - logo.height) // 2
                    img.paste(logo, (px, py), mask=logo)

            # 6. 고해상도 무손실 PDF 생성 (덮어쓰기 방지된 고유 파일명 저장)
            rgb_img = img.convert("RGB")
            rgb_img.save(output_pdf_path, "PDF", resolution=300.0, save_all=True, quality=100)
            logging.info(f"신규 고화질 PDF 생성이 완료되었습니다: {output_pdf_path.name}")

    except Exception as e:
        logging.error(f"처리 중 오류 발생: {e}")

if __name__ == "__main__":
    process_image_to_pdf()