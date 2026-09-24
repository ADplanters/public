"""
main.py
- 실행 환경: GitHub public 레포지토리의 `image_to_pdf` 폴더 내부
- 기능: 첨부된 'curved arrow.jpg' 이미지를 고해상도 PDF로 변환 및 자동 품질 보정
"""

import sys
import logging
from pathlib import Path
from PIL import Image, ImageEnhance

# ---------------------------------------------------------
# 1. 로깅 설정 (실시간 진행 상황 출력)
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ---------------------------------------------------------
# 2. 이미지 보정 로직
# ---------------------------------------------------------
def apply_natural_enhancement(img: Image.Image) -> Image.Image:
    """
    이미지의 선명도(Sharpness)와 대비(Contrast)를 자연스럽게 보정합니다.
    """
    try:
        # 선명도 1.5배 향상
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(1.5)
        
        # 대비 1.1배 향상
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.1)
        
        logging.info("이미지 자동 보정(선명도 1.5x, 대비 1.1x) 완료")
        return img
    except Exception as e:
        logging.error(f"이미지 보정 중 오류 발생: {e}")
        raise

# ---------------------------------------------------------
# 3. 메인 변환 로직
# ---------------------------------------------------------
def convert_image_to_high_res_pdf(input_filename: str, output_filename: str):
    # 환경 맞춤: 스크립트가 위치한 현재 폴더(image_to_pdf)를 절대 경로로 계산
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / input_filename
    output_path = base_dir / output_filename
    
    logging.info(f"작업 디렉토리: {base_dir}")
    
    # 파일 존재 여부 확인
    if not input_path.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다: {input_path}")
        logging.info(f"실행 환경에 '{input_filename}' 파일이 존재하는지 확인해주세요.")
        return

    try:
        # 리소스 관리: with 문을 사용하여 메모리 누수 방지
        with Image.open(input_path) as img:
            logging.info(f"이미지 로드 성공: 원본 크기 {img.size}, 모드 {img.mode}")
            
            # PDF 저장을 위해 색상 모드 최적화 (RGBA, P 등인 경우 RGB로 변환)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logging.info("PDF 변환을 위해 이미지를 RGB 모드로 변환했습니다.")
            
            # 자동 품질 보정 적용
            enhanced_img = apply_natural_enhancement(img)
            
            # 고해상도 PDF 저장 (dpi=300 이상 보장, 최고 품질)
            logging.info(f"고해상도 PDF 생성을 시작합니다...")
            enhanced_img.save(
                output_path,
                "PDF",
                resolution=300.0,
                quality=100,
                save_all=True
            )
            
            logging.info(f"고해상도 PDF 생성 완료! 저장 위치: {output_path}")

    except MemoryError:
        logging.error("메모리가 부족합니다. 이미지가 너무 크거나 시스템 리소스가 부족할 수 있습니다.")
    except PermissionError:
        logging.error(f"파일 저장 권한이 없습니다: {output_path}")
    except OSError as e:
        logging.error(f"파일 입출력(OS) 오류가 발생했습니다: {e}")
    except Exception as e:
        logging.error(f"PDF 변환 중 예기치 않은 오류가 발생했습니다: {e}")

# ---------------------------------------------------------
# 4. 실행부
# ---------------------------------------------------------
if __name__ == "__main__":
    # 타겟 파일명 설정
    INPUT_IMAGE_NAME = "curved arrow.jpg"
    OUTPUT_PDF_NAME = "output.pdf"
    
    convert_image_to_high_res_pdf(INPUT_IMAGE_NAME, OUTPUT_PDF_NAME)