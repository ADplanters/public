import os
import sys
import logging
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas

# 진행 상황 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def convert_raster_to_vector_pdf(input_filename: str, output_filename: str, k_colors: int = 24) -> bool:
    """
    라스터 이미지(PNG)를 분석하여 벡터 도형 패스(Path)로 변환한 뒤 고해상도 PDF로 저장합니다.
    
    :param input_filename: 입력 PNG 파일명
    :param output_filename: 출력 PDF 파일명
    :param k_colors: 추출할 대표 색상 수 (높을수록 원본 이미지와 가까운 디테일 표현)
    """
    # 1. 안전한 상대 경로 계산 (GitHub 레포 및 터널 환경 대응)
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / input_filename
    output_path = base_dir / output_filename

    logging.info(f"기준 디렉토리: {base_dir}")
    logging.info(f"입력 파일 검색: {input_path}")

    if not input_path.exists():
        logging.error(f"오류: 입력 파일이 존재하지 않습니다 -> {input_path}")
        logging.info("파일이 'image_to_pdf' 폴더 내에 정확히 위치해 있는지 확인하세요.")
        return False

    try:
        # 2. 이미지 읽기 (한글 경로 호환성을 위해 np.fromfile + cv2.imdecode 사용)
        logging.info("이미지 데이터를 로드하는 중...")
        img_array = np.fromfile(str(input_path), np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            raise ValueError("이미지를 디코딩할 수 없습니다. 올바른 이미지 파일인지 확인하세요.")

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        height, width, _ = img_rgb.shape
        logging.info(f"원본 이미지 해상도: {width} x {height} px")

        # 3. K-Means 색상 양자화 (컬러 벡터 영역 분할)
        logging.info(f"색상 벡터화 처리 중 (대표 색상 {k_colors}개 추출)...")
        pixel_data = img_rgb.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixel_data, k_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)
        quantized_labels = labels.reshape((height, width))

        # 4. ReportLab PDF 캔버스 생성 (1:1 포인트 벡터 캔버스)
        pt_width = float(width)
        pt_height = float(height)
        
        logging.info("고해상도 벡터 PDF 캔버스 생성 중...")
        pdf_canvas = canvas.Canvas(str(output_path), pagesize=(pt_width, pt_height))

        total_paths = 0

        # 5. 각 색상 레이어별 윤곽선(Contour) 추출 및 벡터 경로 렌더링
        for i in range(k_colors):
            color = centers[i]
            r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

            # 해당 색상 영역 마스크 생성
            mask = np.uint8(quantized_labels == i) * 255
            
            # 노이즈 필터링
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # 윤곽선 검출
            contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            pdf_canvas.setFillColorRGB(r, g, b)
            pdf_canvas.setStrokeColorRGB(r, g, b)

            for cnt in contours:
                # 작은 노이즈 제거
                if cv2.contourArea(cnt) < 3:
                    continue

                # 벡터 경로 다각형 단순화 및 곡선 정밀화
                epsilon = 0.0008 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                if len(approx) < 3:
                    continue

                # PDF 벡터 Path 생성
                path = pdf_canvas.beginPath()
                
                # ReportLab 캔버스는 좌하단이 (0,0) 원점이므로 Y축 반전
                start_x = float(approx[0][0][0])
                start_y = float(pt_height - approx[0][0][1])
                path.moveTo(start_x, start_y)

                for pt in approx[1:]:
                    x = float(pt[0][0])
                    y = float(pt_height - pt[0][1])
                    path.lineTo(x, y)

                path.close()
                pdf_canvas.drawPath(path, fill=1, stroke=1)
                total_paths += 1

        # 6. PDF 저장 및 리소스 해제
        pdf_canvas.showPage()
        pdf_canvas.save()

        logging.info(f"변환 성공! 총 {total_paths}개의 벡터 패스가 PDF에 생성되었습니다.")
        logging.info(f"저장된 파일: {output_path}")
        return True

    except Exception as e:
        logging.exception(f"변환 도중 오류가 발생했습니다: {e}")
        return False


if __name__ == "__main__":
    INPUT_FILENAME = "애드플랜터스_추석 인사 카드.png"
    OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_vector.pdf"

    print("=" * 65)
    print(" [Image2PDF] 이미지 -> 고해상도 벡터 PDF 변환 프로세스 시작")
    print("=" * 65)

    success = convert_raster_to_vector_pdf(INPUT_FILENAME, OUTPUT_FILENAME, k_colors=24)

    if success:
        print("\n[완료] 벡터 PDF 변환이 정상적으로 종료되었습니다.")
    else:
        print("\n[실패] 변환 도중 오류가 발생했습니다. 로그 메시지를 확인하세요.")