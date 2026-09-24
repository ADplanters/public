"""
=============================================================================
[애드플랜터스 추석 인사 카드 - 강아지 '고리' 이름 추가 스크립트]
실행 환경: VS Code Tunnel / GitHub Public Repository (image_to_pdf 폴더 내)
필요 패키지: pip install pypdf reportlab
=============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from io import BytesIO

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    from reportlab.lib.colors import HexColor, white
except ImportError:
    logging.error("필수 패키지가 설치되지 않았습니다. 터미널에서 다음을 실행하세요: pip install pypdf reportlab")
    sys.exit(1)


# =============================================================================
# 1. 경로 및 환경 설정 (절대 경로 기반의 상대적 위치 계산)
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
INPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_highres.pdf"
OUTPUT_PDF = BASE_DIR / "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"

# TODO: 사용하려는 한글 TTF 폰트 파일명으로 변경하세요. (현재 폴더에 위치해야 함)
FONT_FILENAME = "NanumGothic.ttf" 
FONT_PATH = BASE_DIR / FONT_FILENAME

# =============================================================================
# 2. 스타일 및 위치 커스텀 설정 (기존 사람들의 이름 스타일과 동일하게 맞추세요)
# =============================================================================
STYLE_CONFIG = {
    "text": "고리",
    "font_size": 24,            # 글자 크기
    "font_color": HexColor("#FFFFFF"), # 글자 색상 (현재 흰색)
    
    # PDF의 좌표는 좌측 하단이 (0, 0)입니다. 
    # 우측 하단 시바견 위치에 맞게 X, Y 좌표를 조정하세요.
    "pos_x": 800,               # 텍스트 좌측 하단 X 좌표 (문서 크기에 맞춰 수정 필요)
    "pos_y": 150,               # 텍스트 좌측 하단 Y 좌표 (문서 크기에 맞춰 수정 필요)
    
    # 배경 박스(직책/이름표 느낌)가 필요하다면 아래 설정을 사용하세요.
    "use_bg_box": True,
    "bg_color": HexColor("#333333"), # 배경색 (현재 어두운 회색)
    "bg_padding_x": 15,         # 텍스트 좌우 여백
    "bg_padding_y": 8,          # 텍스트 상하 여백
    "bg_radius": 5              # 모서리 둥글기
}


def create_overlay_pdf(width: float, height: float) -> BytesIO:
    """
    주어진 문서 크기(width, height)에 맞춰 텍스트가 포함된 투명 PDF(오버레이)를 메모리에 생성합니다.
    """
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    
    # 한글 폰트 등록
    if not FONT_PATH.exists():
        logging.error(f"폰트 파일을 찾을 수 없습니다: {FONT_PATH}")
        logging.error("한글 출력을 위해 TTF 폰트 파일을 폴더에 넣고 이름을 맞춰주세요.")
        sys.exit(1)
        
    try:
        pdfmetrics.registerFont(TTFont('KoreanFont', str(FONT_PATH)))
        c.setFont('KoreanFont', STYLE_CONFIG["font_size"])
    except Exception as e:
        logging.error(f"폰트 등록 중 오류가 발생했습니다: {e}")
        sys.exit(1)

    text = STYLE_CONFIG["text"]
    x = STYLE_CONFIG["pos_x"]
    y = STYLE_CONFIG["pos_y"]
    
    # 배경 박스 그리기 (기존 인물 이름 스타일에 박스가 있다면)
    if STYLE_CONFIG["use_bg_box"]:
        text_width = c.stringWidth(text, 'KoreanFont', STYLE_CONFIG["font_size"])
        box_x = x - STYLE_CONFIG["bg_padding_x"]
        # Y좌표 보정 (폰트 베이스라인 아래로 박스 여백 확보)
        box_y = y - STYLE_CONFIG["bg_padding_y"] - (STYLE_CONFIG["font_size"] * 0.2)
        box_width = text_width + (STYLE_CONFIG["bg_padding_x"] * 2)
        box_height = STYLE_CONFIG["font_size"] + (STYLE_CONFIG["bg_padding_y"] * 2)
        
        c.setFillColor(STYLE_CONFIG["bg_color"])
        c.setStrokeColor(STYLE_CONFIG["bg_color"])
        c.roundRect(box_x, box_y, box_width, box_height, STYLE_CONFIG["bg_radius"], fill=1, stroke=0)

    # 텍스트 그리기
    c.setFillColor(STYLE_CONFIG["font_color"])
    c.drawString(x, y, text)
    
    c.save()
    packet.seek(0)
    return packet


def main():
    if not INPUT_PDF.exists():
        logging.error(f"입력 PDF 파일이 존재하지 않습니다: {INPUT_PDF}")
        return

    logging.info(f"원본 PDF 로드 중: {INPUT_PDF.name}")
    
    try:
        # 1. 원본 PDF 읽기
        reader = PdfReader(str(INPUT_PDF))
        writer = PdfWriter()
        
        # 2. 첫 번째 페이지 가져오기 및 크기 확인
        page = reader.pages[0]
        # MediaBox: [x0, y0, x1, y1] (x1이 너비, y1이 높이)
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        
        logging.info(f"PDF 페이지 크기: Width={page_width}, Height={page_height}")
        
        # 3. 투명 배경에 '고리' 텍스트가 그려진 오버레이 PDF 생성
        logging.info("강아지 '고리' 이름 태그 오버레이 생성 중...")
        overlay_packet = create_overlay_pdf(page_width, page_height)
        overlay_reader = PdfReader(overlay_packet)
        overlay_page = overlay_reader.pages[0]
        
        # 4. 원본 페이지 위에 오버레이 병합 (고해상도 원본 데이터 100% 유지)
        page.merge_page(overlay_page)
        writer.add_page(page)
        
        # 나머지 페이지가 있다면 그대로 추가 (일반적으로 인사카드는 1장이지만 예외처리)
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])
            
        # 5. 결과물 저장
        with open(OUTPUT_PDF, "wb") as f:
            writer.write(f)
            
        logging.info(f"성공적으로 생성되었습니다! 저장 위치: {OUTPUT_PDF.name}")
        logging.info("안내: 위치(X, Y)나 색상이 어색하다면 STYLE_CONFIG의 pos_x, pos_y, 컬러 값을 수정 후 다시 실행하세요.")
        
    except Exception as e:
        logging.error(f"PDF 처리 중 예기치 않은 오류가 발생했습니다: {e}", exc_info=True)


if __name__ == "__main__":
    main()