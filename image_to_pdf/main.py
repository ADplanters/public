# ==============================================================================
# [의존성 설치 안내]
# 터미널에서 아래 명령어를 실행하세요.
# pip install pymupdf
# ==============================================================================

import os
import sys
import logging
from pathlib import Path
import pymupdf  # 최신 PyMuPDF API 사용

# [환경 설정] 로깅 초기화
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_system_korean_font() -> str:
    """운영체제별 기본 한글 폰트(.ttf/.ttc) 파일 경로를 탐색합니다."""
    candidate_paths = [
        r"C:\Windows\Fonts\malgun.ttf",       # Windows 맑은 고딕
        r"C:\Windows\Fonts\malgunbd.ttf",     # Windows 맑은 고딕 Bold
        r"C:\Windows\Fonts\gulim.ttc",        # Windows 굴림
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # macOS
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",     # Linux
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return None

def add_label_and_arrow_to_pdf(input_path: Path, output_path: Path, custom_font_path: str = None):
    """
    기존 고해상도 PDF를 불러와 네이티브 벡터 방식으로
    '고리' 이름표와 화살표를 추가하여 원본 해상도 100% 유지 상태로 저장합니다.
    """
    if not input_path.exists():
        logging.error(f"입력 파일을 찾을 수 없습니다: {input_path}")
        return

    # 폰트 파일 경로 확정
    font_path = custom_font_path or get_system_korean_font()
    if not font_path or not os.path.exists(font_path):
        logging.error("사용 가능한 한글 폰트(.ttf) 파일을 찾지 못했습니다.")
        return

    try:
        logging.info(f"PDF 문서를 엽니다: {input_path}")
        with pymupdf.open(input_path) as doc:
            page = doc[0]
            width = page.rect.width
            height = page.rect.height
            
            logging.info(f"페이지 크기 확인 - 너비: {width:.2f}, 높이: {height:.2f}")

            # ==================================================================
            # [디자인 커스텀 영역] (너비 368.64 / 높이 660.48 기준)
            # ==================================================================
            text = "고리"
            fontsize = 16          # 글자 크기
            text_color = (0, 0, 0) # RGB 검은색
            
            # 우측 하단 시바견 위치 좌표 세팅
            text_x = width - 110
            text_y = height - 120
            text_point = pymupdf.Point(text_x, text_y)

            # 화살표 설정
            arrow_color = (0.1, 0.1, 0.1) # 짙은 회색 / 검은색
            line_thickness = 1.8           # 선 두께
            
            arrow_start = pymupdf.Point(text_x + 15, text_y + 12) # 텍스트 아래쪽
            arrow_end = pymupdf.Point(width - 50, height - 50)     # 강아지 위치 방향
            # ==================================================================

            # 1. 한글 폰트 동적 등록
            font_name = "KoreanFont"
            page.insert_font(fontname=font_name, fontfile=font_path)
            logging.info(f"폰트 적용 완료: {font_path}")

            # 2. 텍스트 삽입 (네이티브 벡터)
            page.insert_text(
                text_point, 
                text, 
                fontsize=fontsize, 
                fontname=font_name, 
                color=text_color
            )
            logging.info(f"텍스트 '{text}' 삽입 완료 (좌표: {text_point})")

            # 3. 화살표 벡터 그리기 (arrows=2 는 끝부분 화살표 머리를 의미함)
            shape = page.new_shape()
            shape.draw_line(arrow_start, arrow_end)
            shape.finish(
                width=line_thickness, 
                color=arrow_color, 
                arrows=2  # 0:없음, 1:시작점, 2:끝점(ARROW_LAST), 3:양쪽
            )
            shape.commit()
            logging.info("화살표 벡터 적용 완료")

            # 4. 고해상도 최적화 저장
            doc.save(output_path, garbage=4, deflate=True)
            logging.info(f"성공적으로 저장되었습니다: {output_path}")

    except Exception as e:
        logging.error(f"PDF 처리 중 오류 발생: {e}", exc_info=True)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    
    INPUT_FILENAME = "애드플랜터스_추석_인사_카드_highres.pdf"
    OUTPUT_FILENAME = "애드플랜터스_추석_인사_카드_highres_gori.pdf"
    
    input_pdf_path = BASE_DIR / INPUT_FILENAME
    output_pdf_path = BASE_DIR / OUTPUT_FILENAME
    
    logging.info("=== PDF 고리 이름표 추가 작업 시작 ===")
    add_label_and_arrow_to_pdf(
        input_path=input_pdf_path, 
        output_path=output_pdf_path
    )