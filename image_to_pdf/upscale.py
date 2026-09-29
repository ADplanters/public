import os
from PIL import Image, ImageEnhance, ImageFilter

input_image_path = 'Slice 1.png'          # 원본 이미지 파일명
output_pdf_path = 'final_high_res.pdf'    # 최종 고해상도 PDF 파일명

def convert_to_high_res_pdf():
    if not os.path.exists(input_image_path):
        print(f"[오류] '{input_image_path}' 파일이 폴더에 없습니다. 파일명을 확인해 주세요.")
        return

    print("1/3 원본 이미지 읽는 중...")
    img = Image.open(input_image_path).convert('RGB')
    
    # 2. 4배 고화질 Lanczos 업스케일링
    print("2/3 이미지 4배 확대 및 텍스트/도형 선명도 보정 중...")
    w, h = img.size
    scaled_img = img.resize((w * 4, h * 4), Image.Resampling.LANCZOS)
    
    # 글씨 테두리 및 도형 경계선을 또렷하게 만드는 언샤프 마스크 필터 적용
    sharpened_img = scaled_img.filter(
        ImageFilter.UnsharpMask(radius=3, percent=180, threshold=2)
    )
    
    # 대비(Contrast) 보정으로 글자 가독성 향상
    enhancer = ImageEnhance.Contrast(sharpened_img)
    final_img = enhancer.enhance(1.1)

    # 3. 300 DPI 고해상도 PDF로 저장
    print("3/3 고해상도 PDF 출력 중...")
    final_img.save(output_pdf_path, "PDF", resolution=300.0)
    
    print(f"\n성공! 고해상도 PDF 파일이 생성되었습니다: '{output_pdf_path}'")

if __name__ == "__main__":
    convert_to_high_res_pdf()