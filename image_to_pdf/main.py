# ==========================================
# File: main.py
# Description: 단가표/로고 이미지 오탐지를 방지하고, 지정된 9:16 '해피메리추석' 포스터를 300 DPI 고해상도 PDF로 변환하는 스크립트
# Location: github_repo/image_to_pdf/main.py
# ==========================================
# [Requirements]
# pip install pillow reportlab python-dotenv
# ==========================================

import os
import sys
import logging
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas

# --- [터미널 실시간 로깅 설정] ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# --- [상수 및 절대 경로 설정] ---
BASE_DIR = Path(__file__).parent.resolve()
PDF_DPI = 300  # 고해상도 인쇄 규격 (300 DPI)
OUTPUT_PDF_NAME = "ADPLANTERS_HappyMerryChuseok_300DPI.pdf"

# 단가표, 안내문, 로고, 파비콘 등 잘못된 이미지 변환 방지용 필터 키워드
EXCLUDE_KEYWORDS = ["광고", "상품", "안내", "단가", "price", "table", "logo", "favicon", "banner", "로고", "파비콘", "배너", "icon"]

def find_chuseok_poster_image(script_dir: Path) -> Path:
    """
    단가표/안내문/로고 이미지를 제외하고 '해피메리추석' 포스터 이미지 파일만 정확히 찾습니다.
    """
    valid_extensions = ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG")
    candidates = []

    for ext in valid_extensions:
        for file_path in script_dir.glob(ext):
            filename_lower = file_path.name.lower()
            # 단가표 및 안내문 등 제외 키워드 검사
            if any(keyword in filename_lower for keyword in EXCLUDE_KEYWORDS):
                continue
            candidates.append(file_path)

    if candidates:
        # 조건에 맞는 최신 포스터 이미지 선택
        latest_file = max(candidates, key=lambda p: p.stat().st_mtime)
        logging.info(f"🔍 변환 대상 포스터 이미지 감지: {latest_file.name}")
        return latest_file

    return None

def convert_image_to_pdf(image_path: Path, pdf_path: Path) -> bool:
    """
    포스터 이미지를 화질 손실 없이 300 DPI 고해상도 규격의 PDF 문서로 변환합니다.
    """
    logging.info(f"📄 PDF 변환 시작: {image_path.name} -> {pdf_path.name}")

    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            img_mode = img.mode
            logging.info(f"📊 이미지 해상도 분석: {img_width} x {img_height} px ({img_mode})")

            # 300 DPI 기준 PDF Canvas Point 단위 계산 (1 inch = 72 points)
            page_width_pts = (img_width / PDF_DPI) * 72
            page_height_pts = (img_height / PDF_DPI) * 72

            c = canvas.Canvas(str(pdf_path), pagesize=(page_width_pts, page_height_pts))
            c.drawImage(
                str(image_path),
                0, 0,
                width=page_width_pts,
                height=page_height_pts,
                preserveAspectRatio=True,
                mask='auto'
            )
            c.showPage()
            c.save()

            logging.info(f"🎉 300 DPI 고해상도 PDF 출력 성공: {pdf_path.name}")
            return True

    except MemoryError:
        logging.error("❌ 메모리 부족: 이미지 해상도가 가용 메모리를 초과했습니다.")
        return False
    except PermissionError:
        logging.error("❌ 권한 오류: 출력할 PDF 파일이 다른 프로그램에서 열려 있는지 확인하세요.")
        return False
    except Exception as e:
        logging.error(f"❌ PDF 변환 중 예기치 못한 오류 발생: {e}", exc_info=True)
        return False

def main():
    print("\n" + "="*65)
    print("🚀 [ADPLANTERS] 해피메리추석 포스터 -> 300 DPI PDF 출력기")
    print("="*65)
    logging.info(f"작업 폴더 위치: {BASE_DIR}")

    # 1. 단가표/로고 제외 후 포스터 이미지 탐색
    target_image = find_chuseok_poster_image(BASE_DIR)

    if not target_image:
        logging.error("❌ 'image_to_pdf' 폴더 내에서 변환할 포스터 이미지를 찾을 수 없습니다.")
        print("-" * 65)
        print("💡 [해결 방법]")
        print("1. 생성된 세로형 '해피메리추석' 포스터 이미지를 다운로드받으세요.")
        print(f"2. 다운로드받은 파일(.png/.jpg)을 '{BASE_DIR}' 폴더에 넣으세요.")
        print("3. 단가표나 로고 이미지 파일은 폴더에서 삭제하거나 이동해 주세요.")
        print("="*65 + "\n")
        return

    # 2. 고해상도 PDF 변환
    output_pdf_path = BASE_DIR / OUTPUT_PDF_NAME
    success = convert_image_to_pdf(target_image, output_pdf_path)

    print("-" * 65)
    if success:
        print("✅ [성공] 고해상도 300 DPI PDF 출력이 완료되었습니다!")
        print(f"📁 생성된 PDF 파일 경로: {output_pdf_path}")
    else:
        print("❌ [실패] 변환 도중 오류가 발생했습니다. 로그를 확인해 주세요.")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()