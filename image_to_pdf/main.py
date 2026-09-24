"""
=============================================================================
[애드플랜터스 추석 인사 카드 - 픽셀 수정 및 강아지 '고리' 이름 추가 스크립트]
실행 환경: VS Code Tunnel / GitHub Public Repository (image_to_pdf 폴더 내)
필요 패키지: pip install pymupdf Pillow opencv-python numpy
=============================================================================
"""

import os
import sys
import logging
import math
from pathlib import Path

# 로깅 설정 (터미널에서 진행 상황 확인)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    import fitz  # PyMuPDF: 고해상도 PDF 렌더링 용도
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np
except ImportError:
    logging.error("필수 패키지가 설치되지 않았습니다.")
    logging.error("터미널에서 다음을 실행하세요: pip install pymupdf Pillow opencv-python numpy")
    sys.exit(1)


# =============================================================================
# 1. 경로 및 파일 설정 (절대 경로 기반 상대 위치)
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
INPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_highres.pdf"
OUTPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_고리추가_완성.pdf"

# 손글씨 폰트 파일명 (현재 폴더에 위치해야 함, 없으면 기본 폰트 사용)
FONT_FILENAME = "NanumPen.ttf" 
FONT_PATH = BASE_DIR / FONT_FILENAME

# =============================================================================
# 2. 이미지 처리 및 드로잉 함수
# =============================================================================

def fix_pixel_glitches(image: Image.Image) -> Image.Image:
    """
    OpenCV를 사용하여 빨간 박스로 표시된 부분의 픽셀 엇나감을 자연스럽게 연결(Inpainting)합니다.
    """
    logging.info("어색한 픽셀 경계면 인페인팅(보정) 처리 중...")
    
    # PIL Image -> OpenCV Image(NumPy 배열)로 변환
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = cv_img.shape[:2]
    
    # 수정을 위한 빈 마스크 생성
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # [수정 영역 1] 오른쪽 하단 노트북/손 부근 픽셀 엇나감 (상대 좌표 기반)
    # 이미지 비율에 맞춰 영역(x, y, width, height) 설정
    x1, y1 = int(w * 0.77), int(h * 0.78)
    x2, y2 = int(w * 0.85), int(h * 0.82)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)
    
    # [수정 영역 2] 하단 테이블 다리 부근 픽셀 엇나감 (상대 좌표 기반)
    x3, y3 = int(w * 0.68), int(h * 0.88)
    x4, y4 = int(w * 0.73), int(h * 0.94)
    cv2.rectangle(mask, (x3, y3), (x4, y4), 255, thickness=-1)
    
    # OpenCV 인페인팅 적용 (주변 픽셀을 이용해 자연스럽게 채움)
    # 반경(inpaintRadius)을 3으로 주어 너무 뭉개지지 않고 경계만 부드럽게 이어지도록 처리
    repaired_img = cv2.inpaint(cv_img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # OpenCV Image -> PIL Image로 복구
    return Image.fromarray(cv2.cvtColor(repaired_img, cv2.COLOR_BGR2RGB))


def draw_bezier_curve_with_arrow(draw: ImageDraw.Draw, p0, p1, p2, p3, color="white", width=4):
    """
    자연스러운 곡선(베지어 곡선) 화살표를 그립니다. (기존 스타일 통일)
    """
    # 1. 곡선 그리기 (100개의 점으로 분할하여 부드럽게 연결)
    steps = 100
    points = []
    for i in range(steps + 1):
        t = i / steps
        # 3차 베지어 곡선 공식
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
        
    draw.line(points, fill=color, width=width)
    
    # 2. 끝부분(p3)에 화살표 머리(Arrowhead) 그리기
    # 마지막 두 점을 이용해 각도 계산
    dx = points[-1][0] - points[-2][0]
    dy = points[-1][1] - points[-2][1]
    angle = math.atan2(dy, dx)
    
    arrow_length = 20
    arrow_angle = math.pi / 6  # 30도
    
    # 화살표 양 날개 좌표 계산
    left_x = p3[0] - arrow_length * math.cos(angle - arrow_angle)
    left_y = p3[1] - arrow_length * math.sin(angle - arrow_angle)
    
    right_x = p3[0] - arrow_length * math.cos(angle + arrow_angle)
    right_y = p3[1] - arrow_length * math.sin(angle + arrow_angle)
    
    draw.line([p3, (left_x, left_y)], fill=color, width=width)
    draw.line([p3, (right_x, right_y)], fill=color, width=width)


def add_name_and_arrow(image: Image.Image) -> Image.Image:
    """
    강아지 머리 위에 '고리' 텍스트와 화살표를 추가합니다.
    """
    logging.info("손글씨 텍스트 '고리' 및 곡선 화살표 추가 중...")
    draw = ImageDraw.Draw(image)
    w, h = image.size
    
    # 폰트 설정 (기존 이미지 해상도에 맞춰 크기 조정, 약 300DPI 기준)
    font_size = int(h * 0.025) 
    try:
        if FONT_PATH.exists():
            font = ImageFont.truetype(str(FONT_PATH), font_size)
        else:
            logging.warning("지정된 폰트를 찾을 수 없어 기본 폰트를 사용합니다. (한글이 깨질 수 있습니다)")
            font = ImageFont.load_default()
    except Exception as e:
        logging.error(f"폰트 로드 실패: {e}")
        font = ImageFont.load_default()

    # '고리' 텍스트 위치 (시바견 우측 상단 쯤)
    text_x = int(w * 0.85)
    text_y = int(h * 0.77)
    
    # 텍스트 그리기 (흰색)
    draw.text((text_x, text_y), "고리", font=font, fill="white")
    
    # 곡선 화살표 시작점 및 제어점 설정
    # p0: 텍스트 바로 아래
    # p1, p2: 곡선의 휘어짐을 제어하는 점
    # p3: 강아지 머리(끝점)
    p0 = (text_x + int(font_size * 0.5), text_y + font_size + 10)
    p3 = (int(w * 0.83), int(h * 0.86)) # 시바견 머리 위치 부근
    
    # C자 형태로 둥글게 내려가도록 제어점 설정
    p1 = (p0[0] + 50, p0[1] + 50)
    p2 = (p3[0] + 50, p3[1] - 50)
    
    # 곡선 화살표 그리기
    draw_bezier_curve_with_arrow(draw, p0, p1, p2, p3, color="white", width=4)
    
    return image


# =============================================================================
# 3. 메인 실행 함수
# =============================================================================
def main():
    if not INPUT_PDF.exists():
        logging.error(f"입력 PDF 파일이 존재하지 않습니다: {INPUT_PDF}")
        return

    try:
        # 1. 고해상도 렌더링을 위해 PyMuPDF(fitz)로 PDF 열기
        logging.info(f"원본 PDF 로드 중 (고해상도 변환): {INPUT_PDF.name}")
        pdf_document = fitz.open(str(INPUT_PDF))
        page = pdf_document[0] # 첫 번째 페이지
        
        # 300 DPI 수준으로 고해상도 렌더링 (확대 비율 적용)
        zoom = 300 / 72  # PDF 기본 72ppi를 300ppi로 확대
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # PyMuPixmap을 PIL Image로 변환
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 2. 픽셀 오류 수정 (인페인팅)
        img_repaired = fix_pixel_glitches(img)
        
        # 3. '고리' 텍스트 및 스타일 화살표 추가
        img_final = add_name_and_arrow(img_repaired)
        
        # 4. 수정된 고해상도 이미지를 다시 PDF로 저장 (압축 손실 최소화)
        logging.info("최종 결과물을 고해상도 PDF로 저장 중...")
        img_final.save(
            str(OUTPUT_PDF), 
            "PDF", 
            resolution=300.0,
            save_all=True
        )
        
        pdf_document.close()
        
        logging.info(f"✨ 성공적으로 생성되었습니다! 저장 위치: {OUTPUT_PDF.name}")
        logging.info("※ 좌표나 곡선의 위치가 맞지 않는다면, 코드 내 상대 좌표(0.0 ~ 1.0) 수치를 조금씩 조절해 보세요.")
        
    except Exception as e:
        logging.error(f"작업 중 예기치 않은 오류가 발생했습니다: {e}", exc_info=True)


if __name__ == "__main__":
    main()