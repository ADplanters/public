import os

def create_true_vector_slide():
    output_filename = "Vector_Slide_2.html"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide 2 - 고해상도 복원</title>
        <style>
            /* 1. 기본 폰트 세팅 (Pretendard) */
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; background-color: #333; 
            }
            
            /* 2. 슬라이드 본체 (1280x720 캔버스) */
            .slide {
                width: 1280px; height: 720px;
                background: linear-gradient(135deg, #020012 0%, #060b26 40%, #0f103b 100%);
                position: relative;
                font-family: 'Pretendard', sans-serif;
                color: #fff;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            }
            
            /* 3. 요소 배치 - 절대 위치 (position: absolute) */
            
            /* 배경 네온 라인 (SVG) */
            .bg-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.3; }
            
            /* 로고 */
            .header-logo { position: absolute; top: 30px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; }
            .logo-main { font-size: 26px; font-weight: 800; color: #ff8c00; letter-spacing: 2px; }
            .logo-sub { font-size: 13px; font-weight: 400; color: #aaa; letter-spacing: 4px; display: block; margin-top: 5px; }
            
            /* 페이지 번호 */
            .page-num { position: absolute; top: 30px; right: 50px; font-size: 65px; font-weight: 900; color: rgba(255,255,255,0.2); z-index: 10; }
            
            /* 메인 텍스트 컨테이너 */
            .content-left { position: absolute; top: 150px; left: 100px; z-index: 10; }
            .title-1 { font-size: 45px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }
            .title-2 { font-size: 50px; font-weight: 900; margin-bottom: 50px; text-shadow: 0 2px 10px rgba(255,255,255,0.4); }
            
            /* 설명 텍스트 */
            .desc-group { position: absolute; top: 400px; left: 100px; font-size: 26px; line-height: 1.7; font-weight: 400; color: #d0d0d0; z-index: 10; }
            .desc-group span { font-weight: 700; color: white; }
            .desc-group strong { font-weight: 700; color: #ff8c00; }
            .magnifier-icon { display: inline-flex; align-items: center; vertical-align: middle; margin-right: 5px; }

            /* 목업 컨테이너 */
            .mockup-group { position: absolute; top: 420px; right: 80px; width: 450px; height: 350px; z-index: 5; }
            
            /* 스마트폰 목업 */
            .phone {
                width: 160px; height: 330px; background: #000; border: 3px solid #333; border-radius: 25px;
                position: absolute; bottom: 0; left: 0;
                box-shadow: 0 10px 20px rgba(0,0,0,0.6);
                padding: 15px; box-sizing: border-box; font-size: 8px; color: #555;
            }
            .phone-screen { background: #fff; width: 100%; height: 100%; border-radius: 15px; overflow: hidden; position: relative; }
            .phone-header { height: 15px; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; padding: 0 8px; }
            .phone-content { padding: 8px; }
            .phone-text-1 { font-weight: 700; color: #000; font-size: 10px; margin-bottom: 4px; }
            .phone-text-2 { color: #888; }
            .phone-square { width: 100%; height: 40px; background: #eee; margin-top: 8px; border-radius: 5px; }

            /* 태블릿 목업 */
            .tablet {
                width: 300px; height: 210px; background: #000; border: 4px solid #333; border-radius: 15px;
                position: absolute; top: 0; right: 0;
                box-shadow: 0 10px 20px rgba(0,0,0,0.6);
                padding: 10px; box-sizing: border-box; font-size: 9px; color: #555;
            }
            .tablet-screen { background: #fff; width: 100%; height: 100%; border-radius: 8px; overflow: hidden; position: relative; }
            .tablet-header { height: 20px; background: #eee; display: flex; align-items: center; padding: 0 10px; }
            .tablet-logo { font-weight: 900; color: #4285F4; font-size: 11px; margin-right: 15px; }
            .tablet-search { width: 100px; height: 10px; background: #fff; border-radius: 10px; }
            .tablet-content { padding: 10px; }
            .tablet-rect { width: 100%; height: 8px; background: #f0f0f0; margin-bottom: 5px; border-radius: 2px; }
            .tablet-rect-short { width: 60%; }

            /* 네온 버튼 */
            .neon-button {
                position: absolute; bottom: 60px; left: 50%; transform: translateX(-50%);
                background: #060b26;
                border-radius: 40px;
                padding: 16px 50px;
                font-size: 26px; font-weight: 700;
                color: white;
                z-index: 10;
                box-shadow: 0 0 25px rgba(255, 0, 255, 0.6), inset 0 0 15px rgba(255, 0, 255, 0.3);
                cursor: pointer;
                border: none;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            /* 그라데이션 테두리 구현 */
            .neon-button::before {
                content: '';
                position: absolute;
                top: -4px; left: -4px; right: -4px; bottom: -4px;
                border-radius: 44px;
                background: linear-gradient(135deg, #ff69b4, #ff0080);
                z-index: -1;
            }
            .neon-button:hover {
                transform: translateX(-50%) scale(1.03);
                box-shadow: 0 0 35px rgba(255, 0, 255, 0.8), inset 0 0 20px rgba(255, 0, 255, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 배경 그래픽 라인 (SVG) -->
            <svg class="bg-lines">
                <line x1="-100" y1="700" x2="1300" y2="0" stroke="#00ffff" stroke-width="2" />
                <line x1="-100" y1="600" x2="1300" y2="-100" stroke="#9d4edd" stroke-width="1.5" />
            </svg>
            
            <!-- 로고 및 페이지 번호 -->
            <div class="header-logo">
                <div class="logo-main">ADPLANTERS</div>
                <div class="logo-sub">GENTLE STUDIO</div>
            </div>
            <div class="page-num">2</div>
            
            <!-- 메인 텍스트 -->
            <div class="content-left">
                <div class="title-1">사는 사람만 찾아서 매칭합니다</div>
                <div class="title-2">확실한 구매 전환율</div>
            </div>
            
            <!-- 설명 텍스트 -->
            <div class="desc-group">
                <p>네이버와 구글의 알고리즘을 뚫는<br><span>정밀 타겟팅으로,</span></p>
                <p>낭비 없는 효율적인
                    <span class="magnifier-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                    </span>
                    <strong>키워드 광고</strong>를<br>경험하세요.</p>
            </div>
            
            <!-- 목업 그래픽 -->
            <div class="mockup-group">
                <div class="tablet">
                    <div class="tablet-screen">
                        <div class="tablet-header">
                            <span class="tablet-logo">Google</span>
                            <div class="tablet-search"></div>
                        </div>
                        <div class="tablet-content">
                            <div class="tablet-rect"></div>
                            <div class="tablet-rect"></div>
                            <div class="tablet-rect"></div>
                            <div class="tablet-rect tablet-rect-short"></div>
                        </div>
                    </div>
                </div>
                <div class="phone">
                    <div class="phone-screen">
                        <div class="phone-header">
                            <span>Instagram</span>
                        </div>
                        <div class="phone-content">
                            <div class="phone-text-1">정밀 타겟팅</div>
                            <div class="phone-text-2">사는 사람만 찾아내는 알고리즘</div>
                            <div class="phone-square"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 네온 버튼 -->
            <button class="neon-button">지금 상담 시 무료 진단 제공</button>
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ 벡터 복원 완료! '{output_filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_true_vector_slide()