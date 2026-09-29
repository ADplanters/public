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
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageFont
import img2pdf
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일 환경 대비)
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
    운영체제별 가용한 시스템 폰트를 탐색하여 안전하게 로드합니다.
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
# 단일 이미지 고화질 디밸롭 & 300DPI PDF 변환 엔진
# ---------------------------------------------------------------------------
def process_single_image_to_pdf(
    image_path: Path,
    output_pdf_path: Path,
    scale_factor: float = 3.0,
    target_dpi: int = 300
) -> bool:
    """
    1. Lanczos3 알고리즘으로 이미지 픽셀 밀도를 3배 확장
    2. Unsharp Mask 정밀 필터 적용으로 텍스트 선명도 극대화
    3. img2pdf 기반 300 DPI 무손실 PDF 인코딩
    """
    if not image_path.exists():
        logging.error(f"[오류] 대상을 찾을 수 없습니다: {image_path.name}")
        return False

    temp_hd_path = image_path.parent / f"_temp_hd_{image_path.stem}.png"

    try:
        logging.info(f"-> '{image_path.name}' 고화질 디밸롭 보정 시작...")
        
        with Image.open(image_path) as img:
            # 1. 색상 모드 최적화 (RGB 전환 및 투명도 배경 흰색 처리)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 2. Lanczos 고밀도 리사이징 (해상도 3배 확장)
            target_w = int(img.width * scale_factor)
            target_h = int(img.height * scale_factor)
            hd_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # 3. 텍스트 경계면 디테일 향상 (Unsharp Mask)
            hd_img = hd_img.filter(
                ImageFilter.UnsharpMask(radius=1.5, percent=170, threshold=2)
            )

            # 4. 대비 및 선명도 미세 조정
            hd_img = ImageEnhance.Sharpness(hd_img).enhance(1.8)
            hd_img = ImageEnhance.Contrast(hd_img).enhance(1.08)

            # 5. 무손실 임시 이미지 저장
            hd_img.save(temp_hd_path, format="PNG", compress_level=0, dpi=(target_dpi, target_dpi))
            logging.info(f"   - 해상도 확장 완료: {img.width}x{img.height} px -> {hd_img.width}x{hd_img.height} px")

        # 6. 무손실 PDF 생성
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(str(temp_hd_path)))

        logging.info(f"[성공] 고화질 PDF 생성 완료: {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[변환 실패] {image_path.name}: {e}")
        return False

    finally:
        # 임시 가공 파일 정리
        if temp_hd_path.exists():
            try:
                os.remove(temp_hd_path)
            except Exception:
                pass

# ---------------------------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------------------------
def main():
    base_dir = Path(__file__).parent.resolve()

    # Slice 1 관련 전달받은 파일 탐색 (Slice 1_2.jpg, Slice 1.jpg, Slice 1.png 등)
    candidate_names = ["Slice 1_2.jpg", "Slice 1.jpg", "Slice 1.png", "Slice 1_2.png"]
    target_image_path: Optional[Path] = None

    for name in candidate_names:
        chk_path = base_dir / name
        if chk_path.exists():
            target_image_path = chk_path
            break

    # 파일명을 직접 지정하려면 아래 변수에 넣으셔도 됩니다.
    if not target_image_path:
        # 폴더 내 Slice 1로 시작하는 모든 이미지 탐색
        for p in base_dir.glob("Slice 1*"):
            if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                target_image_path = p
                break

    if target_image_path:
        output_pdf = base_dir / "Slice_1_MaxRes.pdf"
        logging.info("==========================================")
        logging.info(" Slice 1 최대 해상도 PDF 디밸롭 변환")
        logging.info("==========================================")
        process_single_image_to_pdf(target_image_path, output_pdf)
        logging.info("==========================================")
    else:
        logging.error("폴더에 'Slice 1' 이미지가 존재하지 않습니다. 이미지 파일명을 확인해 주세요.")

if __name__ == "__main__":
    main()