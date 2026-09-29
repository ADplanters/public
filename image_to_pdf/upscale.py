import os
from PIL import Image, ImageFilter, ImageEnhance

# 파일 경로 설정
input_image_path = 'Slice 1.png'        # 원본 이미지 파일명
output_pdf_path = 'output_high_res.pdf' # 최종 출력될 고해상도 PDF 파일명

def upscale_to_pdf():
    # 1. 원본 이미지 파일 존재 여부 확인
    if not os.path.exists(input_image_path):
        print(f"[오류] '{input_image_path}' 파일이 현재 폴더에 없습니다.")
        return

    print("1/3 이미지를 불러오는 중...")
    img = Image.open(input_image_path).convert('RGB')

    # 2. 4배 고해상도 리사이징 (Lanczos 알고리즘 적용)
    print("2/3 이미지 4배 확대 및 선명도 보정 작업 중...")
    new_width = img.width * 4
    new_height = img.height * 4
    
    # Lanczos 필터로 고화질 확대
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 텍스트 및 도형 선명도(Unsharp Mask) 강화
    sharpened_img = resized_img.filter(
        ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3)
    )

    # 3. 고해상도(300 DPI) PDF 파일로 직접 출력 및 저장
    print("3/3 고해상도 PDF 파일 생성 중...")
    sharpened_img.save(output_pdf_path, "PDF", resolution=300.0)

    print(f"\n성공! '{output_pdf_path}' 고해상도 PDF가 생성되었습니다.")

if __name__ == "__main__":
    upscale_to_pdf()