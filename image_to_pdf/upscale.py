import os
import cv2
from fpdf import FPDF

# 1. 파일 경로 설정 (Slice 1.png 로 수정됨)
input_image_path = 'Slice 1.png'       # 원본 이미지 파일명
output_pdf_path = 'output_high_res.pdf' # 최종 출력될 PDF 파일명
model_path = 'fsrcnn_x4.pb'            # 초해상도 AI 모델 파일명
temp_image_path = 'temp_upscaled.png'   # 임시 저장 파일명

def run_upscale():
    # 2. 파일 존재 여부 점검
    if not os.path.exists(input_image_path):
        print(f"[오류] 원본 이미지 파일('{input_image_path}')이 폴더에 없습니다. 파일명과 위치를 확인해주세요.")
        return
    if not os.path.exists(model_path):
        print(f"[오류] AI 모델 파일('{model_path}')이 폴더에 없습니다. fsrcnn_x4.pb 파일을 다운로드해서 같은 폴더에 배치해 주세요.")
        return

    # 3. 이미지 로드 및 AI 업스케일링 (4배 확대)
    print("1/3 이미지 고해상도 복원 중... (시간이 조금 걸릴 수 있습니다)")
    img = cv2.imread(input_image_path)
    
    if img is None:
         print(f"[오류] '{input_image_path}' 이미지를 읽을 수 없습니다. 파일이 손상되었거나 경로가 잘못되었습니다.")
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
        
    print(f"3/3 완료! '{output_pdf_path}' 고해상도 PDF 파일이 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    run_upscale()