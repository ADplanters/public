import os
import logging
from pathlib import Path
from PIL import Image, ImageEnhance
import img2pdf

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

def apply_image_enhancements(img: Image.Image, sharpness: float = 1.0, contrast: float = 1.0, brightness: float = 1.0) -> Image.Image:
    """
    이미지 품질을 자동으로 보정합니다. (기본값 1.0은 원본 유지)
    """
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(sharpness)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)
    return img

def convert_single_image_to_pdf(image_path: Path, output_pdf_path: Path, auto_enhance: bool = False) -> bool:
    """
    이미지 재압축이나 해상도 저하(Resampling) 없이 1:1 고해상도 원본 그대로 PDF로 변환합니다.
    """
    if not image_path.exists():
        logging.warning(f"파일을 찾을 수 없습니다: {image_path.name}")
        return False

    try:
        if auto_enhance:
            # 이미지 보정 적용시 임시 바이너리로 가공 처리
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = img.convert("RGB")
                
                enhanced_img = apply_image_enhancements(img, sharpness=1.1, contrast=1.05)
                temp_enhanced_path = image_path.parent / f"_temp_{image_path.name}"
                enhanced_img.save(temp_enhanced_path, format="PNG", compress_level=0)
                
                with open(output_pdf_path, "wb") as f:
                    f.write(img2pdf.convert(str(temp_enhanced_path)))
                
                if temp_enhanced_path.exists():
                    os.remove(temp_enhanced_path)
        else:
            # 원본 비트스트림 손실 없이 그대로 PDF 컨테이너 패킹 (최고 화질 보장)
            with open(output_pdf_path, "wb") as f:
                f.write(img2pdf.convert(str(image_path)))

        logging.info(f"변환 완료 (고해상도 원본 유지): {image_path.name} -> {output_pdf_path.name}")
        return True

    except Exception as e:
        logging.warning(f"img2pdf 엔진 실패 ({e}). Pillow 대체 엔진으로 전환합니다...")
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                dpi = img.info.get("dpi", (300, 300))
                img.save(output_pdf_path, "PDF", resolution=dpi[0])
            logging.info(f"대체 엔진 변환 성공: {output_pdf_path.name}")
            return True
        except Exception as fallback_err:
            logging.error(f"PDF 변환 실패 ({image_path.name}): {fallback_err}")
            return False

def main():
    # 실행 위치와 상관없이 스크립트가 속한 폴더(image_to_pdf) 기준으로 경로 계산
    base_dir = Path(__file__).parent.resolve()
    
    # Slice 1.png 부터 Slice 6.png 까지 대상 지정
    slice_names = [f"Slice {i}.png" for i in range(1, 7)]
    valid_image_paths = []

    logging.info("===== 이미지 -> 고해상도 PDF 변환 시작 =====")

    for name in slice_names:
        img_file = base_dir / name
        if img_file.exists():
            pdf_file = base_dir / f"{img_file.stem}.pdf"
            # auto_enhance=False : 원본 화질/색상 100% 보존
            if convert_single_image_to_pdf(img_file, pdf_file, auto_enhance=False):
                valid_image_paths.append(img_file)

    # 6장 전체를 하나의 합본 PDF로도 생성
    if valid_image_paths:
        combined_pdf_path = base_dir / "Slice_All_Combined.pdf"
        try:
            with open(combined_pdf_path, "wb") as f:
                f.write(img2pdf.convert([str(p) for p in valid_image_paths]))
            logging.info(f"전체 합본 PDF 생성 완료: {combined_pdf_path.name}")
        except Exception as e:
            logging.error(f"합본 PDF 생성 실패: {e}")

    logging.info("===== 모든 작업 완료 =====")

if __name__ == "__main__":
    main()