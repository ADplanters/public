"""
=============================================================================
의존성 라이브러리 설치:
pip install pillow img2pdf python-dotenv
=============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageFont
import img2pdf
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 존재할 경우)
load_dotenv()

# ---------------------------------------------------------------------------
# 로깅 설정
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# ---------------------------------------------------------------------------
# 안전한 시스템 폰트 로더 (Fallback 지원)
# ---------------------------------------------------------------------------
def load_system_font(font_size: int = 16) -> ImageFont.FreeTypeFont:
    """
    운영체제별 가용한 시스템 폰트를 탐색하여 로드합니다.
    """
    candidate_fonts = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    ]
    for font_path in candidate_fonts:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                continue
    return ImageFont.load_default()

# ---------------------------------------------------------------------------
# 고화질 디밸롭 (Super-Sampling & Text Edge Sharpening) 엔진
# ---------------------------------------------------------------------------
def develop_high_res_image(
    image_path: Path,
    scale_factor: float = 3.0,
    sharpness_amount: float = 1.8,
    contrast_amount: float = 1.08
) -> Image.Image:
    """
    1. Lanczos3 알고리즘으로 해상도(픽셀 밀도)를 3배 확장
    2. Unsharp Mask 필터로 텍스트 윤곽선과 경계면 복원
    3. 색상 뭉개짐/번짐 없는 깔끔한 텍스트 가독성 최적화
    """
    with Image.open(image_path) as img:
        # RGBA / Palette 모드를 깔끔한 RGB로 변환 (배경 흰색)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 1. 고밀도 슈퍼 샘플링 (Lanczos 리사이징)
        target_w = int(img.width * scale_factor)
        target_h = int(img.height * scale_factor)
        enhanced_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 2. Unsharp Mask 필터로 텍스트 엣지 정밀 선명화 (물감 번짐 현상 방지)
        enhanced_img = enhanced_img.filter(
            ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=3)
        )

        # 3. 선명도 및 대비 미세 튜닝
        if sharpness_amount != 1.0:
            enhanced_img = ImageEnhance.Sharpness(enhanced_img).enhance(sharpness_amount)
        if contrast_amount != 1.0:
            enhanced_img = ImageEnhance.Contrast(enhanced_img).enhance(contrast_amount)

        return enhanced_img

# ---------------------------------------------------------------------------
# 단일 고화질 PDF 생성
# ---------------------------------------------------------------------------
def convert_to_high_res_pdf(image_path: Path, output_pdf_path: Path) -> bool:
    """
    디밸롭된 초고해상도 비트맵을 300 DPI 기준 무손실 PDF로 인코딩합니다.
    """
    if not image_path.exists():
        logging.error(f"파일을 찾을 수 없습니다: {image_path.name}")
        return False

    temp_hd_path = image_path.parent / f"_temp_hd_{image_path.stem}.png"

    try:
        # 고화질 이미지 디밸롭 처리
        hd_img = develop_high_res_image(image_path)
        
        # 300 DPI 무손실 PNG로 임시 저장
        hd_img.save(temp_hd_path, format="PNG", compress_level=0, dpi=(300, 300))

        # img2pdf를 활용한 무손실 PDF 패킹
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(str(temp_hd_path)))

        logging.info(f"[디밸롭 성공] {image_path.name} -> {output_pdf_path.name} ({hd_img.width}x{hd_img.height} px, 300DPI)")
        return True

    except Exception as e:
        logging.error(f"[변환 실패] {image_path.name}: {e}")
        return False

    finally:
        if temp_hd_path.exists():
            try:
                os.remove(temp_hd_path)
            except Exception:
                pass

# ---------------------------------------------------------------------------
# 전체 합본 고화질 PDF 생성
# ---------------------------------------------------------------------------
def create_combined_high_res_pdf(image_paths: List[Path], output_pdf_path: Path) -> bool:
    """
    모든 슬라이드 이미지를 디밸롭하여 단일 고해상도 PDF로 병합합니다.
    """
    temp_files: List[Path] = []
    try:
        for img_path in image_paths:
            if not img_path.exists():
                continue
            
            hd_img = develop_high_res_image(img_path)
            temp_path = img_path.parent / f"_temp_comb_{img_path.stem}.png"
            hd_img.save(temp_path, format="PNG", compress_level=0, dpi=(300, 300))
            temp_files.append(temp_path)

        if not temp_files:
            return False

        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert([str(p) for p in temp_files]))

        logging.info(f"[합본 디밸롭 성공] {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[합본 생성 실패]: {e}")
        return False

    finally:
        for temp_f in temp_files:
            if temp_f.exists():
                try:
                    os.remove(temp_f)
                except Exception:
                    pass

# ---------------------------------------------------------------------------
# 메인 실행 구문
# ---------------------------------------------------------------------------
def main():
    base_dir = Path(__file__).parent.resolve()
    
    # Slice 1 ~ Slice 6 (.png 및 .jpg 모두 지원)
    valid_image_paths: List[Path] = []

    logging.info("==========================================")
    logging.info(" 초고해상도/선명도 디밸롭 PDF 변환 시작")
    logging.info("==========================================")

    for i in range(1, 7):
        png_path = base_dir / f"Slice {i}.png"
        jpg_path = base_dir / f"Slice {i}.jpg"
        
        target_path = png_path if png_path.exists() else (jpg_path if jpg_path.exists() else None)

        if target_path:
            pdf_out_path = base_dir / f"Slice {i}.pdf"
            if convert_to_high_res_pdf(target_path, pdf_out_path):
                valid_image_paths.append(target_path)
        else:
            logging.warning(f"Slice {i} (.png / .jpg) 파일을 찾을 수 없습니다.")

    if valid_image_paths:
        combined_pdf_path = base_dir / "Slice_All_Combined.pdf"
        create_combined_high_res_pdf(valid_image_paths, combined_pdf_path)

    logging.info("==========================================")
    logging.info(" 모든 디밸롭 PDF 작업이 완료되었습니다.")
    logging.info("==========================================")

if __name__ == "__main__":
    main()