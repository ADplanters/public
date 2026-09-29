import os
import vtracer
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

# 파일 경로 설정
input_image_path = 'Slice 1.png'        # 원본 이미지 파일명
output_svg_path = 'output_vector.svg'   # 1차 출력: 벡터 SVG
output_pdf_path = 'output_vector.pdf'   # 2차 출력: 최대해상도 벡터 PDF

def convert_to_vector_pdf():
    if not os.path.exists(input_image_path):
        print(f"[오류] '{input_image_path}' 파일이 폴더에 없습니다. 파일명을 확인해 주세요.")
        return

    print("1/3 이미지 경계선 추적 및 벡터 패스(Bézier Curve) 생성 중...")
    
    # vtracer 엔진을 사용해 비트맵 픽셀을 벡터 패스로 완전 전환
    vtracer.convert_image_to_svg_py(
        input_image_path,
        output_svg_path,
        colormode="color",        # 색상 벡터 보존
        hierarchical="stacked",   # 계층 구조 쌓기 형태
        mode="spline",            # 유기적 곡선(Spline) 모드 적용
        filter_speckle=4,         # 자잘한 픽셀 노이즈 제거
        color_precision=8,        # 정밀 색상 양자화
        layer_difference=16,      # 색상 레이어 분할 임계값
        corner_threshold=60,      # 텍스트 및 도형 코너 감도
        length_threshold=4.0,     # 최소 세그먼트 길이
        max_iterations=10,        # 정밀 반복 연산 횟수
        path_precision=8          # 베지어 곡선 정밀도 (최대 수준)
    )
    print(f"   - 벡터 SVG 파일 생성 완료: {output_svg_path}")

    print("2/3 벡터 SVG를 백터 PDF 엔진으로 변환 중...")
    # SVG 패스를 읽어와 PDF 백터 그래픽으로 렌더링
    drawing = svg2rlg(output_svg_path)
    renderPDF.drawToFile(drawing, output_pdf_path)

    print(f"3/3 완료! 무한 확대 가능한 최고 품질 백터 PDF가 생성되었습니다: '{output_pdf_path}'")

if __name__ == "__main__":
    convert_to_vector_pdf()