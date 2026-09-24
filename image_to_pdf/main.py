# Required Dependencies:
# pip install opencv-python reportlab pillow numpy

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
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

def enhance_details(img_rgb: np.ndarray) -> np.ndarray:
    """
    텍스트 및 미세한 윤곽선 선명도를 업스케일링/샤프닝하는 보정 함수 (언샤프 마스킹)
    """
    gaussian_blur = cv2.GaussianBlur(img_rgb, (0, 0), 2.0)
    sharpened = cv2.addWeighted(img_rgb, 1.4, gaussian_blur, -0.4, 0)
    return sharpened

def create_framed_high_res_pdf(input_name: str, target_dpi: int = 300, padding_ratio: float = 0.08) -> bool:
    """
    이미지를 보정한 뒤, 넓은 흰색 캔버스(도화지) 위에 올려 프레임 효과를 주고
    겹치지 않는 타임스탬프 파일명의 300 DPI 고해상도 PDF로 저장합니다.
    """
    base_dir = Path(__file__).resolve().parent
    logging.info(f"작업 디렉토리: {base_dir}")

    input_path = find_input_file(base_dir, input_name)
    if not input_path or not input_path.exists():
        logging.error(f"오류: 입력 파일을 찾을 수 없습니다 -> 대상: '{input_name}'")
        logging.info("파일이 'image_to_pdf' 폴더 내에 존재하는지 확인하세요.")
        return False

    logging.info(f"입력 파일 감지: {input_path.name}")
    
    # 겹치지 않는 새로운 파일명 생성 (타임스탬프 활용)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"애드플랜터스_추석_인사_카드_framed_{timestamp}.pdf"
    output_path = base_dir / output_filename

    try:
        # 1. 이미지 로드 (한글 경로 지원)
        logging.info("고화질 이미지 데이터 로드 중...")
        img_array = np.fromfile(str(input_path), np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise ValueError("이미지 데이터를 디코딩할 수 없습니다.")

        # RGB 변환 및 디테일 보정
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        logging.info("텍스트 가독성 및 디테일 보정 처리 중...")
        enhanced_rgb = enhance_details(img_rgb)

        # 2. Pillow를 이용한 넓은 흰색 도화지(캔버스) 프레임 추가
        logging.info(f"넓은 흰색 도화지(여백 비율: {padding_ratio*100}%) 프레임 생성 중...")
        original_pil = Image.fromarray(enhanced_rgb)
        orig_w, orig_h = original_pil.size
        
        # 프레임이 추가된 새 캔버스 사이즈 계산
        pad_x = int(orig_w * padding_ratio)
        pad_y = int(orig_h * padding_ratio)
        new_w = orig_w + (pad_x * 2)
        new_h = orig_h + (pad_y * 2)

        # 흰색 배경 캔버스 생성 후 원본 이미지 중앙에 부착
        framed_img = Image.new("RGB", (new_w, new_h), "white")
        framed_img.paste(original_pil, (pad_x, pad_y))

        # 3. 고해상도 무손실 임시 파일 저장
        temp_png = base_dir / f"_temp_framed_{timestamp}.png"
        framed_img.save(temp_png, format="PNG", dpi=(target_dpi, target_dpi), optimize=True)

        # 4. PDF Vector Canvas 생성 (인쇄용 규격 단위 1pt = 1/72 inch)
        pt_width = (new_w / target_dpi) * 72
        pt_height = (new_h / target_dpi) * 72

        logging.info(f"300 DPI 고해상도 PDF 생성 중... ({pt_width:.2f}pt x {pt_height:.2f}pt)")
        pdf_canvas = canvas.Canvas(str(output_path), pagesize=(pt_width, pt_height))
        pdf_canvas.drawImage(str(temp_png), 0, 0, width=pt_width, height=pt_height)
        pdf_canvas.showPage()
        pdf_canvas.save()

        # 5. 리소스 및 임시 파일 정리
        if temp_png.exists():
            os.remove(temp_png)

        logging.info(f"변환 성공! 흰색 캔버스가 깔린 고해상도 PDF가 생성되었습니다.")
        logging.info(f"저장 경로: {output_path}")
        return True

    except Exception as e:
        logging.exception(f"변환 도중 오류가 발생했습니다: {e}")
        # 예외 발생 시 생성된 임시 파일이 있다면 강제 삭제
        temp_cleanup = base_dir / f"_temp_framed_{timestamp}.png"
        if temp_cleanup.exists():
            os.remove(temp_cleanup)
        return False


if __name__ == "__main__":
    INPUT_FILENAME = "애드플랜터스_추석 인사 카드"

    print("=" * 65)
    print(" [Image2PDF] 흰색 도화지 프레임 적용 & 고해상도 PDF 변환 시작")
    print("=" * 65)

    # padding_ratio=0.08 은 원본 대비 8% 두께의 액자(여백)를 생성한다는 의미입니다.
    success = create_framed_high_res_pdf(INPUT_FILENAME, target_dpi=300, padding_ratio=0.08)

    if success:
        print("\n[완료] 포스터 형식의 깔끔한 고해상도 PDF가 생성되었습니다.")
    else:
        print("\n[실패] 변환 도중 오류가 발생했습니다. 터미널 로그를 확인하세요.")