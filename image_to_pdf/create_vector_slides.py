import os

def create_true_vector_slides():
    # 공통으로 사용되는 기본 HTML/CSS 템플릿
    base_html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide {slide_num}</title>
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #111; }}
            
            .slide {{
                width: 1280px; height: 720px;
                background: linear-gradient(135deg, #05051a 0%, #0a0a2a 40%, #020211 100%);
                position: relative; overflow: hidden;
                font-family: 'Pretendard', sans-serif;
                box-shadow: 0 0 20px rgba(0,0,0,0.8);
            }}

            /* 빛 번짐 (Neon Glow) 효과 배경 */
            .glow-top-left {{ position: absolute; top: -100px; left: -100px; width: 400px; height: 400px; background: radial-gradient(circle, rgba(100,50,255,0.3) 0%, rgba(0,0,0,0) 70%); filter: blur(40px); z-index: 1; }}
            .glow-bottom-right {{ position: absolute; bottom: -150px; right: -100px; width: 600px; height: 500px; background: radial-gradient(circle, rgba(0,255,255,0.15) 0%, rgba(0,0,0,0) 70%); filter: blur(50px); z-index: 1; }}
            .glow-line {{ position: absolute; background: linear-gradient(to right, transparent, #00ffff, transparent); height: 2px; width: 100%; transform: rotate(-45deg); opacity: 0.2; }}

            /* 로고 영역 */
            .logo-container {{ position: absolute; top: 30px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; display: flex; align-items: center; gap: 5px; }}
            .logo-arc {{ width: 20px; height: 15px; border-top: 3px solid #f97316; border-left: 3px solid #f97316; border-radius: 20px 0 0 0; margin-bottom: 10px; }}
            .logo-text {{ color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: 1px; }}
            .logo-sub {{ color: #888; font-size: 10px; font-weight: 400; letter-spacing: 2px; display: block; margin-top: -3px; }}

            /* 우측 상단 슬라이드 번호 */
            .slide-number {{ position: absolute; top: 30px; right: 50px; color: rgba(255,255,255,0.2); font-size: 80px; font-weight: 900; z-index: 10; }}

            /* 하단 네온 버튼 */
            .bottom-btn {{
                position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
                border: 2px solid #00ffff; border-radius: 30px;
                padding: 15px 40px; color: #fff; font-size: 22px; font-weight: bold;
                background: rgba(0,0,0,0.6);
                box-shadow: 0 0 15px rgba(0,255,255,0.4), inset 0 0 10px rgba(0,255,255,0.2);
                z-index: 10; text-shadow: 0 0 5px #00ffff;
            }}
            
            .bottom-btn-filled {{
                background: linear-gradient(90deg, #00ffff, #ff00ff); border: none; box-shadow: 0 0 20px rgba(255,0,255,0.5); text-shadow: none; color: #fff;
            }}

            /* 공통 텍스트 스타일 */
            .title-center {{ position: absolute; top: 130px; width: 100%; text-align: center; color: #fff; font-size: 48px; font-weight: 800; line-height: 1.3; z-index: 10; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }}
            
            /* 디바이스 목업 (벡터 UI) */
            .device-phone {{ position: absolute; width: 220px; height: 460px; background: #fff; border-radius: 30px; border: 6px solid #333; box-shadow: -10px 10px 30px rgba(0,0,0,0.6); z-index: 5; overflow: hidden; }}
            .device-phone::before {{ content:''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 100px; height: 20px; background: #333; border-radius: 0 0 10px 10px; }} /* 노치 */
            .device-tablet {{ position: absolute; width: 400px; height: 300px; background: #fff; border-radius: 20px; border: 6px solid #333; box-shadow: -10px 10px 30px rgba(0,0,0,0.6); z-index: 4; overflow: hidden; }}
            
            /* 목업 내부 가짜 UI (벡터) */
            .ui-skeleton-img {{ width: 100%; height: 200px; background: linear-gradient(135deg, #e0e0e0, #f5f5f5); display: flex; justify-content: center; align-items: center; font-size: 50px; }}
            .ui-skeleton-text {{ width: 80%; height: 10px; background: #ddd; margin: 10px auto; border-radius: 5px; }}
            .ui-skeleton-text.short {{ width: 50%; margin-left: 10%; }}
            
            {custom_css}
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 배경 효과 -->
            <div class="glow-top-left"></div>
            <div class="glow-bottom-right"></div>
            <div class="glow-line" style="top: 20%; left: -20%;"></div>
            <div class="glow-line" style="top: 80%; left: 50%;"></div>
            
            <!-- 공통 헤더 -->
            <div class="logo-container">
                <div class="logo-arc"></div>
                <div>
                    <div class="logo-text">ADPLANTERS</div>
                    <div class="logo-sub">GENTLE STUDIO</div>
                </div>
            </div>
            <div class="slide-number">{slide_num}</div>
            
            <!-- 슬라이드별 커스텀 콘텐츠 -->
            {slide_content}
        </div>
    </body>
    </html>
    """

    # 슬라이드 2 데이터
    slide2_css = """
        .s2-title {{ top: 120px; }}
        .s2-text-left {{ position: absolute; top: 320px; left: 100px; color: #fff; font-size: 32px; font-weight: 500; line-height: 1.5; z-index: 10; }}
        .s2-text-left span {{ color: #aaa; }}
        .s2-tablet {{ top: 280px; right: 100px; transform: rotate(5deg); }}
        .s2-phone {{ top: 250px; right: 450px; }}
        .s2-search-bar {{ width: 80%; height: 30px; border-radius: 15px; border: 1px solid #ccc; margin: 30px auto 10px; display: flex; align-items: center; padding: 0 10px; font-size: 12px; color: #666; }}
    """
    slide2_content = """
        <div class="title-center s2-title">사는 사람만 찾아서 매칭합니다<br>확실한 구매 전환율</div>
        <div class="s2-text-left">네이버와 구글의 알고리즘을 뚫는<br>정밀 타겟팅으로,<br><br>낭비 없는 효율적인 🔍<br>키워드 광고를<br>경험하세요.</div>
        
        <div class="device-tablet s2-tablet">
            <div style="text-align:center; padding: 20px; font-size: 24px; font-weight: bold; color: #4285F4;">Google</div>
            <div class="s2-search-bar">🔍 검색어를 입력하세요</div>
            <div class="ui-skeleton-text"></div><div class="ui-skeleton-text short"></div>
            <div class="ui-skeleton-text"></div><div class="ui-skeleton-text short"></div>
        </div>
        
        <div class="device-phone s2-phone">
            <div style="padding: 40px 15px 10px; border-bottom: 1px solid #eee; font-size: 12px; font-weight: bold;">Naver 파워링크</div>
            <div style="padding: 15px;">
                <div style="font-weight: bold; color: #000; font-size: 14px; margin-bottom: 5px;">프리미엄 타겟팅 광고</div>
                <div style="color: #00c73c; font-size: 10px; margin-bottom: 5px;">adplanters.com</div>
                <div class="ui-skeleton-text" style="width: 100%; margin: 5px 0;"></div>
                <div class="ui-skeleton-text" style="width: 70%; margin: 5px 0;"></div>
            </div>
        </div>
        
        <div class="bottom-btn">지금 상담 시 무료 진단 제공</div>
    """

    # 슬라이드 3 데이터
    slide3_css = """
        .s3-text-left {{ position: absolute; top: 300px; left: 100px; color: #fff; font-size: 28px; font-weight: 500; line-height: 2; z-index: 10; }}
        .s3-text-left li {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
        .s3-icon {{ font-size: 30px; }}
        .s3-phone1 {{ top: 250px; right: 350px; z-index: 6; }}
        .s3-phone2 {{ top: 350px; right: 100px; z-index: 5; background: #f0f0f0; }}
    """
    slide3_content = """
        <div class="title-center">피드를 멈추게 하는 비주얼<br>매출로 이어지는 타겟팅</div>
        <div class="s3-text-left">
            <div style="margin-bottom: 20px;">시선을 사로잡는 감각적인 소재와</div>
            <li><span class="s3-icon">📱</span> scroll stop</li>
            <li><span class="s3-icon">📊</span> engagement metrics</li>
            <li><span class="s3-icon">🏷️</span> shoppable feed</li>
        </div>
        
        <div class="device-phone s3-phone1">
            <div class="ui-skeleton-img" style="height: 100%; background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);">📸</div>
            <div style="position: absolute; bottom: 20px; left: 20px; color: white; text-shadow: 0 0 5px black;">
                <div style="font-weight: bold; font-size: 14px;">@adplanters</div>
                <div style="font-size: 12px;">제품 사용 후기 영상</div>
            </div>
        </div>
        
        <div class="device-phone s3-phone2">
            <div style="padding: 30px 10px 10px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #ccc;">
                <div style="width: 30px; height: 30px; background: #ccc; border-radius: 50%;"></div>
                <div class="ui-skeleton-text" style="margin: 0; width: 100px;"></div>
            </div>
            <div class="ui-skeleton-img" style="height: 250px;">🖼️</div>
            <div style="padding: 10px;">
                <div style="font-size: 20px;">❤️ 💬 ↗️</div>
            </div>
        </div>
        
        <div class="bottom-btn">지금 상담 시 무료 진단 제공</div>
    """

    # 슬라이드 4 데이터
    slide4_css = """
        .s4-text-left {{ position: absolute; top: 320px; left: 100px; color: #fff; font-size: 30px; font-weight: 500; line-height: 1.8; z-index: 10; }}
        .s4-icon {{ font-size: 35px; vertical-align: middle; }}
        .s4-phone1 {{ top: 250px; right: 500px; transform: rotate(-5deg); z-index: 5; }}
        .s4-phone2 {{ top: 220px; right: 280px; z-index: 6; }}
        .s4-phone3 {{ top: 280px; right: 50px; transform: rotate(5deg); z-index: 4; }}
    """
    slide4_content = """
        <div class="title-center">진정성 있는 확산<br>자연스러운 팬덤을 만듭니다</div>
        <div class="s4-text-left">
            브랜드에 가장 잘 맞는<br>최적의 인플루언서 매칭으로<br><br>
            <div><span class="s4-icon">🤝</span> like 협찬</div>
            <div><span class="s4-icon">🔗</span> genuine connection</div>
        </div>
        
        <div class="device-phone s4-phone1"><div class="ui-skeleton-img" style="height:100%; background: #e0f7fa;">👧</div></div>
        <div class="device-phone s4-phone2"><div class="ui-skeleton-img" style="height:100%; background: #ffe0b2;">👩</div></div>
        <div class="device-phone s4-phone3"><div class="ui-skeleton-img" style="height:100%; background: #f8bbd0;">👱‍♀️</div></div>
        
        <div class="bottom-btn">지금 상담 시 무료 진단 제공</div>
    """

    # 슬라이드 5 데이터
    slide5_css = """
        .s5-text-right {{ position: absolute; top: 320px; right: 100px; color: #fff; font-size: 26px; font-weight: 500; line-height: 2.2; z-index: 10; }}
        .s5-icon {{ font-size: 30px; vertical-align: middle; margin-right: 15px; }}
        .s5-tablet {{ top: 250px; left: 100px; z-index: 4; }}
        .s5-phone {{ top: 220px; left: 350px; z-index: 5; background: #111; }}
    """
    slide5_content = """
        <div class="title-center">고객이 머무는 페이지<br>지갑을 여는 영상 콘텐츠</div>
        
        <div class="device-tablet s5-tablet">
            <div style="padding: 10px; border-bottom: 1px solid #eee; display: flex; gap: 5px;">
                <div style="width:10px; height:10px; border-radius:50%; background:#ff5f56;"></div>
                <div style="width:10px; height:10px; border-radius:50%; background:#ffbd2e;"></div>
                <div style="width:10px; height:10px; border-radius:50%; background:#27c93f;"></div>
            </div>
            <div style="display:flex; padding: 20px; gap: 20px;">
                <div class="ui-skeleton-img" style="width: 150px; height: 150px; border-radius: 10px;">⌚</div>
                <div style="flex: 1;">
                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">프리미엄 워치</div>
                    <div class="ui-skeleton-text" style="width: 100%; margin: 5px 0;"></div>
                    <div class="ui-skeleton-text" style="width: 100%; margin: 5px 0;"></div>
                    <div class="ui-skeleton-text" style="width: 60%; margin: 5px 0;"></div>
                </div>
            </div>
        </div>
        
        <div class="device-phone s5-phone">
            <div class="ui-skeleton-img" style="height: 100%; background: #222; color: white;">▶️ Video</div>
            <div style="position: absolute; bottom: 30px; left: 10%; width: 80%; height: 40px; background: #ff5555; color: white; border-radius: 20px; display: flex; justify-content: center; align-items: center; font-weight: bold;">구매하기</div>
        </div>

        <div class="s5-text-right">
            <div><span class="s5-icon">▶️</span> 몰입도 높은 브랜드 영상부터</div>
            <div><span class="s5-icon">⏱️</span> 이탈률을 줄이고</div>
            <div><span class="s5-icon">↪️</span> 구매를 설득하는 고효율</div>
            <div><span class="s5-icon">🖱️</span> 웹·상세페이지 제작까지</div>
        </div>
        
        <div class="bottom-btn">지금 상담 시 무료 진단 제공</div>
    """

    # 슬라이드 6 데이터
    slide6_css = """
        .s6-text-left {{ position: absolute; top: 320px; left: 100px; color: #fff; font-size: 32px; font-weight: 500; line-height: 1.8; z-index: 10; }}
        .s6-text-left span {{ color: #00ffff; font-weight: bold; }}
        .s6-graphics {{ position: absolute; top: 250px; right: 100px; width: 450px; height: 350px; z-index: 5; position: relative; }}
        .s6-emoji-large {{ position: absolute; font-size: 150px; bottom: 0; right: 100px; filter: drop-shadow(0 10px 10px rgba(0,0,0,0.5)); z-index: 6; }}
        .s6-doc {{ position: absolute; top: 20px; right: 200px; width: 180px; height: 220px; background: #fff; border-radius: 10px; padding: 15px; box-shadow: -5px 5px 15px rgba(0,0,0,0.3); transform: rotate(-10deg); z-index: 4; }}
        .s6-badge {{ position: absolute; width: 60px; height: 60px; background: linear-gradient(135deg, #00ffff, #0088ff); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 30px; box-shadow: 0 5px 10px rgba(0,0,0,0.5); z-index: 7; }}
    """
    slide6_content = """
        <div class="title-center">성공하는 브랜드의 뒤편엔<br>항상 우리가 있습니다</div>
        
        <div class="s6-text-left">
            지금, 우리 브랜드에 딱 맞는<br>
            <span>맞춤형 마케팅 전략</span>을<br>
            무료로 상담받아보세요.
        </div>
        
        <div class="s6-graphics">
            <div class="s6-doc">
                <div style="font-size: 40px;">📈</div>
                <div class="ui-skeleton-text" style="width: 100%; margin: 15px 0 5px;"></div>
                <div class="ui-skeleton-text" style="width: 80%; margin: 5px 0;"></div>
                <div style="display: flex; gap: 5px; margin-top: 20px; align-items: flex-end; height: 60px; border-bottom: 2px solid #ddd;">
                    <div style="width: 30px; height: 40%; background: #4285F4;"></div>
                    <div style="width: 30px; height: 60%; background: #34A853;"></div>
                    <div style="width: 30px; height: 90%; background: #FBBC05;"></div>
                </div>
            </div>
            <div class="s6-badge" style="top: 150px; right: 120px;">📞</div>
            <div class="s6-badge" style="top: 50px; right: -20px; background: linear-gradient(135deg, #8800ff, #ff00ff);">🏁</div>
            <div class="s6-emoji-large">🤝</div>
        </div>
        
        <div class="bottom-btn bottom-btn-filled">문의하기 (프로필 링크 클릭)</div>
    """

    # 슬라이드 데이터 매핑
    slides_data = [
        ("Slide_2.html", 2, slide2_css, slide2_content),
        ("Slide_3.html", 3, slide3_css, slide3_content),
        ("Slide_4.html", 4, slide4_css, slide4_content),
        ("Slide_5.html", 5, slide5_css, slide5_content),
        ("Slide_6.html", 6, slide6_css, slide6_content),
    ]

    # 각 파일 생성
    for filename, num, css, content in slides_data:
        html_output = base_html.format(
            slide_num=num,
            custom_css=css,
            slide_content=content
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"[완료] {filename} 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_true_vector_slides()
    print("\\n🎉 모든 슬라이드(Slice 2 ~ 6) 변환이 완료되었습니다!")
    print("--------------------------------------------------")
    print("💡 [고해상도 PDF 추출 가이드]")
    print("1. 생성된 HTML 파일(Slide_2.html 등)을 크롬(Chrome)이나 엣지(Edge) 브라우저로 엽니다.")
    print("2. [Ctrl + P] 또는 우클릭 후 '인쇄'를 누릅니다.")
    print("3. 대상을 'PDF로 저장'으로 변경합니다.")
    print("4. 설정에서 '배경 그래픽(Background graphics)'을 반드시 체크합니다.")
    print("5. 저장을 누르시면 무한 확대해도 폰트와 그라데이션이 깨지지 않는 완벽한 벡터 PDF를 얻을 수 있습니다.")