"""
=============================================================================
의존성 라이브러리 설치 명령어:
pip install pillow reportlab img2pdf python-dotenv
=============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageFont, ImageDraw
from reportlab.pdfgen import canvas
import img2pdf

# ---------------------------------------------------------------------------
# 로깅 설정
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# ---------------------------------------------------------------------------
# 폰트 안전 로드 로직 (시스템 폰트 폴백 메커니즘)
# ---------------------------------------------------------------------------
def load_safe_font(font_size: int = 20) -> ImageFont.FreeTypeFont:
    """
    OS 환경별 시스템 폰트를 자동 탐색하여 안전하게 로드합니다.
    """
    candidate_fonts = [
        # Windows
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/arial.ttf",
        # macOS
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/Arial.ttf",
        # Linux / Ubuntu
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/gnu-free/FreeSans.ttf",
    ]
    
    for font_path in candidate_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                continue
    
    return ImageFont.load_default()

# ---------------------------------------------------------------------------
# 고해상도 업스케일링 & 선명도(Sharpness) 극대화 엔진
# ---------------------------------------------------------------------------
def enhance_image_for_ultra_clarity(
    img: Image.Image,
    upscale_factor: float = 2.0,
    sharpness_factor: float = 2.2,
    contrast_factor: float = 1.15,
    brightness_factor: float = 1.02,
    color_factor: float = 1.05
) -> Image.Image:
    """
    이미지 해상도 저하 및 흐림 현상을 제거하는 이미지 보정 함수
    - Lanczos 고품질 업스케일링 (픽셀 밀도 증가)
    - Unsharp Mask 필터로 윤곽선 및 텍스트 경계선 명확화
    - 대비/선명도 극대화 튜닝
    """
    # 1. 알파 채널/투명도 RGBA -> RGB 최적화 처리
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # 2. Lanczos 보간법을 활용한 고해상도 리사이즈 (픽셀 해상도 2배 확대)
    if upscale_factor > 1.0:
        new_w = int(img.width * upscale_factor)
        new_h = int(img.height * upscale_factor)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 3. 언샤프 마스크(Unsharp Mask) 필터 적용하여 선명한 텍스트/윤곽 복원
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))

    # 4. Pillow ImageEnhance 알고리즘 적용
    if sharpness_factor != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)
    if contrast_factor != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    if brightness_factor != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness_factor)
    if color_factor != 1.0:
        img = ImageEnhance.Color(img).enhance(color_factor)

    return img

# ---------------------------------------------------------------------------
# ReportLab 기반 고해상도 300 DPI PDF 생성
# ---------------------------------------------------------------------------
def create_high_res_pdf_reportlab(
    image_path: Path,
    output_pdf_path: Path,
    target_dpi: int = 300
) -> bool:
    """
    300 DPI 규격에 맞춘 고해상도 PDF 캔버스 매핑 생성을 진행합니다.
    """
    try:
        with Image.open(image_path) as orig_img:
            # 고화질 보정 및 업스케일링 적용
            enhanced_img = enhance_image_for_ultra_clarity(orig_img)
            
            # 임시 무손실 PNG 비트맵으로 디스크 저장
            temp_path = image_path.parent / f"_ultra_hd_{image_path.name}"
            enhanced_img.save(temp_path, format="PNG", compress_level=0, dpi=(target_dpi, target_dpi))

            # PDF 포인트 (1 Inch = 72 Point) 환산
            width_px, height_px = enhanced_img.size
            width_pt = (width_px / target_dpi) * 72.0
            height_pt = (height_px / target_dpi) * 72.0

            # ReportLab Canvas에 고해상도 드로잉
            c = canvas.Canvas(str(output_pdf_path), pagesize=(width_pt, height_pt))
            c.drawImage(str(temp_path), 0, 0, width=width_pt, height=height_pt, preserveAspectRatio=True)
            c.save()

            if temp_path.exists():
                os.remove(temp_path)

            logging.info(f"[성공] 300 DPI 초고화질 PDF 생성 완료: {output_pdf_path.name} ({width_px}x{height_px} px)")
            return True

    except Exception as e:
        logging.error(f"[오류] PDF 생성 실패 ({image_path.name}): {e}")
        return False

# ---------------------------------------------------------------------------
# 전체 합본 PDF 생성
# ---------------------------------------------------------------------------
def create_combined_pdf(image_paths: List[Path], output_pdf_path: Path, target_dpi: int = 300) -> bool:
    """
    보정된 고해상도 이미지를 묶어 하나로 구성된 합본 PDF를 만듭니다.
    """
    temp_enhanced_files = []
    try:
        for img_path in image_paths:
            with Image.open(img_path) as orig_img:
                enhanced_img = enhance_image_for_ultra_clarity(orig_img)
                temp_file = img_path.parent / f"_comb_hd_{img_path.name}"
                enhanced_img.save(temp_file, format="PNG", compress_level=0, dpi=(target_dpi, target_dpi))
                temp_enhanced_files.append(temp_file)

        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert([str(p) for p in temp_enhanced_files]))

        logging.info(f"[성공] 초고화질 합본 PDF 생성 완료: {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[오류] 합본 PDF 생성 중 에러 발생: {e}")
        return False

    finally:
        for temp_file in temp_enhanced_files:
            if temp_file.exists():
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

# ---------------------------------------------------------------------------
# 실행 메인 구문
# ---------------------------------------------------------------------------
def main():
    base_dir = Path(__file__).parent.resolve()
    
    slice_names = [f"Slice {i}.png" for i in range(1, 7)]
    valid_images = []

    logging.info("==========================================")
    logging.info(" 초고화질/선명도 극대화 PDF 변환 작업 시작")
    logging.info("==========================================")

    for name in slice_names:
        img_path = base_dir / name
        if img_path.exists():
            pdf_path = base_dir / f"{img_path.stem}.pdf"
            if create_high_res_pdf_reportlab(img_path, pdf_path):
                valid_images.append(img_path)
        else:
            logging.warning(f"파일을 찾을 수 없습니다: {name}")

    if valid_images:
        combined_pdf_path = base_dir / "Slice_All_Combined.pdf"
        create_combined_pdf(valid_images, combined_pdf_path)

    logging.info("==========================================")
    logging.info(" 모든 작업이 완벽하게 처리되었습니다.")
    logging.info("==========================================")

if __name__ == "__main__":
    main()