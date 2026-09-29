import os
from playwright.sync_api import sync_playwright

def convert_specific_html_slides():
    # 사용자의 폴더에 있는 6개 HTML 파일 지정
    target_files = [
        "Perfect_Vector_Slide.html",
        "Vector_Slide_2_Naver.html",
        "Vector_Slide_3_Creative.html",
        "Vector_Slide_4.html",
        "Vector_Slide_5.html",
        "Vector_Slide_6.html"
    ]
    
    # 존재하지 않는 파일 걸러내기 및 안내
    existing_files = [f for f in target_files if os.path.exists(f)]
    missing_files = set(target_files) - set(existing_files)
    
    if missing_files:
        print("⚠️ 다음 파일들은 현재 폴더에 존재하지 않아 스킵됩니다:")
        for mf in missing_files:
            print(f"   - {mf}")
        print("-" * 50)
        
    if not existing_files:
        print("❌ 변환할 대상을 찾을 수 없습니다. HTML 파일 위치를 확인해주세요.")
        return

    print("🚀 HTML 슬라이드를 고화질 PNG / JPG 이미지로 변환 시작합니다...\n")

    with sync_playwright() as p:
        # 헤드리스 크롬 브라우저 실행
        browser = p.chromium.launch()
        
        # 16:9 슬라이드 캔버스 기준 2배율(2560x1440 4K급 고해상도) 크기 세팅
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            device_scale_factor=2
        )
        page = context.new_page()
        
        for html_file in existing_files:
            file_path = f"file://{os.path.abspath(html_file)}"
            
            # 페이지 로드 및 폰트/그래픽 렌더링 완료 대기
            page.goto(file_path, wait_until="networkidle")
            
            # 출력할 이미지 파일명 정의
            base_name = os.path.splitext(html_file)[0]
            output_png = f"{base_name}.png"
            output_jpg = f"{base_name}.jpg"
            
            # 1. PNG 스크린샷 캡처 (고화질 선명도 보장)
            page.screenshot(path=output_png, full_page=True)
            
            # 2. JPG 스크린샷 캡처 (압축 품질 95%)
            page.screenshot(path=output_jpg, type="jpeg", quality=95, full_page=True)
            
            print(f"✅ 변환 성공:")
            print(f"   📄 HTML: {html_file}")
            print(f"   🖼️ PNG : {output_png}")
            print(f"   🖼️ JPG : {output_jpg}")
            print("-" * 50)
            
        browser.close()
        print("\n🎉 모든 슬라이드 이미지 변환 작업이 완료되었습니다!")

if __name__ == "__main__":
    convert_specific_html_slides()