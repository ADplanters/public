"""
image_to_pdf/main.py

Requirements:
Pillow
"""

import os
import logging
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_cursive_font(base_dir: Path) -> Path:
    """한글 필기체 폰트(나눔펜스크립트)가 없으면 자동으로 다운로드합니다."""
    font_path = base_dir / "cursive.ttf"
    if not font_path.exists():
        logging.info("필기체 폰트를 다운로드 중입니다...")
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/NanumPenScript-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
            logging.info("필기체 폰트 다운로드 완료.")
        except Exception as e:
            logging.warning(f"폰트 다운로드 실패: {e}")
    return font_path

def get_cursive_font(base_dir: Path, size: int) -> ImageFont.FreeTypeFont:
    """필기체 폰트를 로드하고, 없을 경우 시스템 폰트로 폴백합니다."""
    font_path = ensure_cursive_font(base_dir)
    try:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
        for name in ["malgun.ttf", "AppleGothic.ttf", "NanumGothic.ttf"]:
            try:
                return ImageFont.truetype(name, size)
            except IOError:
                continue
    except Exception as e:
        logging.error(f"폰트 로드 실패: {e}")
    return ImageFont.load_default()

def draw_pigtail_tag(draw: ImageDraw.ImageDraw, text_pos: tuple, head_pos: tuple, text: str, font: ImageFont.FreeTypeFont):
    """
    네모 박스 없이 흰색 필기체 텍스트와 곡선 돼지 꼬리표(화살표/포인터)로 자연스럽게 연결합니다.
    """
    tx, ty = text_pos
    hx, hy = head_pos
    
    # 1. 곡선 돼지 꼬리표 지점 계산 (주변을 돌아서 머리를 가리키는 부드러운 S자/돼지꼬리 형태)
    ctrl_x = tx + (hx - tx) * 0.5 + 20
    ctrl_y = ty + (hy - ty) * 0.5 - 15
    
    # 베지에 곡선 좌표 생성
    points = []
    for t in [i / 20.0 for i in range(21)]:
        bx = (1 - t)**2 * tx + 2 * (1 - t) * t * ctrl_x + t**2 * hx
        by = (1 - t)**2 * ty + 2 * (1 - t) * t * ctrl_y + t**2 * hy
        points.append((bx, by))
    
    # 꼬리표 선 그리기 (자연스러운 부드러운 흰색 선)
    draw.line(points, fill=(255, 255, 255, 230), width=3)
    
    # 머리 지점에 작은 포인트 원 그리기
    r = 4
    draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 255, 255, 255))
    
    # 2. 흰색 필기체 텍스트 작성 (그림자 효과로 가독성 보장)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    text_x = tx - (tw / 2)
    text_y = ty - th
    
    # 텍스트 은은한 검은색 그림자 (가독성 향상)
    draw.text((text_x + 2, text_y + 2), text, font=font, fill=(0, 0, 0, 180))
    # 선명한 흰색 필기체 본체
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

def process_image_to_pdf():
    base_dir = Path(__file__).parent.resolve()
    input_img_path = base_dir / "image_56c6ff.jpg"
    logo_path = base_dir / "애드플랜터스-로고_PNG.png"
    output_pdf_path = base_dir / "output_high_res.pdf"

    if not input_img_path.exists():
        logging.error(f"원본 이미지가 존재하지 않습니다: {input_img_path}")
        return

    logging.info("고화질 그래픽 정밀 재구성 작업을 시작합니다...")

    try:
        with Image.open(input_img_path) as img:
            img = img.convert("RGBA")
            W, H = img.size

            # ---------------------------------------------------------
            # 1. 인물 스왑 (사각형 경계선 깨짐 방지를 위한 패더링 알몸 합성)
            # ---------------------------------------------------------
            box_cam = (int(W * 0.02), int(H * 0.52), int(W * 0.22), int(H * 0.95))
            box_stand = (int(W * 0.60), int(H * 0.52), int(W * 0.78), int(H * 0.95))
            
            crop_cam = img.crop(box_cam)
            crop_stand = img.crop(box_stand)
            
            # 부드러운 가장자리 마스크 생성 (경계선 잘림 현상 제거)
            def create_feather_mask(size, radius=15):
                mask = Image.new('L', size, 255)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.rectangle([0, 0, size[0], size[1]], fill=255)
                return mask.filter(ImageFilter.GaussianBlur(radius))

            mask_cam = create_feather_mask(crop_cam.size)
            mask_stand = create_feather_mask(crop_stand.size)

            crop_cam_resized = crop_cam.resize((box_stand[2] - box_stand[0], box_stand[3] - box_stand[1]), Image.Resampling.LANCZOS)
            mask_cam_resized = mask_cam.resize((box_stand[2] - box_stand[0], box_stand[3] - box_stand[1]), Image.Resampling.LANCZOS)

            crop_stand_resized = crop_stand.resize((box_cam[2] - box_cam[0], box_cam[3] - box_cam[0] * 0 + (box_cam[3] - box_cam[1])), Image.Resampling.LANCZOS)
            mask_stand_resized = mask_stand.resize((box_cam[2] - box_cam[0], box_cam[3] - box_cam[1]), Image.Resampling.LANCZOS)

            img.paste(crop_stand_resized, (box_cam[0], box_cam[1]), mask_stand_resized)
            img.paste(crop_cam_resized, (box_stand[0], box_stand[1]), mask_cam_resized)

            # ---------------------------------------------------------
            # 2. 하늘 푸른색 자연스러운 블렌딩 (어색한 네모 상자 블록 제거)
            # ---------------------------------------------------------
            sky_gradient = Image.new('RGBA', (W, H), (15, 60, 160, 0))
            sky_draw = ImageDraw.Draw(sky_gradient)
            for y in range(int(H * 0.40)):
                alpha = int(110 * (1 - (y / (H * 0.40))))
                sky_draw.line([(0, y), (W, y)], fill=(15, 75, 180, alpha))
            img = Image.alpha_composite(img, sky_gradient)

            # ---------------------------------------------------------
            # 3. 기존 문구 이질감 없이 삭제 및 필기체 '해피메리추석' 적용
            # ---------------------------------------------------------
            # 부드러운 패더링 마스크로 기존 글자 영역만 자연스럽게 배경 블러 처리
            title_region_box = (int(W * 0.15), int(H * 0.35), int(W * 0.85), int(H * 0.45))
            sky_patch = img.crop((int(W * 0.15), int(H * 0.05), int(W * 0.85), int(H * 0.15)))
            sky_patch = sky_patch.resize((title_region_box[2] - title_region_box[0], title_region_box[3] - title_region_box[1]))
            sky_patch = sky_patch.filter(ImageFilter.GaussianBlur(20))
            
            patch_mask = create_feather_mask(sky_patch.size, radius=25)
            img.paste(sky_patch, (title_region_box[0], title_region_box[1]), patch_mask)

            # 메인 필기체 폰트 로드
            draw = ImageDraw.Draw(img, "RGBA")
            main_title_font = get_cursive_font(base_dir, int(W * 0.095))
            main_text = "해피메리추석 ♡"

            tb = draw.textbbox((0, 0), main_text, font=main_title_font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx_pos = (W - tw) / 2
            ty_pos = H * 0.36

            # 글자 그림자 및 필기체 작성
            draw.text((tx_pos + 3, ty_pos + 3), main_text, font=main_title_font, fill=(0, 0, 0, 150))
            draw.text((tx_pos, ty_pos), main_text, font=main_title_font, fill=(255, 255, 255, 255))

            # ---------------------------------------------------------
            # 4. 돼지 꼬리표 화살표 및 흰색 필기체 직책 연결
            # ---------------------------------------------------------
            tag_font = get_cursive_font(base_dir, int(W * 0.042))
            
            # (텍스트 위치(x, y), 머리 위치(x, y), 직책명)
            people_targets = [
                ((W * 0.11, H * 0.47), (W * 0.11, H * 0.52), "촬영감독"),
                ((W * 0.33, H * 0.51), (W * 0.33, H * 0.56), "셀럽A"),
                ((W * 0.55, H * 0.57), (W * 0.58, H * 0.62), "CEO"),
                ((W * 0.69, H * 0.47), (W * 0.69, H * 0.53), "셀럽B"),
                ((W * 0.79, H * 0.53), (W * 0.79, H * 0.58), "웹기획자"),
                ((W * 0.90, H * 0.63), (W * 0.91, H * 0.68), "마케터")
            ]

            for t_pos, h_pos, role_name in people_targets:
                draw_pigtail_tag(draw, t_pos, h_pos, role_name, tag_font)

            # ---------------------------------------------------------
            # 5. 하단 투명 PNG 로고 부드러운 자연 합성
            # ---------------------------------------------------------
            if logo_path.exists():
                logo_area = (int(W * 0.30), int(H * 0.92), int(W * 0.70), int(H * 0.99))
                # 기존 로고 자리 주변 자연스러운 그라데이션 커버
                cover_patch = Image.new('RGBA', (logo_area[2] - logo_area[0], logo_area[3] - logo_area[1]), (12, 10, 20, 240))
                cover_mask = create_feather_mask(cover_patch.size, radius=15)
                img.paste(cover_patch, (logo_area[0], logo_area[1]), cover_mask)

                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    lw = logo_area[2] - logo_area[0]
                    lh = logo_area[3] - logo_area[1]
                    logo.thumbnail((lw, lh), Image.Resampling.LANCZOS)

                    px = logo_area[0] + (lw - logo.width) // 2
                    py = logo_area[1] + (lh - logo.height) // 2
                    img.paste(logo, (px, py), mask=logo)

            # ---------------------------------------------------------
            # 6. 초고화질 무손실 PDF 출력
            # ---------------------------------------------------------
            rgb_img = img.convert("RGB")
            rgb_img.save(output_pdf_path, "PDF", resolution=300.0, save_all=True, quality=100)
            logging.info(f"선명한 고화질 PDF 생성이 완료되었습니다: {output_pdf_path}")

    except Exception as e:
        logging.error(f"처리 중 오류 발생: {e}")

if __name__ == "__main__":
    process_image_to_pdf()