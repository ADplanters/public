import os
from playwright.sync_api import sync_playwright

def convert_html_slides_to_image():
    # 현재 폴더의 모든 HTML 파일 탐색
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    if not html_files:
        print("❌ 변환할 HTML 파일이 없습니다.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # 2배 해상도(2560x1440 4K급) 출력을 위해 device_scale_factor=2 설정
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            device_scale_factor=2
        )
        page = context.new_page()
        
        for html_file in html_files:
            file_path = f"file://{os.path.abspath(html_file)}"
            page.goto(file_path)
            
            # 파일명 설정
            output_png = html_file.replace('.html', '.png')
            output_jpg = html_file.replace('.html', '.jpg')
            
            # PNG 저장 (투명도/고품질 유지)
            page.screenshot(path=output_png)
            
            # JPG 저장 (필요 시 사용)
            page.screenshot(path=output_jpg, type="jpeg", quality=95)
            
            print(f"✅ 변환 완료: {html_file} -> {output_png}, {output_jpg}")
            
        browser.close()

if __name__ == "__main__":
    convert_html_slides_to_image()