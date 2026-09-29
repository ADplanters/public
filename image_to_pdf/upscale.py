import os
import urllib.request
import cv2
from fpdf import FPDF

# 파일 경로 설정
input_image_path = 'Slice 1.png'        # 원본 이미지 파일명
output_pdf_path = 'output_high_res.pdf' # 최종 출력될 PDF 파일명
model_path = 'fsrcnn_x4.pb'             # 초해상도 AI 모델 파일명
temp_image_path = 'temp_upscaled.png'    # 임시 저장 파일명

# AI 모델 다운로드 URL
MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/FSRCNN_x4.pb"

def download_model_if_needed():
    """모델 파일이 없으면 인터넷에서 자동으로 다운로드합니다."""
    if not os.path.exists(model_path):
        print("AI 모델 파일(fsrcnn_x4.pb)을 찾을 수 없어 자동으로 다운로드를 시작합니다...")
        try:
            urllib.request.urlretrieve(MODEL_URL, model_path)
            print("모델 다운로드 완료!")
        except Exception as e:
            print(f"[오류] 모델 다운로드 실패: {e}")

def run_upscale():
    # 1. AI 모델 파일 체크 및 자동 다운로드
    download_model_if_needed()

    # 2. 원본 이미지 존재 여부 점검
    if not os.path.exists(input_image_path):
        print(f"[오류] 원본 이미지 파일('{input_image_path}')이 폴더에 없습니다.")
        return

    # 3. 이미지 로드 및 AI 업스케일링 (4배 확대)
    print("1/3 이미지 고해상도 복원 중... (잠시만 기다려주세요)")
    img = cv2.imread(input_image_path)
    
    if img is None:
        print(f"[오류] '{input_image_path}' 이미지를 읽을 수 없습니다.")
        return

    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel("fsrcnn", 4)
    upscaled = sr.upsample(img)
    
    cv2.imwrite(temp_image_path, upscaled)

    # 4. 고해상도 이미지를 PDF로 변환
    print("2/3 PDF 파일 생성 중...")
    h, w, _ = upscaled.shape
    pdf = FPDF(unit="pt", format=[w, h])
    pdf.add_page()
    pdf.image(temp_image_path, 0, 0, w, h)
    pdf.output(output_pdf_path)

    # 5. 임시 파일 정리
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
        
    print(f"3/3 완료! '{output_pdf_path}' 고해상도 PDF 파일이 생성되었습니다.")

if __name__ == "__main__":
    run_upscale()