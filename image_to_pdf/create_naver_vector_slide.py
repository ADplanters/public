import os

def create_naver_vector_slide():
    output_filename = "Vector_Slide_2_Naver.html"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide 2 - 네이버 UI 적용</title>
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
            
            /* 배경 네온 라인 (SVG) */
            .bg-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.3; }
            
            /* 로고 및 페이지 번호 */
            .header-logo { position: absolute; top: 30px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; }
            .logo-main { font-size: 26px; font-weight: 800; color: #ff8c00; letter-spacing: 2px; }
            .logo-sub { font-size: 13px; font-weight: 400; color: #aaa; letter-spacing: 4px; display: block; margin-top: 5px; }
            .page-num { position: absolute; top: 30px; right: 50px; font-size: 65px; font-weight: 900; color: rgba(255,255,255,0.2); z-index: 10; }
            
            /* 메인 텍스트 영역 */
            .content-left { position: absolute; top: 150px; left: 100px; z-index: 10; }
            .title-1 { font-size: 45px; font-weight: 800; margin-bottom: 5px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }
            .title-2 { font-size: 50px; font-weight: 900; margin-bottom: 50px; text-shadow: 0 2px 10px rgba(255,255,255,0.4); }
            
            .desc-group { position: absolute; top: 400px; left: 100px; font-size: 26px; line-height: 1.7; font-weight: 400; color: #d0d0d0; z-index: 10; }
            .desc-group span { font-weight: 700; color: white; }
            .desc-group strong { font-weight: 700; color: #ff8c00; }
            .magnifier-icon { display: inline-flex; align-items: center; vertical-align: middle; margin-right: 5px; }

            /* ==================================================
               목업 컨테이너 및 네이버 UI 디자인 시작
               ================================================== */
            .mockup-group { position: absolute; top: 410px; right: 80px; width: 480px; height: 350px; z-index: 5; }
            
            /* --- 1. 태블릿 (네이버 메인) --- */
            .tablet {
                width: 320px; height: 230px; background: #222; border: 4px solid #444; border-radius: 12px;
                position: absolute; top: 0; right: 0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.8);
                box-sizing: border-box; overflow: hidden;
            }
            .tablet-screen { background: #fff; width: 100%; height: 100%; position: relative; display: flex; flex-direction: column; }
            
            /* 네이버 헤더 & 검색창 */
            .naver-header { height: 35px; display: flex; align-items: center; padding: 0 12px; border-bottom: 1px solid #e4e8eb; }
            .naver-logo { color: #03c75a; font-weight: 900; font-size: 15px; margin-right: 12px; letter-spacing: -0.5px; }
            .naver-search { flex-grow: 1; height: 18px; border: 2px solid #03c75a; border-radius: 2px; position: relative; }
            .naver-search::after { content: ''; position: absolute; right: 3px; top: 2px; width: 10px; height: 10px; background: #03c75a; clip-path: polygon(100% 100%, 75% 100%, 40% 65%, 40% 40%, 65% 40%); }
            
            /* 네이버 GNB (메뉴) */
            .naver-nav { display: flex; gap: 10px; padding: 6px 12px; font-size: 8px; font-weight: 700; color: #333; border-bottom: 1px solid #e4e8eb; }
            .naver-nav span:first-child, .naver-nav span:nth-child(2) { color: #03c75a; }
            
            /* 네이버 본문 레이아웃 */
            .naver-body { display: flex; padding: 10px 12px; gap: 10px; height: 100%; background: #f5f6f8; }
            .naver-main-ad { flex: 2; background: #fff; border: 1px solid #dae1e6; border-radius: 4px; padding: 10px; position: relative; overflow: hidden; }
            .naver-main-ad-title { font-size: 10px; font-weight: 800; color: #333; margin-bottom: 5px; }
            .naver-main-ad-desc { font-size: 7px; color: #666; line-height: 1.4; }
            .naver-main-ad-highlight { display: inline-block; margin-top: 8px; color: #ff8c00; font-weight: 800; font-size: 10px; }
            
            .naver-side { flex: 1; display: flex; flex-direction: column; gap: 8px; }
            .naver-login { background: #fff; border: 1px solid #dae1e6; height: 45px; border-radius: 4px; display: flex; justify-content: center; align-items: center; }
            .naver-login-btn { background: #03c75a; color: white; padding: 4px 16px; border-radius: 2px; font-weight: bold; font-size: 8px; }
            .naver-widget { background: #fff; border: 1px solid #dae1e6; flex-grow: 1; border-radius: 4px; padding: 8px; }
            
            .fake-line { height: 4px; background: #e9ecef; margin-bottom: 4px; border-radius: 2px; }
            .fake-line.short { width: 60%; }

            /* --- 2. 스마트폰 (네이버 지도) --- */
            .phone {
                width: 155px; height: 320px; background: #222; border: 3px solid #444; border-radius: 24px;
                position: absolute; bottom: 0; left: 0;
                box-shadow: -10px 15px 30px rgba(0,0,0,0.8);
                box-sizing: border-box; padding: 8px;
            }
            .phone-screen { background: #eaf1f8; width: 100%; height: 100%; border-radius: 14px; position: relative; overflow: hidden; }
            
            /* 지도 배경 그래픽 (SVG) */
            .map-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
            
            /* 상단 검색바 플로팅 UI */
            .map-ui-top { position: absolute; top: 12px; left: 10px; right: 10px; background: #fff; height: 28px; border-radius: 14px; box-shadow: 0 3px 8px rgba(0,0,0,0.15); display: flex; align-items: center; padding: 0 12px; }
            .map-menu-icon { width: 12px; height: 10px; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; position: relative; margin-right: 8px; }
            .map-menu-icon::after { content: ''; position: absolute; top: 2.5px; width: 100%; height: 1.5px; background: #333; }
            .map-search-text { font-size: 9px; color: #999; font-weight: 500; }
            
            /* 마커 핀 */
            .map-pin { position: absolute; top: 45%; left: 50%; transform: translate(-50%, -100%); width: 22px; height: 28px; z-index: 5; }
            
            /* 하단 정보 바텀시트 */
            .map-ui-bottom { position: absolute; bottom: 0; left: 0; width: 100%; background: #fff; border-radius: 16px 16px 0 0; padding: 15px 12px 20px 12px; box-sizing: border-box; box-shadow: 0 -3px 15px rgba(0,0,0,0.15); }
            .map-title { font-size: 12px; font-weight: 900; color: #111; margin-bottom: 3px; }
            .map-subtitle { font-size: 8px; color: #777; margin-bottom: 10px; }
            .map-btn-group { display: flex; gap: 6px; }
            .map-btn { flex: 1; background: #f4f7f8; color: #333; font-size: 8px; text-align: center; padding: 6px 0; border-radius: 6px; font-weight: 800; border: 1px solid #eef1f4;}
            .map-btn.primary { background: #03c75a; color: white; border: none; }

            /* ==================================================
               네온 버튼
               ================================================== */
            .neon-button {
                position: absolute; bottom: 60px; left: 50%; transform: translateX(-50%);
                background: #060b26; border-radius: 40px; padding: 16px 50px;
                font-size: 26px; font-weight: 700; color: white; z-index: 10;
                box-shadow: 0 0 25px rgba(255, 0, 255, 0.6), inset 0 0 15px rgba(255, 0, 255, 0.3);
                cursor: pointer; border: none;
            }
            .neon-button::before {
                content: ''; position: absolute; top: -4px; left: -4px; right: -4px; bottom: -4px;
                border-radius: 44px; background: linear-gradient(135deg, #ff69b4, #ff0080); z-index: -1;
            }
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 1. 배경 그래픽 라인 -->
            <svg class="bg-lines">
                <line x1="-100" y1="700" x2="1300" y2="0" stroke="#00ffff" stroke-width="2" />
                <line x1="-100" y1="600" x2="1300" y2="-100" stroke="#9d4edd" stroke-width="1.5" />
            </svg>
            
            <!-- 2. 로고 및 번호 -->
            <div class="header-logo">
                <div class="logo-main">ADPLANTERS</div>
                <div class="logo-sub">GENTLE STUDIO</div>
            </div>
            <div class="page-num">2</div>
            
            <!-- 3. 좌측 텍스트 -->
            <div class="content-left">
                <div class="title-1">사는 사람만 찾아서 매칭합니다</div>
                <div class="title-2">확실한 구매 전환율</div>
            </div>
            
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
            
            <!-- 4. 네이버 UI 목업 그룹 -->
            <div class="mockup-group">
                
                <!-- 태블릿 : 네이버 메인 UI -->
                <div class="tablet">
                    <div class="tablet-screen">
                        <div class="naver-header">
                            <div class="naver-logo">NAVER</div>
                            <div class="naver-search"></div>
                        </div>
                        <div class="naver-nav">
                            <span>메일</span><span>카페</span><span>블로그</span><span>지식iN</span><span>쇼핑</span><span>Pay</span>
                        </div>
                        <div class="naver-body">
                            <div class="naver-main-ad">
                                <div class="naver-main-ad-title">ADPLANTERS 타겟팅</div>
                                <div class="naver-main-ad-desc">알고리즘을 뚫고 실구매자에게만 노출되는<br>스마트한 광고 솔루션을 만나보세요.</div>
                                <div class="naver-main-ad-highlight">무료 진단 받기 ></div>
                            </div>
                            <div class="naver-side">
                                <div class="naver-login">
                                    <div class="naver-login-btn">NAVER 로그인</div>
                                </div>
                                <div class="naver-widget">
                                    <div class="fake-line"></div>
                                    <div class="fake-line"></div>
                                    <div class="fake-line short"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 스마트폰 : 네이버 지도 UI -->
                <div class="phone">
                    <div class="phone-screen">
                        <!-- 지도 배경 그래픽 (녹지, 강, 도로) -->
                        <svg class="map-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                            <polygon points="0,0 45,0 35,35 0,25" fill="#d9ebd3" />
                            <polygon points="65,65 100,50 100,100 70,100" fill="#d9ebd3" />
                            <path d="M-10,40 Q 50,70 110,30 L 110,40 Q 50,80 -10,50 Z" fill="#b9d9ef" />
                            <line x1="25" y1="-10" x2="85" y2="110" stroke="#ffffff" stroke-width="4.5" />
                            <line x1="-10" y1="85" x2="110" y2="25" stroke="#ffffff" stroke-width="3" />
                            <line x1="30" y1="50" x2="100" y2="80" stroke="#f2ca74" stroke-width="2.5" />
                        </svg>
                        
                        <!-- 상단 검색바 -->
                        <div class="map-ui-top">
                            <div class="map-menu-icon"></div>
                            <div class="map-search-text">장소, 버스, 지하철, 도로 검색</div>
                        </div>
                        
                        <!-- 네이버 지도 스타일 빨간 핀 -->
                        <div class="map-pin">
                            <svg viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M12 0C5.37258 0 0 5.37258 0 12C0 19.5 12 30 12 30C12 30 24 19.5 24 12C24 5.37258 18.6274 0 12 0ZM12 17C9.23858 17 7 14.7614 7 12C7 9.23858 9.23858 7 12 7C14.7614 7 17 9.23858 17 12C17 14.7614 14.7614 17 12 17Z" fill="#ff3b30"/>
                                <circle cx="12" cy="12" r="4" fill="white"/>
                            </svg>
                        </div>
                        
                        <!-- 하단 장소 정보 패널 -->
                        <div class="map-ui-bottom">
                            <div class="map-title">애드플랜터스 본사</div>
                            <div class="map-subtitle">마케팅, 광고 대행업</div>
                            <div class="map-btn-group">
                                <div class="map-btn primary">도착</div>
                                <div class="map-btn">출발</div>
                                <div class="map-btn">저장</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 5. 하단 네온 버튼 -->
            <button class="neon-button">지금 상담 시 무료 진단 제공</button>
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ 네이버 UI 벡터 복원 완료! '{output_filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_naver_vector_slide()