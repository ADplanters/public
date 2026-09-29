import os
import cv2
import numpy as np
import svgwrite
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# 파일 경로
input_image_path = 'Slice 1.png'
output_svg_path = 'output_vector.svg'
output_pdf_path = 'output_vector.pdf'

def run_safe_vectorization():
    if not os.path.exists(input_image_path):
        print(f"[오류] '{input_image_path}' 파일이 없습니다.")
        return

    print("1/4 이미지 로드 및 AI 색상 분석 중 (K-Means 연산)...")
    img = cv2.imread(input_image_path)
    
    # 픽셀 노이즈를 없애기 위해 이미지의 색상을 16가지로 압축 및 정돈
    K = 16 
    Z = img.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    center = np.uint8(center)
    res = center[label.flatten()]
    simplified_img = res.reshape((img.shape))
    
    print("2/4 이미지 경계선 추적 및 선형 백터화(Vector Path) 조립 중...")
    h, w = img.shape[:2]
    dwg = svgwrite.Drawing(output_svg_path, size=(w, h), profile='tiny')
    
    all_contours = []
    
    # 색상별로 분리하여 선형 다각형을 추출
    for i in range(K):
        color = center[i]
        mask = cv2.inRange(simplified_img, color, color)
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # BGR -> HEX 컬러(웹/백터 색상) 변환
        hex_color = "#{:02x}{:02x}{:02x}".format(color[2], color[1], color[0])
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= 2:  # 자잘한 픽셀 찌꺼기 제거
                # 선형 근사화 (곡선과 직선을 수학적 좌표로 변환)
                epsilon = 0.0015 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                
                if len(approx) > 2:
                    all_contours.append({
                        'area': area,
                        'path': approx,
                        'color': hex_color
                    })

    # 큰 덩어리(배경)를 먼저 그리고, 그 위에 작은 글씨들이 겹쳐지도록 면적순 정렬
    all_contours.sort(key=lambda x: x['area'], reverse=True)

    print("3/4 무한 확대 가능한 SVG 파일 작성 중...")
    for item in all_contours:
        approx = item['path']
        # M(시작) L(선 긋기) Z(닫기)의 벡터 패스 명령어 생성
        path_data = "M " + " L ".join([f"{p[0][0]},{p[0][1]}" for p in approx]) + " Z"
        dwg.add(dwg.path(d=path_data, fill=item['color'], stroke="none"))
        
    dwg.save()
    print(f"  -> '{output_svg_path}' 파일 생성 완료")
    
    print("4/4 최종 백터 PDF 출력 중...")
    try:
        drawing = svg2rlg(output_svg_path)
        renderPDF.drawToFile(drawing, output_pdf_path)
        print(f"\n⭐ 성공! 해상도 무제한의 백터 PDF가 생성되었습니다: {output_pdf_path}")
    except Exception as e:
        print(f"\n[알림] PDF 변환 오류 발생: {e}")
        print(f"대신 생성된 '{output_svg_path}' 파일을 웹 브라우저나 일러스트레이터로 열어보세요.")

if __name__ == "__main__":
    run_safe_vectorization()