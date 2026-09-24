# ==========================================
# File: main.py
# Description: ADPLANTERS 9:16 '해피메리추석' AI 이미지 생성 및 300 DPI 고해상도 PDF 변환 통합 스크립트
# Location: github_repo/image_to_pdf/main.py
# ==========================================
# [Requirements]
# pip install pillow reportlab python-dotenv requests openai
# ==========================================

import os
import sys
import logging
from pathlib import Path
from io import BytesIO

# 외부 패키지 안전 임포트
try:
    import requests
    from PIL import Image
    from reportlab.pdfgen import canvas
    from dotenv import load_dotenv
    ENV_AVAILABLE = True
except ImportError as e:
    print(f"❌ 필수 패키지가 설치되지 않았습니다: {e}")
    print("👉 실행 전 터미널에서 다음 명령어를 입력하세요: pip install pillow reportlab python-dotenv requests openai")
    sys.exit(1)

# --- [실시간 터미널 로깅 설정] ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# --- [상수 및 경로 설정 (환경 격리 완벽 대응)] ---
BASE_DIR = Path(__file__).parent.resolve()
PDF_DPI = 300  # 고해상도 인쇄 규격 (300 DPI)
TARGET_IMAGE_NAME = "happy_merry_chuseok_9x16.png"
OUTPUT_PDF_NAME = "ADPLANTERS_HappyMerryChuseok_300DPI.pdf"

# 파비콘, 로고 등 포스터가 아닌 이미지 오탐지 방지 키워드
EXCLUDE_KEYWORDS = ["logo", "favicon", "banner", "로고", "파비콘", "배너", "icon"]

# 환경변수 로드 (.env 보안 설정)
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

# [보안 지침] API 키는 코드에 하드코딩하지 않고 환경 변수에서 가져옵니다.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 상세 프롬프트 (요청하신 모든 시각적 요소 포함)
PROMPT_DESCRIPTION = """
Vertical 9:16 aspect ratio poster for Chuseok holiday greeting.
Deep navy blue night sky with a giant bright golden full moon at top center, shooting stars, and dark blue mountain lake landscape with moonlight reflecting on the water.
Written in clean white Korean calligraphy in the upper sky: '해피메리추석'.
At the bottom campsite setup with equipment hardcases and warm lanterns.
Team members positioned around lakeside from left to right:
1. '촬영감독' (Male director standing behind a professional camera on a tripod),
2. '웹기획자' (Male web planner next to him holding a tablet),
3. 'CEO' (Male CEO sitting on a camping chair, wearing dark blue Levi's jeans with the red pocket tab visible, and light grey Asics Gel-Kayano sneakers),
4. '셀럽 A' (Attractive female celebrity nearby),
5. '셀럽 B' (Attractive female celebrity standing),
6. '마케터' (Handsome male marketer with a notebook),
7. '개발자' (Male developer on the right wearing a headset working on a laptop),
8. A cute Shiba Inu dog sitting next to the developer.
White text labels with small white pointer arrows above each person: '촬영감독', '웹기획자', 'CEO', '셀럽 A', '셀럽 B', '마케터', '개발자'.
At the bottom center, the official ADPLANTERS logo.
Photorealistic, rich blue night lighting, ultra-high detail.
"""

def generate_image_with_ai(prompt: str, save_path: Path) -> bool:
    """
    OpenAI DALL-E 3 API를 연동하여 요청한 구도와 조건의 9:16 포스터 이미지를 생성합니다.
    """
    if not OPENAI_API_KEY:
        logging.warning("⚠️ OPENAI_API_KEY가 설정되지 않아 AI 이미지 자동 생성을 건너뜁니다.")
        return False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        logging.info("🎨 OpenAI API를 통해 '해피메리추석' 9:16 포스터 이미지를 생성 중입니다...")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",  # 9:16 세로형 규격
            quality="hd",
            n=1
        )
        image_url = response.data[0].url
        logging.info("✅ 이미지 생성 성공! 고해상도 파일 다운로드 중...")

        res = requests.get(image_url, timeout=30)
        res.raise_for_status()

        with Image.open(BytesIO(res.content)) as img:
            img.save(save_path, format="PNG")
            logging.info(f"💾 이미지 저장 완료: {save_path.name}")
        return True

    except Exception as e:
        logging.error(f"❌ AI 이미지 생성 중 에러 발생: {e}")
        return False

def find_chuseok_poster_image(script_dir: Path) -> Path:
    """
    폴더 내부에서 로고/배너/파비콘 이미지를 제외하고
    '해피메리추석' 포스터 이미지(.png, .jpg)를 자동으로 찾아냅니다.
    """
    target_path = script_dir / TARGET_IMAGE_NAME
    if target_path.exists():
        return target_path

    valid_extensions = ("*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG")
    candidates = []

    for ext in valid_extensions:
        for file_path in script_dir.glob(ext):
            filename_lower = file_path.name.lower()
            if any(keyword in filename_lower for keyword in EXCLUDE_KEYWORDS):
                continue
            candidates.append(file_path)

    if candidates:
        latest_file = max(candidates, key=lambda p: p.stat().st_mtime)
        logging.info(f"🔍 포스터 이미지 자동 감지: {latest_file.name}")
        return latest_file

    return None

def convert_image_to_pdf(image_path: Path, pdf_path: Path) -> bool:
    """
    이미지를 화질 손실 없이 300 DPI 고해상도 규격의 PDF 문서로 변환합니다.
    """
    logging.info(f"📄 PDF 변환 시작: {image_path.name} -> {pdf_path.name}")

    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            img_mode = img.mode
            logging.info(f"📊 이미지 해상도 분석: {img_width} x {img_height} px ({img_mode})")

            # 300 DPI 기준 PDF Canvas Point 단위 계산 (1 inch = 72 points)
            page_width_pts = (img_width / PDF_DPI) * 72
            page_height_pts = (img_height / PDF_DPI) * 72

            c = canvas.Canvas(str(pdf_path), pagesize=(page_width_pts, page_height_pts))
            c.drawImage(
                str(image_path),
                0, 0,
                width=page_width_pts,
                height=page_height_pts,
                preserveAspectRatio=True,
                mask='auto'
            )
            c.showPage()
            c.save()

            logging.info(f"🎉 300 DPI 고해상도 PDF 출력 성공: {pdf_path.name}")
            return True

    except MemoryError:
        logging.error("❌ 메모리 부족: 이미지 파일의 해상도가 가용 메모리를 초과했습니다.")
        return False
    except PermissionError:
        logging.error("❌ 권한 오류: 출력할 PDF 파일이 이미 다른 프로그램에서 열려 있는지 확인하세요.")
        return False
    except Exception as e:
        logging.error(f"❌ PDF 변환 중 예기치 못한 에러 발생: {e}", exc_info=True)
        return False

def main():
    print("\n" + "="*65)
    print("🚀 [ADPLANTERS] 해피메리추석 9:16 포스터 -> 300 DPI PDF 파이프라인")
    print("="*65)
    logging.info(f"작업 폴더 위치: {BASE_DIR}")

    image_filepath = BASE_DIR / TARGET_IMAGE_NAME
    pdf_filepath = BASE_DIR / OUTPUT_PDF_NAME

    # 1. API 키가 등록되어 있고 파일이 없으면 AI 자동 생성
    if not image_filepath.exists() and OPENAI_API_KEY:
        generate_image_with_ai(PROMPT_DESCRIPTION, image_filepath)

    # 2. 이미지 파일 자동 감지 (로고/배너 파일 제외)
    target_image = find_chuseok_poster_image(BASE_DIR)

    if not target_image:
        logging.error("❌ 'image_to_pdf' 폴더에서 포스터 이미지를 찾을 수 없습니다.")
        print("-" * 65)
        print("💡 [안내]")
        print("1. .env 파일에 OPENAI_API_KEY를 설정하시면 이미지가 자동으로 생성됩니다.")
        print(f"2. 또는 원하시는 포스터 이미지 파일(.png/.jpg)을 '{BASE_DIR}' 폴더에 넣고 `python main.py`를 다시 실행해 주세요.")
        print("="*65 + "\n")
        return

    # 3. 고해상도 PDF 출력
    success = convert_image_to_pdf(target_image, pdf_filepath)

    print("-" * 65)
    if success:
        print("✅ [성공] 고해상도 300 DPI PDF 출력이 완료되었습니다!")
        print(f"📁 생성된 PDF 위치: {pdf_filepath}")
    else:
        print("❌ [실패] 변환 도중 에러가 발생했습니다. 로그를 확인해 주세요.")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()