"""
=============================================================================
의존성 라이브러리 설치:
pip install opencv-python numpy reportlab pillow python-dotenv
=============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageFont
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 존재하는 경우)
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
# 안전한 시스템 폰트 로더 (Fallback)
# ---------------------------------------------------------------------------
def load_system_font(font_size: int = 16) -> ImageFont.FreeTypeFont:
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
# 비트맵 -> 100% 벡터 패스(Vector Path) 트레이싱 변환 엔진
# ---------------------------------------------------------------------------
def convert_raster_to_vector_pdf(
    image_path: Path,
    output_pdf_path: Path,
    num_colors: int = 12,
    smoothing_epsilon: float = 0.0008
) -> bool:
    """
    비트맵 이미지(PNG/JPG)의 색상 및 윤곽선(Contour)을 정밀 추출하여
    ReportLab 캔버스 상에 깨짐 없는 벡터 곡선(Vector Path)으로 직접 렌더링합니다.
    """
    if not image_path.exists():
        logging.error(f"파일을 찾을 수 없습니다: {image_path.name}")
        return False

    try:
        # OpenCV로 이미지 로드 및 노이즈 제거 프리프로세싱
        img = cv2.imread(str(image_path))
        if img is None:
            logging.error(f"이미지 디코딩 실패: {image_path.name}")
            return False

        h, w, c = img.shape

        # 1. K-Means 클러스터링 기반 주요 색상 및 레이어 양자화
        data = img.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.8)
        _, labels, centers = cv2.kmeans(data, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        labels_grid = labels.reshape((h, w))

        # ReportLab PDF 캔버스 생성 (포인트 1:1 디바이스 인디펜던트 벡터 좌표계)
        pdf_canvas = canvas.Canvas(str(output_pdf_path), pagesize=(w, h))

        # 2. 색상 레이어별 윤곽선(Contour) 트레이싱 및 벡터 그리기
        for idx, center_color in enumerate(centers):
            b, g, r = center_color
            fill_r, fill_g, fill_b = r / 255.0, g / 255.0, b / 255.0

            # 특정 색상 마스크 영역 생성
            mask = np.where(labels_grid == idx, 255, 0).astype(np.uint8)

            # 모폴로지 연산으로 텍스트 및 경계선 유격 메우기
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # 윤곽선 계층 구조 탐색 (외부 경계 및 내부 홀 처리)
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

            if contours is None or len(contours) == 0:
                continue

            pdf_canvas.setFillColorRGB(fill_r, fill_g, fill_b)
            pdf_canvas.setStrokeColorRGB(fill_r, fill_g, fill_b)

            path = pdf_canvas.beginPath()

            for i, contour in enumerate(contours):
                if cv2.contourArea(contour) < 2.0:  # 극소 미세 잡음 제거
                    continue

                # 윤곽선 자간 및 매끄러움 곡선 근사화 (approxPolyDP)
                arc_len = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, smoothing_epsilon * arc_len, True)

                if len(approx) < 2:
                    continue

                # OpenCV(Top-Left 기준) 좌표계를 ReportLab(Bottom-Left 기준) 좌표계로 변환
                start_pt = approx[0][0]
                path.moveTo(float(start_pt[0]), float(h - start_pt[1]))

                for pt in approx[1:]:
                    px, py = pt[0]
                    path.lineTo(float(px), float(h - py))

                path.close()

            # 벡터 패스 렌더링
            pdf_canvas.drawPath(path, fill=1, stroke=0)

        pdf_canvas.save()
        logging.info(f"[벡터 PDF 완료] {image_path.name} -> {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[벡터 변환 실패] {image_path.name}: {e}")
        return False

# ---------------------------------------------------------------------------
# 전체 합본 PDF 생성
# ---------------------------------------------------------------------------
def create_combined_vector_pdf(image_paths: List[Path], output_pdf_path: Path) -> bool:
    """
    모든 이미지를 순서대로 트레이싱하여 단일 합본 벡터 PDF로 변환합니다.
    """
    try:
        if not image_paths:
            return False

        # 첫 번째 파일 규격으로 대표 캔버스 생성
        first_img = cv2.imread(str(image_paths[0]))
        h, w, _ = first_img.shape

        pdf_canvas = canvas.Canvas(str(output_pdf_path), pagesize=(w, h))

        for idx, img_path in enumerate(image_paths):
            img = cv2.imread(str(img_path))
            if img is None:
                continue

            curr_h, curr_w, _ = img.shape
            if idx > 0:
                pdf_canvas.setPageSize((curr_w, curr_h))

            # 이미지 색상 레이어 K-Means 트레이싱
            data = img.reshape((-1, 3)).astype(np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.8)
            _, labels, centers = cv2.kmeans(data, 12, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            centers = np.uint8(centers)
            labels_grid = labels.reshape((curr_h, curr_w))

            for c_idx, center_color in enumerate(centers):
                b, g, r = center_color
                mask = np.where(labels_grid == c_idx, 255, 0).astype(np.uint8)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

                contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    continue

                pdf_canvas.setFillColorRGB(r / 255.0, g / 255.0, b / 255.0)
                pdf_canvas.setStrokeColorRGB(r / 255.0, g / 255.0, b / 255.0)

                path = pdf_canvas.beginPath()
                for contour in contours:
                    if cv2.contourArea(contour) < 2.0:
                        continue
                    approx = cv2.approxPolyDP(contour, 0.0008 * cv2.arcLength(contour, True), True)
                    if len(approx) < 2:
                        continue

                    path.moveTo(float(approx[0][0][0]), float(curr_h - approx[0][0][1]))
                    for pt in approx[1:]:
                        path.lineTo(float(pt[0][0]), float(curr_h - pt[0][1]))
                    path.close()

                pdf_canvas.drawPath(path, fill=1, stroke=0)

            pdf_canvas.showPage()  # 다음 페이지로 이동

        pdf_canvas.save()
        logging.info(f"[합본 벡터 PDF 완료] {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.error(f"[합본 변환 오류]: {e}")
        return False

# ---------------------------------------------------------------------------
# 메인 실행 함수
# ---------------------------------------------------------------------------
def main():
    # 현재 실행 스크립트 위치 기준 경로 설정
    base_dir = Path(__file__).parent.resolve()
    slice_names = [f"Slice {i}.png" for i in range(1, 7)]
    valid_images: List[Path] = []

    logging.info("==========================================")
    logging.info(" 고화질 벡터(Vector) 트레이싱 PDF 변환 시작")
    logging.info("==========================================")

    for name in slice_names:
        img_path = base_dir / name
        if img_path.exists():
            pdf_path = base_dir / f"{img_path.stem}.pdf"
            if convert_raster_to_vector_pdf(img_path, pdf_path):
                valid_images.append(img_path)
        else:
            logging.warning(f"파일이 존재하지 않습니다: {name}")

    if valid_images:
        combined_pdf_path = base_dir / "Slice_All_Combined.pdf"
        create_combined_vector_pdf(valid_images, combined_pdf_path)

    logging.info("==========================================")
    logging.info(" 모든 작업이 완벽하게 완료되었습니다.")
    logging.info("==========================================")

if __name__ == "__main__":
    main()