# main.py
import os
import sys
import logging
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

# ==========================================
# 1. 로깅 및 환경 설정
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 경로 설정 (현재 스크립트가 위치한 image_to_pdf 폴더 기준 절대 경로 유도)
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = BASE_DIR / "optimized_high_res_output.pdf"

# 처리할 파일 기본 이름 배열 (확장자는 jpg 또는 png 자동 탐색)
FILE_BASE_NAME = "네이버 플레이스 순위상승의 핵심, 리뷰 쌓는 법 Q&A (영수증 리뷰 vs 블로그 리뷰) ({})"
FILE_COUNT = 7

# ==========================================
# 2. 유틸리티 함수: 한글 경로 이미지 안전 로드 (Windows 환경 예외 처리)
# ==========================================
def read_image_safely(file_path):
    try:
        # cv2.imread는 경로에 한글이 포함될 경우 에러가 발생하므로 numpy를 거쳐 디코딩합니다.
        with open(file_path, "rb") as stream:
            bytes_array = bytearray(stream.read())
            np_array = np.asarray(bytes_array, dtype=np.uint8)
            cv_img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            return cv_img
    except Exception as e:
        logger.error(f"이미지 로드 중 오류 발생: {file_path} - {e}")
        return None

# ==========================================
# 3. 유틸리티 함수: 시스템 폰트 안전 로드 (텍스트 및 레이아웃 요구사항)
# ==========================================
def get_system_fallback_font(font_size=20):
    """OS별 기본 폰트를 안전하게 로드합니다."""
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",       # Windows 맑은 고딕
        "/System/Library/Fonts/AppleGothic.ttf", # Mac 애플 고딕
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf", # Linux 나눔고딕
        "arial.ttf" # Fallback
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, font_size)
        except IOError:
            continue
    # 폰트를 찾을 수 없는 경우 Pillow 기본 폰트 사용
    return ImageFont.load_default()

# ==========================================
# 4. 코어 로직: 우측 하단 별모양 자국(워터마크) 제거 및 복원
# ==========================================
def remove_transparent_mark(cv_img):
    """
    우측 하단 영역(ROI)을 지정하여 반투명 흰색 자국을 제거하고 텍스트를 복원합니다.
    """
    h, w = cv_img.shape[:2]
    
    # 우측 하단 ROI 영역 설정 (전체 너비의 우측 30%, 하단 20%)
    roi_x, roi_y = int(w * 0.70), int(h * 0.80)
    roi = cv_img[roi_y:h, roi_x:w]
    
    # 그레이스케일 변환 및 CLAHE(대비 제한 적응형 히스토그램 평활화) 적용
    # -> 흰색 반투명 자국으로 인해 흐려진 텍스트의 대비를 극대화하여 복원
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced_roi = clahe.apply(gray_roi)
    
    # 밝은 색(흰색 워터마크) 마스킹 처리 후 인페인팅 적용
    # 텍스트(검은색)는 보호하고 밝은 영역(별모양)을 주변 픽셀로 덮어씌움
    _, mask = cv2.threshold(gray_roi, 230, 255, cv2.THRESH_BINARY)
    inpainted_roi = cv2.inpaint(roi, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # CLAHE 처리된 텍스트와 인페인팅 결과를 합성 (텍스트 선명도 유지)
    # OpenCV 이미지를 다시 BGR 형태로 맞춤
    enhanced_roi_bgr = cv2.cvtColor(enhanced_roi, cv2.COLOR_GRAY2BGR)
    final_roi = cv2.addWeighted(inpainted_roi, 0.6, enhanced_roi_bgr, 0.4, 0)
    
    # 원본 이미지에 ROI 덮어쓰기
    result_img = cv_img.copy()
    result_img[roi_y:h, roi_x:w] = final_roi
    
    # Pillow Image 형식으로 변환 (BGR -> RGB)
    rgb_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_img)

# ==========================================
# 5. 코어 로직: 고해상도 이미지 보정 및 레이아웃 텍스트 추가
# ==========================================
def enhance_and_layout(pil_img, page_num):
    """이미지의 선명도, 대비를 자동 보정하고 하단 중앙에 페이지 번호를 삽입합니다."""
    # 1. 자동 보정 (선명도, 대비, 색상)
    enhancer = ImageEnhance.Sharpness(pil_img)
    img = enhancer.enhance(2.0) # 선명도 대폭 향상 (인쇄용)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.15) # 텍스트 가독성을 위한 대비 증가
    
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.05) # 색조 미세 보정

    # 2. 정밀한 텍스트 및 레이아웃 추가 (요구사항 충족)
    draw = ImageDraw.Draw(img)
    font = get_system_fallback_font(font_size=24)
    text = f"- {page_num} -"
    
    # 하단 중앙 텍스트 좌표 자동 계산
    img_w, img_h = img.size
    # 최신 Pillow 버전의 텍스트 바운딩 박스 계산
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # 구버전 Pillow 폴백
        text_w, text_h = draw.textsize(text, font=font)
        
    x = (img_w - text_w) / 2
    y = img_h - text_h - 40 # 하단에서 40px 위로 배치
    
    # 텍스트에 약간의 반투명 배경(그림자) 효과를 주어 자연스럽게 합성
    draw.rectangle([x-10, y-5, x+text_w+10, y+text_h+5], fill=(255, 255, 255, 180))
    draw.text((x, y), text, font=font, fill=(50, 50, 50))
    
    return img

# ==========================================
# 6. 메인 실행 함수
# ==========================================
def main():
    logger.info("이미지 로드 및 보정 작업을 시작합니다...")
    processed_images = []

    for i in range(1, FILE_COUNT + 1):
        target_name = FILE_BASE_NAME.format(i)
        
        # 확장자 자동 탐색 (jpg, png)
        file_path = None
        for ext in [".jpg", ".png", ".jpeg"]:
            candidate = BASE_DIR / f"{target_name}{ext}"
            if candidate.exists():
                file_path = candidate
                break
                
        if not file_path:
            logger.warning(f"파일을 찾을 수 없습니다, 건너뜁니다: {target_name}")
            continue

        logger.info(f"[{i}/{FILE_COUNT}] 파일 처리 중: {file_path.name}")
        
        try:
            # 1. 이미지 로드 (한글 경로 대응)
            cv_img = read_image_safely(str(file_path))
            if cv_img is None:
                continue

            # 2. 워터마크(별모양 자국) 제거 및 텍스트 복원
            pil_img = remove_transparent_mark(cv_img)

            # 3. 이미지 보정 및 페이지 레이아웃 삽입
            final_img = enhance_and_layout(pil_img, page_num=i)
            
            # 리소스 관리를 위해 메모리 할당 유지
            processed_images.append(final_img)
            
        except Exception as e:
            logger.error(f"이미지 {target_name} 처리 중 치명적 오류 발생: {e}")

    # ==========================================
    # 7. 고해상도 PDF 저장 (메모리 누수 방지 및 리소스 관리)
    # ==========================================
    if processed_images:
        try:
            logger.info("고해상도 PDF 생성을 시작합니다...")
            # 고해상도 유지를 위해 resolution 및 quality 옵션 세팅
            processed_images[0].save(
                OUTPUT_PDF,
                "PDF",
                resolution=300.0,
                save_all=True,
                append_images=processed_images[1:],
                quality=100
            )
            logger.info(f"✅ PDF가 성공적으로 저장되었습니다: {OUTPUT_PDF}")
        except Exception as e:
            logger.error(f"PDF 저장 중 오류 발생: {e}")
        finally:
            # 리소스 정리 (명시적 메모리 릴리즈)
            for img in processed_images:
                img.close()
    else:
        logger.error("처리된 이미지가 없어 PDF를 생성하지 못했습니다.")

if __name__ == "__main__":
    main()