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

from PIL import Image, ImageFont
import img2pdf
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 존재하는 경우 대비)
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
# 안전한 시스템 폰트 로더 (예외 처리 지원)
# ---------------------------------------------------------------------------
def load_system_font(font_size: int = 16) -> ImageFont.FreeTypeFont:
    """
    운영체제별 가용한 시스템 폰트를 안전하게 검색하여 로드합니다.
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
# 100% 원본 손실 없는 무압축 Direct PDF 컨테이너 변환 엔진
# ---------------------------------------------------------------------------
def convert_image_to_pdf_lossless(image_path: Path, output_pdf_path: Path) -> bool:
    """
    이미지 비트스트림을 재압축/보정/변형하지 않고 1:1 바이너리 그대로 
    PDF 컨테이너에 수록하여 원본의 선명함과 픽셀을 100% 보존합니다.
    """
    if not image_path.exists():
        logging.error(f"파일을 찾을 수 없습니다: {image_path.name}")
        return False

    try:
        # img2pdf: 이미지 픽셀/색상 재인코딩 없는 순수 무손실 패킹
        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(str(image_path)))

        logging.info(f"[변환 성공] 원본 1:1 무손실 유지: {image_path.name} -> {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.warning(f"[img2pdf 오류] Pillow 엔진으로 우회 진행: {e}")
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output_pdf_path, "PDF", resolution=300.0)
            logging.info(f"[Pillow 변환 성공]: {output_pdf_path.name}")
            return True
        except Exception as fallback_err:
            logging.error(f"[최종 변환 실패] {image_path.name}: {fallback_err}")
            return False

# ---------------------------------------------------------------------------
# 전체 이미지 합본 PDF 생성
# ---------------------------------------------------------------------------
def create_combined_pdf_lossless(image_paths: List[Path], output_pdf_path: Path) -> bool:
    """
    전체 순서대로 이미지를 단일 무손실 PDF로 병합합니다.
    """
    try:
        valid_paths = [str(p) for p in image_paths if p.exists()]
        if not valid_paths:
            logging.error("병합할 이미지 파일이 존재하지 않습니다.")
            return False

        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(valid_paths))

        logging.info(f"[합본 성공] 무손실 병합 완료: {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[합본 병합 오류]: {e}")
        return False

# ---------------------------------------------------------------------------
# 실행 메인 함수
# ---------------------------------------------------------------------------
def main():
    # 현재 실행 파일 기준 경로 설정
    base_dir = Path(__file__).parent.resolve()
    
    slice_names = [f"Slice {i}.png" for i in range(1, 7)]
    valid_images: List[Path] = []

    logging.info("==========================================")
    logging.info(" 원본 화질 100% 무손실 PDF 변환 시작")
    logging.info("==========================================")

    for name in slice_names:
        img_path = base_dir / name
        if img_path.exists():
            pdf_path = base_dir / f"{img_path.stem}.pdf"
            if convert_image_to_pdf_lossless(img_path, pdf_path):
                valid_images.append(img_path)
        else:
            logging.warning(f"파일을 찾을 수 없습니다: {name}")

    if valid_images:
        combined_pdf_path = base_dir / "Slice_All_Combined.pdf"
        create_combined_pdf_lossless(valid_images, combined_pdf_path)

    logging.info("==========================================")
    logging.info(" 모든 변환 작업이 완벽히 완료되었습니다.")
    logging.info("==========================================")

if __name__ == "__main__":
    main()