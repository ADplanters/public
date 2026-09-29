import cv2
import numpy as np
from fpdf import FPDF
import os

# 1. 파일 이름 설정
input_image_path = 'image_0.png'  # 원본 이미지 파일명
output_pdf_path = 'high_res_image_pdf.pdf'  # 출력 PDF 파일명
model_path = 'fsrcnn_x4.pb'  # 다운로드한 초해상도 모델 파일명
temp_image_path = 'temp_upscaled_image.png'  # 임시 이미지 파일명

# 2. 초해상도 모델 설정 및 이미지 업스케일링
def upscale_image_dnn(input_path, output_path, model_path_local):
    print(f"이미지 업스케일링 시작: {input_path}...")
    
    # 이미지 로드
    image = cv2.imread(input_path)
    if image is None:
        print(f"에러: 이미지를 불러올 수 없습니다. 경로를 확인하세요: {input_path}")
        return False

    # 초해상도 인스턴스 생성 및 모델 로드
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path_local)
    
    # 모델 이름 및 배율 설정
    model_name = "fsrcnn" # FSRCNN_x4.pb 모델 이름
    scale = 4 # FSRCNN_x4.pb 배율

    sr.setModel(model_name, scale)

    # 이미지 업스케일링
    result = sr.upsample(image)
    
    # 결과 이미지 저장
    cv2.imwrite(output_path, result)
    print(f"이미지 업스케일링 완료: {output_path} (4x)")
    return True

# 3. PDF 생성 및 이미지 추가
def create_pdf_from_image(input_image, output_pdf):
    print(f"PDF 생성 시작: {output_pdf}...")
    
    # 이미지 크기 가져오기
    image = cv2.imread(input_image)
    height, width, channels = image.shape
    
    # PDF 인스턴스 생성 (이미지 크기에 맞게 A4 등 설정)
    pdf = FPDF(unit = "pt", format = [width, height]) # 포인트 단위, 이미지 크기
    pdf.add_page()
    
    # 이미지를 PDF 페이지 전체 크기로 추가
    pdf.image(input_image, 0, 0, width, height)
    
    # PDF 저장
    pdf.output(output_pdf)
    print(f"PDF 생성 완료: {output_pdf}")

# --- 메인 실행 ---
if __name__ == "__main__":
    # 모델 파일 존재 확인
    if not os.path.exists(model_path):
        print(f"에러: 초해상도 모델 파일을 찾을 수 없습니다. '{model_path}' 파일을 프로젝트 폴더에 저장해주세요.")
        exit()

    # 원본 이미지 파일 존재 확인
    if not os.path.exists(input_image_path):
        print(f"에러: 원본 이미지 파일을 찾을 수 없습니다. '{input_image_path}' 파일을 프로젝트 폴더에 저장해주세요.")
        exit()

    # 이미지 업스케일링 실행
    if upscale_image_dnn(input_image_path, temp_image_path, model_path):
        # PDF 생성 실행
        create_pdf_from_image(temp_image_path, output_pdf_path)
        
        # 임시 파일 삭제
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            print(f"임시 파일 삭제 완료: {temp_image_path}")
        
        print("모든 작업이 완료되었습니다. 고해상도 PDF 파일을 확인하세요.")
    else:
        print("이미지 업스케일링에 실패하여 PDF 생성을 중단합니다.")