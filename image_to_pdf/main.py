# GitHub public 레포지토리 환경(VS Code 터널 등)에서 즉시 실행 가능한 완성된 main.py 코드입니다.
# 실행 전 터미널에서 아래 의존성 패키지를 반드시 설치해주세요.
# pip install pymupdf pillow reportlab

import os
import sys
import logging
from pathlib import Path
import math

# PDF 처리 및 이미지 변환 라이브러리
try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
except ImportError as e:
    print(f"필수 라이브러리가 설치되지 않았습니다: {e}")
    print("터미널에서 다음 명령어를 실행해주세요: pip install pymupdf pillow reportlab")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 1. 환경 격리 및 경로 설정 (Developer Constraint 1)
# ---------------------------------------------------------------------------
# 현재 실행 중인 main.py의 절대 경로를 기준으로 작업 디렉토리 설정
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    # 대화형 환경 지원
    BASE_DIR = Path(os.getcwd())

INPUT_PDF_NAME = "애드플랜터스_추석_인사_카드_고리추가_highres.pdf"
OUTPUT_PDF_NAME = "애드플랜터스_추석_인사_카드_고리추가_최종.pdf"

# image_to_pdf 폴더 내부에 파일이 존재한다고 가정
INPUT_PATH = BASE_DIR / INPUT_PDF_NAME
OUTPUT_PATH = BASE_DIR / OUTPUT_PDF_NAME

# ---------------------------------------------------------------------------
# 2. 고해상도 및 스타일 설정 (Output Rule 2, 4)
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("Image2PDF_CodeGenerator")

# 출력 PDF 해상도 설정 (300 DPI 이상)
TARGET_DPI = 300
TAG_TEXT = "고리"
# 글씨 색상 (추석 카드 분위기에 맞는 짙은 갈색 계열)
TEXT_COLOR = (74, 44, 23, 255) 
# 텍스트 가독성을 위한 후광(Halo) 효과 색상 (박스 대신 사용)
HALO_COLOR = (255, 255, 255, 200)

# ---------------------------------------------------------------------------
# 3. 유틸리티 함수: 폰트 로드 및 좌표 계산
# ---------------------------------------------------------------------------
def get_korean_font(font_size: int):
    """운영체제별 표준 한글 폰트를 안전하게 로드합니다. (Code Quality 2)"""
    font_paths = []
    
    if sys.platform == "win32":
        font_paths = [
            "C:\\Windows\\Fonts\\malgunbd.ttf", # 맑은 고딕 Bold
            "C:\\Windows\\Fonts\\gulim.ttc"
        ]
    elif sys.platform == "darwin": # macOS
        font_paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/AppleGothic.ttf"
        ]
    else: # Linux
        font_paths = [
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
        ]
        
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                continue
                
    # 폴백: 폰트를 찾지 못했을 경우 기본 폰트 반환 (깨질 수 있음)
    logger.warning("시스템 한글 폰트를 찾지 못해 기본 폰트를 사용합니다.")
    return ImageFont.load_default()

def draw_text_with_halo(draw, position, text, font, text_color, halo_color, halo_radius=2):
    """텍스트 뒤에 박스 없이 배경에 맞게 가독성을 높이는 후광 효과를 추가합니다."""
    x, y = position
    # 후광(Halo) 그리기 (여러 방향으로 텍스트를 겹쳐 그려 부드러운 외곽선 효과)
    for angle in range(0, 360, 45):
        dx = int(halo_radius * math.cos(math.radians(angle)))
        dy = int(halo_radius * math.sin(math.radians(angle)))
        draw.text((x + dx, y + dy), text, font=font, fill=halo_color)
    
    # 본 텍스트 그리기
    draw.text((x, y), text, font=font, fill=text_color)

def calculate_bezier_curve(p0, p1, p2, p3, steps=50):
    """Cubic Bezier Curve 좌표 리스트를 계산합니다."""
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        # 베지에 곡선 공식 적용
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        curve_points.append((x, y))
    return curve_points

def draw_curved_arrow(draw, start_point, end_point, color, width=5):
    """텍스트에서 강아지로 향하는 휘어진 화살표를 그립니다."""
    # 제어점 설정 (휘어지는 정도 조절)
    # 텍스트 오른쪽 아래에서 시작해서, 중간에 오른쪽으로 휘었다가 강아지로 들어감
    p0 = start_point
    p3 = end_point
    
    # 곡률을 위한 제어점 (Start -> P1 -> P2 -> End)
    # 단순히 우하향하는 것보다 약간 S자 형태로 휘어지게 설정
    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]
    
    p1 = (p0[0] + dx * 0.8, p0[1] + dy * 0.1) # 텍스트 근처에서 오른쪽으로 뻗음
    p2 = (p3[0] - dx * 0.1, p3[1] - dy * 0.5) # 강아지 위쪽에서 내려옴
    
    # 곡선 계산 및 그리기
    curve_points = calculate_bezier_curve(p0, p1, p2, p3)
    draw.line(curve_points, fill=color, width=width, joint="curve")
    
    # 화살표 머리 (Arrowhead) 그리기
    # 곡선의 마지막 세그먼트 벡터 방향 계산
    if len(curve_points) >= 2:
        last_p = curve_points[-1]
        prev_p = curve_points[-3] # 약간 이전 점을 기준으로 잡아야 방향이 안정적
        
        angle = math.atan2(last_p[1] - prev_p[1], last_p[0] - prev_p[0])
        arrow_size = width * 5
        
        # 화살표 날개 두 점 계산
        arrow_p1 = (last_p[0] - arrow_size * math.cos(angle - math.pi / 6),
                    last_p[1] - arrow_size * math.sin(angle - math.pi / 6))
        arrow_p2 = (last_p[0] - arrow_size * math.cos(angle + math.pi / 6),
                    last_p[1] - arrow_size * math.sin(angle + math.pi / 6))
        
        draw.polygon([last_p, arrow_p1, arrow_p2], fill=color)

# ---------------------------------------------------------------------------
# 4. 메인 처리 로직 (Workflow Example)
# ---------------------------------------------------------------------------
def main():
    logger.info("작업을 시작합니다.")

    # 4-1. 입력 파일 확인
    if not INPUT_PATH.exists():
        logger.error(f"입력 파일을 찾을 수 없습니다: {INPUT_PATH}")
        sys.exit(1)

    try:
        # 4-2. PDF를 고해상도 이미지로 변환 (Code Quality 4 - Resource Cleanup)
        logger.info(f"PDF 로드 중: {INPUT_PDF_NAME}")
        with fitz.open(INPUT_PATH) as doc:
            if doc.page_count == 0:
                raise Exception("PDF에 페이지가 없습니다.")
            
            page = doc.load_page(0) # 첫 번째 페이지
            # 고해상도 렌더링을 위한 Matrix 설정
            mat = fitz.Matrix(TARGET_DPI / 72, TARGET_DPI / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # fitz Pixmap을 Pillow Image로 변환
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            logger.info(f"이미지 변환 완료: {img.width}x{img.height}")

        # 4-3. 자연스러운 이미지 보정 (Output Rule 3)
        logger.info("이미지 보정 적용 중 (선명도, 대비)")
        # 선명도 향상
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3) # 30% 향상
        # 대비 약간 조절 (몽환적이면서 선명하게)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)
        # 미세한 블러로 노이즈 제거 (몽환적 느낌)
        img = img.filter(ImageFilter.SMOOTH_MORE)

        # 4-4. 정밀한 텍스트 및 휘어진 화살표 추가 (Output Rule 4 - 핵심 요구사항)
        draw = ImageDraw.Draw(img)
        
        # 해상도 기반 동적 크기 계산
        width, height = img.size
        dynamic_font_size = int(width * 0.04) # 너비의 4% 크기
        font = get_korean_font(dynamic_font_size)
        line_width = max(3, int(width * 0.003)) # 너비 비례 선 두께

        # 좌표 설정 (전체 이미지 해상도 기준 비율 계산)
        # 핵심: 텍스트는 흰 박스 없이 배경 위에 직접 그림.
        # 강아지 위치 (오른쪽 아래 갈색 강아지 머리 부근 target)
        dog_target_pos = (int(width * 0.85), int(height * 0.82))
        
        # 텍스트 위치 (강아지 왼쪽 위 공간)
        text_origin_pos = (int(width * 0.65), int(height * 0.70))
        
        # 텍스트 폭 계산
        text_bbox = draw.textbbox((0, 0), TAG_TEXT, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        logger.info("텍스트(후광 효과) 및 휘어진 화살표 합성 중")
        
        # [핵심] 1. 텍스트 그리기 (흰 박스 없이 가독성 확보)
        draw_text_with_halo(draw, text_origin_pos, TAG_TEXT, font, TEXT_COLOR, HALO_COLOR, halo_radius=3)

        # [핵심] 2. 텍스트에서 강아지까지 휘어진 화살표 그리기
        # 화살표 시작점: 텍스트의 오른쪽 중앙
        arrow_start_pos = (text_origin_pos[0] + text_w + 10, text_origin_pos[1] + text_h // 2)
        
        # 화살표 색상은 텍스트 색상과 동일하게 설정하여 통일감 부여
        draw_curved_arrow(draw, arrow_start_pos, dog_target_pos, color=TEXT_COLOR, width=line_width)

        # 4-5. 고해상도 PDF로 저장
        logger.info(f"결과 PDF 저장 중: {OUTPUT_PDF_NAME}")
        # DPI 정보를 포함하여 저장
        img.save(OUTPUT_PATH, "PDF", resolution=TARGET_DPI, save_all=True)

        logger.info("모든 작업이 성공적으로 완료되었습니다.")

    except Exception as e:
        logger.error(f"작업 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()