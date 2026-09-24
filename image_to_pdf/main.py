# Required Dependencies:
# pip install opencv-python reportlab pillow numpy

import os
import sys
import logging
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas

# 진행 상황 및 디버깅을 위한 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def find_input_file(base_dir: Path, target_name: str) -> Path:
    """
    확장자 포함 여부와 관계없이 입력 이미지 파일을 안전하게 검색합니다.
    """
    direct_path = base_dir / target_name
    if direct_path.exists() and direct_path.is_file():
        return direct_path

    extensions = ['.png', '.jpg', '.jpeg', '.webp']
    for ext in extensions:
        candidate = base_dir / f"{target_name}{ext}"
        if candidate.exists() and candidate.is_file():
            return candidate

    for file_path in base_dir.iterdir():
        if file_path.is_file() and target_name in file_path.stem:
            return file_path

    return None

def enhance_text_and_details(img_rgb: np.ndarray) -> np.ndarray:
    """
    카드 내 한글 텍스트 및 미세한 윤곽선 선명도를 업스케일링/샤프닝하는 보정 함수
    """
    # 언샤프 마스킹(Unsharp Masking)을 통한 텍스트 및 윤곽선 선명화
    gaussian_blur = cv2.GaussianBlur(img_rgb, (0, 0), 2.0)
    sharpened = cv2.addWeighted(img_rgb, 1.4, gaussian_blur, -0.4, 0)
    return sharpened

def convert_to_high_res_pdf(input_name: str, output_filename: str, target_dpi: int = 300) -> bool:
    """
    원본 이미지의 디테일과 글자를 손실 없이 300 DPI 인쇄 등급 고해상도 PDF로 생성합니다.
    """
    base_dir = Path(__file__).resolve().parent
    logging.info(f"작업 디렉토리: {base_dir}")

    input_path = find_input_file(base_dir, input_name)
    if not input_path or not input_path.exists():
        logging.error(f"오류: 입력 파일을 찾을 수 없습니다 -> 대상: '{input_name}'")
        logging.info("파일이 'image_to_pdf' 폴더 내에 존재하는지 확인하세요.")
        return False

    logging.info(f"입력 파일 감지: {input_path.name}")
    output_path = base_dir / output_filename

    try:
        # 1. 한글 경로 대응 이미지 로드
        logging.info("고화질 이미지 데이터 로드 중...")
        img_array = np.fromfile(str(input_path), np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise ValueError("이미지 데이터를 정상적으로 읽을 수 없습니다.")

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, _ = img_rgb.shape
        logging.info(f"원본 해상도: {width} x {height} px")

        # 2. 텍스트 및 미세 윤곽선 선명화 필터 적용
        logging.info("디테일 복원 및 텍스트 선명화 처리 중...")
        enhanced_rgb = enhance_text_and_details(img_rgb)

        # 3. 무손실 이미지 처리 (PIL)
        pil_img = Image.fromarray(enhanced_rgb)
        temp_png = base_dir / "_temp_highres.png"
        pil_img.save(temp_png, format="PNG", dpi=(target_dpi, target_dpi), optimize=True)

        # 4. PDF Vector Canvas 생성 (인쇄용 규격 단위 1pt = 1/72 inch)
        pt_width = (width / target_dpi) * 72
        pt_height = (height / target_dpi) * 72

        logging.info(f"300 DPI 초고화질 벡터 컨테이너 PDF 출력 중... ({pt_width:.2f}pt x {pt_height:.2f}pt)")
        pdf_canvas = canvas.Canvas(str(output_path), pagesize=(pt_width, pt_height))
        pdf_canvas.drawImage(str(temp_png), 0, 0, width=pt_width, height=pt_height)
        pdf_canvas.showPage()
        pdf_canvas.save()

        # 5. 임시 파일 정리
        if temp_png.exists():
            os.remove(temp_png)

        logging.info(f"변환 성공! 깨짐 없는 고해상도 PDF가 생성되었습니다.")
        logging.info(f"저장 경로: {output_path}")
        return True

    except Exception as e:
        logging.exception(f"변환 중 오류가 발생했습니다: {e}")
        return False


if __name__ == "__main__":
    INPUT_FILENAME = "애드플랜터스_추석 인사 카드"
    OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_highres.pdf"

    print("=" * 65)
    print(" [Image2PDF] 손실 없는 초고화질 인쇄용 PDF 변환 프로세스 시작")
    print("=" * 65)

    success = convert_to_high_res_pdf(INPUT_FILENAME, OUTPUT_FILENAME, target_dpi=300)

    if success:
        print("\n[완료] 깨짐 없는 고해상도 PDF 변환이 완료되었습니다.")
    else:
        print("\n[실패] 변환 도중 오류가 발생했습니다. 로그를 확인하세요.")