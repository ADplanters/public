"""
# main.py for image_to_pdf project
# ADplanters Service Board Generator & PDF Compiler (Windows File Lock Fix & High-Res)

Required Dependencies:
pip install pillow reportlab python-dotenv

requirements.txt:
pillow>=10.0.0
reportlab>=4.0.0
python-dotenv>=1.0.0
"""

import os
import sys
import logging
import urllib.request
import ssl
from pathlib import Path

# 보안 지침: .env 환경 변수 안전 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 이미지 및 PDF 처리 라이브러리
try:
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install dependencies: pip install pillow reportlab python-dotenv")
    sys.exit(1)

# --- 1. 로깅 및 경로 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ADplantersProductionPipeline")

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'
OUTPUT_IMG_PATH = BASE_DIR / 'adplanters_service_board.png'
OUTPUT_PDF_PATH = BASE_DIR / 'adplanters_service_board.pdf'
FONT_PATH = BASE_DIR / 'NanumGothicBold.ttf'

# API Key 검증 함수 (하드코딩 방지)
def load_api_key():
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
        return os.environ.get('API_KEY')
    return None

# --- 2. 한글 폰트 자동 확보 ---
def ensure_korean_font():
    """선명한 고해상도 출력을 위한 나눔고딕 Bold 폰트 자동 다운로드"""
    if not FONT_PATH.exists():
        logger.info("Downloading NanumGothic Bold font...")
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
            logger.info("Font downloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download font: {e}")
            return None
    return str(FONT_PATH)

# --- 3. 정밀 그래픽 조형 헬퍼 함수 ---
def draw_rounded_rectangle(draw, xy, rad, fill, outline=None, width=1):
    """둥근 사각형 조형 함수"""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0, y0 + rad, x1, y1 - rad], fill=fill)
    draw.rectangle([x0 + rad, y0, x1 - rad, y1], fill=fill)
    draw.pieslice([x0, y0, x0 + rad * 2, y0 + rad * 2], 180, 270, fill=fill)
    draw.pieslice([x1 - rad * 2, y0, x1, y0 + rad * 2], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - rad * 2, x0 + rad * 2, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - rad * 2, y1 - rad * 2, x1, y1], 0, 90, fill=fill)
    
    if outline:
        draw.arc([x0, y0, x0 + rad * 2, y0 + rad * 2], 180, 270, fill=outline, width=width)
        draw.arc([x1 - rad * 2, y0, x1, y0 + rad * 2], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - rad * 2, x0 + rad * 2, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - rad * 2, y1 - rad * 2, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + rad, y0, x1 - rad, y0], fill=outline, width=width)
        draw.line([x0 + rad, y1, x1 - rad, y1], fill=outline, width=width)
        draw.line([x0, y0 + rad, x0, y1 - rad], fill=outline, width=width)
        draw.line([x1, y0 + rad, x1, y1 - rad], fill=outline, width=width)

# --- 4. 정밀 조율된 사선 지그재그 로고 워터마크 렌더링 ---
def draw_subtle_zigzag_watermarks(img, font_path):
    """
    워터마크 스탬프 내부에서도 ADplanters 아래에 GentleStudio가 정중앙 소형으로 
    위치하도록 배치하여 시각적 밸런스 유지 (Alpha=70)
    """
    width, height = img.size
    
    stamp_w, stamp_h = 480, 180
    stamp = Image.new('RGBA', (stamp_w, stamp_h), (255, 255, 255, 0))
    stamp_draw = ImageDraw.Draw(stamp)
    
    try:
        wm_font_main = ImageFont.truetype(font_path, 28)
        wm_font_sub = ImageFont.truetype(font_path, 14)
    except Exception:
        wm_font_main = ImageFont.load_default()
        wm_font_sub = ImageFont.load_default()
        
    wm_main_text = "ADplanters"
    wm_sub_text = "GentleStudio"
    
    bbox_m = wm_font_main.getbbox(wm_main_text)
    mw = bbox_m[2] - bbox_m[0]
    mh = bbox_m[3] - bbox_m[1]
    
    bbox_s = wm_font_sub.getbbox(wm_sub_text)
    sw = bbox_s[2] - bbox_s[0]
    
    mx = (stamp_w - mw) // 2
    my = 35
    sx = (stamp_w - sw) // 2
    sy = my + mh + 4
    
    fill_color = (190, 190, 205, 70)  # 은은한 알파 투명도
    stamp_draw.text((mx, my), wm_main_text, fill=fill_color, font=wm_font_main)
    stamp_draw.text((sx, sy), wm_sub_text, fill=fill_color, font=wm_font_sub)
    
    # 사선 회전 (-20도)
    rotated_stamp = stamp.rotate(-20, expand=True, resample=Image.Resampling.BICUBIC)
    
    step_x = 500
    step_y = 280
    
    watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    for row_idx, y in enumerate(range(-120, height + 250, step_y)):
        shift_x = (step_x // 2) if (row_idx % 2 == 1) else 0
        for x in range(-180 + shift_x, width + 250, step_x):
            watermark_layer.paste(rotated_stamp, (x, y), rotated_stamp)
            
    img.paste(watermark_layer, (0, 0), watermark_layer)

# --- 5. 안전 파일 저장 헬퍼 (Errno 22 자동 우회) ---
def save_image_safely(img, target_path, dpi=(300, 300)):
    """파일이 다른 프로그램에서 열려 있어 잠긴 경우(Errno 22) 대체 이름으로 안전 저장"""
    try:
        img.save(str(target_path), format="PNG", dpi=dpi)
        logger.info(f"High-resolution image saved successfully: {target_path.name}")
        return target_path
    except OSError as e:
        logger.warning(f"File lock or permission issue detected on '{target_path.name}'. Retrying with alternative filename...")
        alt_path = target_path.parent / f"{target_path.stem}_new.png"
        try:
            img.save(str(alt_path), format="PNG", dpi=dpi)
            logger.info(f"Image saved safely to alternative file: {alt_path.name}")
            return alt_path
        except Exception as e_inner:
            logger.error(f"Failed to save image: {e_inner}")
            return None

# --- 6. 초고해상도 보드 생성 메인 함수 ---
def generate_service_board(font_path):
    logger.info("Generating Service Board Image...")
    
    # 1600 x 3100 px (300 DPI 규격)
    width, height = 1600, 3100
    dpi = (300, 300)
    
    try:
        fonts = {
            'brand_large': ImageFont.truetype(font_path, 74),
            'brand_small': ImageFont.truetype(font_path, 26),
            'main_title': ImageFont.truetype(font_path, 68),
            'main_sub': ImageFont.truetype(font_path, 32),
            'sec_title': ImageFont.truetype(font_path, 46),
            'sec_tag': ImageFont.truetype(font_path, 28),
            'tbl_head': ImageFont.truetype(font_path, 30),
            'tbl_cell': ImageFont.truetype(font_path, 28),
            'badge': ImageFont.truetype(font_path, 22),
            'card_title': ImageFont.truetype(font_path, 36),
            'card_sub': ImageFont.truetype(font_path, 26),
            'card_bullet': ImageFont.truetype(font_path, 26),
            'bullet_txt': ImageFont.truetype(font_path, 30),
            'footnote': ImageFont.truetype(font_path, 24),
            'btn': ImageFont.truetype(font_path, 38)
        }
    except Exception as e:
        logger.error(f"Font loading failed: {e}")
        return None

    # 색상 정의
    bg_color = (248, 248, 250)
    panel_bg = (255, 255, 255)
    border_color = (220, 220, 228)
    text_dark = (17, 17, 22)
    text_sub = (100, 100, 115)
    brand_orange = (235, 95, 25)  # ADplanters 메인 주황색
    dark_black = (10, 10, 10)     # GentleStudio 아주 검은색
    brand_gold = (181, 145, 70)
    badge_gold = (165, 125, 50)
    
    img = Image.new('RGB', (width, height), color=bg_color)
    
    # 0. 사선 지그재그 워터마크 배경 렌더링
    draw_subtle_zigzag_watermarks(img, font_path)
    
    draw = ImageDraw.Draw(img)
    margin_x = 75

    # ================= 1. 메인 헤더 타이틀 정밀 정렬 =================
    header_y = 105
    
    brand_text = "ADplanters"
    sub_brand_text = "GentleStudio"
    title_suffix = "광고 상품 안내"
    
    bbox_brand = fonts['brand_large'].getbbox(brand_text)
    bw = bbox_brand[2] - bbox_brand[0]
    bh = bbox_brand[3] - bbox_brand[1]
    
    bbox_sub_brand = fonts['brand_small'].getbbox(sub_brand_text)
    gbw = bbox_sub_brand[2] - bbox_sub_brand[0]
    
    bbox_suffix = fonts['main_title'].getbbox(title_suffix)
    sw = bbox_suffix[2] - bbox_suffix[0]
    
    gap = 40
    total_title_w = bw + gap + sw
    start_x = (width - total_title_w) // 2
    
    # 1) ADplanters 브랜드명 (주황색)
    draw.text((start_x, header_y), brand_text, fill=brand_orange, font=fonts['brand_large'])
    
    # 2) GentleStudio 서브 브랜드 (ADplanters 정중앙 바로 아래 배치 & 아주 진한 검은색)
    gentle_x = start_x + (bw - gbw) // 2
    gentle_y = header_y + bh + 4
    draw.text((gentle_x, gentle_y), sub_brand_text, fill=dark_black, font=fonts['brand_small'])
    
    # 3) 광고 상품 안내 타이틀
    draw.text((start_x + bw + gap, header_y + 4), title_suffix, fill=text_dark, font=fonts['main_title'])
    
    # 서브타이틀
    sub_text = "성공적인 비즈니스 성장과 브랜드 가치 상승을 위한 통합 마케팅 솔루션입니다."
    bbox_sub = fonts['main_sub'].getbbox(sub_text)
    sub_w = bbox_sub[2] - bbox_sub[0]
    draw.text(((width - sub_w) // 2, header_y + 120), sub_text, fill=text_sub, font=fonts['main_sub'])

    # ================= 2. Section 1: 인사이트 라이브러리 =================
    sec1_y0, sec1_h = 325, 810
    draw_rounded_rectangle(draw, (margin_x, sec1_y0, width - margin_x, sec1_y0 + sec1_h), 28, fill=panel_bg, outline=border_color, width=2)
    
    draw.text((margin_x + 50, sec1_y0 + 45), "1. 인사이트 라이브러리", fill=text_dark, font=fonts['sec_title'])
    
    tag1_text = "매장 및 협찬 방문 후 인스타그램/블로그 업로드"
    bbox_tag1 = fonts['sec_tag'].getbbox(tag1_text)
    draw.text((width - margin_x - 50 - (bbox_tag1[2] - bbox_tag1[0]), sec1_y0 + 58), tag1_text, fill=text_sub, font=fonts['sec_tag'])
    
    draw.line([(margin_x + 50, sec1_y0 + 115), (width - margin_x - 50, sec1_y0 + 115)], fill=border_color, width=2)
    
    tbl_x0 = margin_x + 45
    tbl_y0 = sec1_y0 + 145
    tbl_w = width - (margin_x * 2) - 90
    col_w = [270, 180, 400, tbl_w - (270 + 180 + 400)]
    
    draw_rounded_rectangle(draw, (tbl_x0, tbl_y0, tbl_x0 + tbl_w, tbl_y0 + 68), 12, fill=(242, 242, 248))
    
    headers = ["팔로워 기준", "구분", "단가 (명당 기준)", "비고"]
    curr_cx = tbl_x0
    for idx, h_txt in enumerate(headers):
        draw.text((curr_cx + 25, tbl_y0 + 20), h_txt, fill=(50, 50, 65), font=fonts['tbl_head'])
        curr_cx += col_w[idx]
        
    rows = [
        ("1만 미만", "고정 단가", "150,000원 ~ 200,000원", "기초 바이럴 및 마이크로 마케팅"),
        ("1만 ~ 3만 미만", "범위 변동", "200,000원 ~ 350,000원", "도달률 및 반응률 반영"),
        ("3만 ~ 5만 미만", "범위 변동", "350,000원 ~ 500,000원", "타겟층 영향력 고려"),
        ("5만 이상", "별도 측정", "500,000원 이상~", "계정별 엔게이지먼트 기반 산출")
    ]
    
    row_y = tbl_y0 + 88
    for r_idx, row_data in enumerate(rows):
        curr_cx = tbl_x0
        if r_idx > 0:
            draw.line([(tbl_x0, row_y - 14), (tbl_x0 + tbl_w, row_y - 14)], fill=(236, 236, 242), width=1)
            
        for c_idx, cell_txt in enumerate(row_data):
            if c_idx == 1:
                badge_bg = badge_gold if "고정" in cell_txt else ((130, 110, 80) if "별도" in cell_txt else (160, 135, 60))
                draw_rounded_rectangle(draw, (curr_cx + 15, row_y + 2, curr_cx + 150, row_y + 44), 8, fill=badge_bg)
                bbox_bg = fonts['badge'].getbbox(cell_txt)
                bw_b = bbox_bg[2] - bbox_bg[0]
                draw.text((curr_cx + 15 + (135 - bw_b) // 2, row_y + 12), cell_txt, fill=(255, 255, 255), font=fonts['badge'])
            elif c_idx == 2:
                draw.text((curr_cx + 25, row_y + 8), cell_txt, fill=text_dark, font=fonts['tbl_cell'])
            else:
                draw.text((curr_cx + 25, row_y + 8), cell_txt, fill=(45, 45, 55), font=fonts['tbl_cell'])
            curr_cx += col_w[c_idx]
        row_y += 102

    draw.text((margin_x + 50, sec1_y0 + sec1_h - 60), "* 진행 인원 수에 따라 견적 조율 가능", fill=text_sub, font=fonts['footnote'])

    # ================= 3. Section 2: 제품 제공 협찬 =================
    sec2_y0, sec2_h = 1195, 820
    draw_rounded_rectangle(draw, (margin_x, sec2_y0, width - margin_x, sec2_y0 + sec2_h), 28, fill=panel_bg, outline=border_color, width=2)
    
    draw.text((margin_x + 50, sec2_y0 + 45), "2. 제품 제공 협찬", fill=text_dark, font=fonts['sec_title'])
    
    tag2_text = "제품 진행 불가 / 그룹 패키지 단위 진행"
    bbox_tag2 = fonts['sec_tag'].getbbox(tag2_text)
    draw.text((width - margin_x - 50 - (bbox_tag2[2] - bbox_tag2[0]), sec2_y0 + 58), tag2_text, fill=text_sub, font=fonts['sec_tag'])
    
    draw.line([(margin_x + 50, sec2_y0 + 115), (width - margin_x - 50, sec2_y0 + 115)], fill=border_color, width=2)

    card_w = 430
    card_gap = 35
    cards_data = [
        ("30명 패키지", "최소 진행 단위", ["인플루언서 30명 매칭", "제품 배송 관리 및 모니터링", "기초 노출 리포트 제공"]),
        ("50명 패키지", "스탠다드 그룹", ["인플루언서 50명 매칭", "제품 배송 관리 및 모니터링", "검색 노출 최적화 세팅"]),
        ("100명 패키지", "프리미엄 그룹", ["인플루언서 100명 매칭", "대량 바이럴 노출 극대화", "상세 성과 분석 보고서 제공"])
    ]

    card_x_start = margin_x + 45
    card_y0 = sec2_y0 + 155
    card_h = 520

    for idx, (c_title, c_sub, c_bullets) in enumerate(cards_data):
        cx = card_x_start + idx * (card_w + card_gap)
        draw_rounded_rectangle(draw, (cx, card_y0, cx + card_w, card_y0 + card_h), 22, fill=(252, 252, 254), outline=(228, 228, 236), width=2)
        
        bbox_ct = fonts['card_title'].getbbox(c_title)
        draw.text((cx + (card_w - (bbox_ct[2] - bbox_ct[0])) // 2, card_y0 + 42), c_title, fill=text_dark, font=fonts['card_title'])
        
        bbox_cs = fonts['card_sub'].getbbox(c_sub)
        draw.text((cx + (card_w - (bbox_cs[2] - bbox_cs[0])) // 2, card_y0 + 95), c_sub, fill=text_sub, font=fonts['card_sub'])
        
        draw.line([(cx + 35, card_y0 + 150), (cx + card_w - 35, card_y0 + 150)], fill=(218, 218, 228), width=1)
        
        b_y = card_y0 + 195
        for bullet in c_bullets:
            draw.text((cx + 30, b_y), "✓", fill=brand_gold, font=fonts['card_bullet'])
            draw.text((cx + 62, b_y), bullet, fill=(45, 45, 55), font=fonts['card_bullet'])
            b_y += 88

    draw.text((margin_x + 50, sec2_y0 + sec2_h - 60), "* 제품 제공 협찬은 최소 30명부터 신청 가능하며, 제품 원가 및 구성에 따라 별도 톤 견적이 산출됩니다.", fill=text_sub, font=fonts['footnote'])

    # ================= 4. Section 3: 인플루언서 공동구매 =================
    sec3_y0, sec3_h = 2065, 740
    draw_rounded_rectangle(draw, (margin_x, sec3_y0, width - margin_x, sec3_y0 + sec3_h), 28, fill=panel_bg, outline=border_color, width=2)
    
    draw.text((margin_x + 50, sec3_y0 + 45), "3. 인플루언서 공동구매", fill=text_dark, font=fonts['sec_title'])
    
    tag3_text = "커머스 연계 및 실질 매출 증대 세팅"
    bbox_tag3 = fonts['sec_tag'].getbbox(tag3_text)
    draw.text((width - margin_x - 50 - (bbox_tag3[2] - bbox_tag3[0]), sec3_y0 + 58), tag3_text, fill=text_sub, font=fonts['sec_tag'])
    
    draw.line([(margin_x + 50, sec3_y0 + 115), (width - margin_x - 50, sec3_y0 + 115)], fill=border_color, width=2)

    bullets3 = [
        "• 대상 기준: 팔로워 1만 이상 인플루언서부터 진행 권장",
        "• 기본 진행비: 250,000원 ~ (기본 매칭 및 운영 관리비)",
        "• 필수 조건: 시연용 제품 무상 제공 필수",
        "• 사전 진단: 상품 마진율, 카테고리, 브랜드 인지도에 대한 정밀한 사전 진단 후 진행"
    ]
    
    b3_y = sec3_y0 + 165
    for bullet_txt in bullets3:
        draw.text((margin_x + 60, b3_y), bullet_txt, fill=(40, 40, 50), font=fonts['bullet_txt'])
        b3_y += 102

    draw.text((margin_x + 50, sec3_y0 + sec3_h - 60), "* 사전 진단 결과에 따라 수수료율 및 진행 여부가 최종 결정됩니다.", fill=text_sub, font=fonts['footnote'])

    # ================= 5. 하단 CTA 버튼 =================
    btn_y0 = 2865
    btn_w, btn_h = 520, 110
    btn_x0 = (width - btn_w) // 2
    
    draw_rounded_rectangle(draw, (btn_x0, btn_y0, btn_x0 + btn_w, btn_y0 + btn_h), 55, fill=brand_gold)
    
    btn_txt = "💬  카카오톡 문의하기"
    bbox_btn = fonts['btn'].getbbox(btn_txt)
    btw = bbox_btn[2] - bbox_btn[0]
    draw.text((btn_x0 + (btn_w - btw) // 2, btn_y0 + 35), btn_txt, fill=(255, 255, 255), font=fonts['btn'])

    # 파일 안전 저장 (잠금 해제 대비 대체 경로 자동 적용)
    saved_path = save_image_safely(img, OUTPUT_IMG_PATH, dpi=dpi)
    return saved_path

# --- 7. 이미지 -> PDF 변환 ---
def compile_pdf(image_path, output_path):
    """생성된 고해상도 이미지 보드를 PDF로 변환"""
    if not image_path or not image_path.exists():
        return False
        
    logger.info("Converting Service Board Image to PDF...")
    try:
        c = canvas.Canvas(str(output_path), pagesize=A4)
        a4_w, a4_h = A4
        
        with Image.open(image_path) as img:
            img_w, img_h = img.size
            
            margin = 0.3 * inch
            avail_w = a4_w - (2 * margin)
            avail_h = a4_h - (2 * margin)
            
            scale = min(avail_w / img_w, avail_h / img_h)
            draw_w = img_w * scale
            draw_h = img_h * scale
            
            x_centered = (a4_w - draw_w) / 2
            y_centered = (a4_h - draw_h) / 2
            
            c.drawImage(str(image_path), x_centered, y_centered, width=draw_w, height=draw_h, preserveAspectRatio=True, mask='auto')
            c.showPage()
            
        c.save()
        logger.info(f"PDF successfully created: {output_path}")
        return True
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return False

# --- 8. 메인 실행 흐름 ---
if __name__ == "__main__":
    logger.info("=== Start ADplanters Production Pipeline ===")
    
    font_path = ensure_korean_font()
    
    if font_path:
        board_img = generate_service_board(font_path)
        if board_img:
            success = compile_pdf(board_img, OUTPUT_PDF_PATH)
            if success:
                logger.info("=== Process Finished Successfully! ===")
                logger.info(f"Generated Image: {board_img.name}")
                logger.info(f"Generated PDF: {OUTPUT_PDF_PATH.name}")
            else:
                logger.error("PDF Compilation Failed.")
        else:
            logger.critical("Board Image Generation Failed.")
    else:
        logger.critical("Font setup failed.")