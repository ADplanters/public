import os

def create_vector_slide_5():
    output_filename = "Vector_Slide_5.html"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide 5 - 웹·상세페이지 및 영상 콘텐츠</title>
        <style>
            /* 1. 기본 폰트 세팅 (Pretendard) */
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; background-color: #1a1a1a; 
            }
            
            /* 2. 슬라이드 캔버스 (1280x720 16:9) */
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
            .bg-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.35; }
            
            /* 헤더 로고 & 페이지 번호 */
            .header-logo { position: absolute; top: 25px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; }
            .logo-main { font-size: 24px; font-weight: 800; color: #ff8c00; letter-spacing: 2px; }
            .logo-sub { font-size: 12px; font-weight: 400; color: #aaa; letter-spacing: 4px; display: block; margin-top: 3px; }
            .page-num { position: absolute; top: 25px; right: 50px; font-size: 65px; font-weight: 900; color: rgba(255,255,255,0.2); z-index: 10; }
            
            /* 메인 슬로건 (상단 정중앙 2줄) */
            .title-center {
                position: absolute; top: 110px; left: 50%; transform: translateX(-50%);
                text-align: center; z-index: 10; width: 100%;
            }
            .title-1 { font-size: 48px; font-weight: 900; color: #ffffff; letter-spacing: -1px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); margin-bottom: 6px; }
            .title-2 { font-size: 48px; font-weight: 900; color: #ffffff; letter-spacing: -1px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }

            /* ==================================================
               좌측 디바이스 목업 (상세페이지 웹 + 영상 플레이어)
               ================================================== */
            .mockup-group { position: absolute; top: 240px; left: 70px; width: 580px; height: 390px; z-index: 5; }
            
            /* 1. 태블릿/웹 화면 (상세페이지 UI) */
            .web-tablet {
                width: 420px; height: 280px; background: #111; border: 3.5px solid #2d3245; border-radius: 16px;
                position: absolute; top: 20px; left: 0; box-shadow: 0 15px 35px rgba(0,0,0,0.7); overflow: hidden;
            }
            .web-screen { width: 100%; height: 100%; background: #ffffff; color: #222; display: flex; flex-direction: column; }
            
            /* 브라우저 상단바 */
            .web-browser-bar { height: 22px; background: #f1f3f5; border-bottom: 1px solid #e9ecef; display: flex; align-items: center; padding: 0 10px; gap: 6px; }
            .dot { width: 7px; height: 7px; border-radius: 50%; }
            .dot-red { background: #ff5f56; } .dot-yellow { background: #ffbd2e; } .dot-green { background: #27c93f; }
            .web-url-bar { background: #fff; border-radius: 4px; height: 12px; flex-grow: 1; margin: 0 10px; font-size: 7px; color: #888; display: flex; align-items: center; padding-left: 6px; border: 1px solid #dee2e6; }

            /* 웹 상세페이지 본문 */
            .web-body { display: flex; padding: 10px; gap: 12px; height: 100%; box-sizing: border-box; background: #fff; }
            .web-hero-img {
                flex: 1.1; background: linear-gradient(135deg, #1c1c1e 0%, #3a3a3c 100%); border-radius: 8px;
                display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; padding: 8px; position: relative;
            }
            .watch-graphic { font-size: 38px; filter: drop-shadow(0 5px 10px rgba(0,0,0,0.5)); }
            .hero-badge { position: absolute; top: 8px; left: 8px; background: #ff0055; color: white; font-size: 7px; font-weight: 800; padding: 2px 5px; border-radius: 4px; }
            
            .web-info { flex: 1.3; display: flex; flex-direction: column; justify-content: space-between; }
            .web-prod-title { font-size: 11px; font-weight: 800; color: #111; line-height: 1.2; }
            .web-prod-price { font-size: 11px; font-weight: 900; color: #ff0055; margin-top: 2px; }
            .web-prod-price span { font-size: 8px; color: #888; text-decoration: line-through; margin-left: 4px; font-weight: 400; }
            .web-stars { font-size: 8px; color: #ffb703; font-weight: 700; margin: 3px 0; }
            .web-opt-box { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 6px; font-size: 7px; color: #444; }
            .web-thumb-list { display: flex; gap: 4px; margin-top: 4px; }
            .web-thumb { width: 22px; height: 22px; background: #e9ecef; border-radius: 4px; border: 1px solid #ced4da; }

            /* 2. 앞쪽 스마트폰 (고효율 영상 플레이어 UI) */
            .phone-front {
                width: 190px; height: 350px; background: #090a0f; border: 3.5px solid #2d3245; border-radius: 32px;
                position: absolute; top: 0; right: 20px; z-index: 10;
                box-shadow: -10px 15px 35px rgba(0,0,0,0.85); overflow: hidden; box-sizing: border-box;
            }
            .phone-screen {
                width: 100%; height: 100%; background: linear-gradient(180deg, #10002b 0%, #240046 50%, #10002b 100%);
                position: relative; padding: 10px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;
            }
            .video-header { display: flex; justify-content: space-between; align-items: center; z-index: 2; }
            .video-tag { background: rgba(0, 229, 255, 0.2); border: 1px solid #00e5ff; color: #00e5ff; font-size: 7px; font-weight: 800; padding: 2px 6px; border-radius: 8px; }
            
            /* 중앙 비디오 플레이 아이콘 */
            .video-center { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); text-align: center; z-index: 2; }
            .play-btn-ring {
                width: 48px; height: 48px; border-radius: 50%; background: rgba(255, 0, 128, 0.4); border: 2px solid #ff0080;
                display: flex; justify-content: center; align-items: center; margin: 0 auto 8px;
                box-shadow: 0 0 20px rgba(255,0,128,0.8);
            }
            .play-icon { width: 0; height: 0; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-left: 14px solid #ffffff; margin-left: 3px; }
            .video-title { font-size: 9px; font-weight: 800; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }

            /* 비디오 타임라인 & CTA 버튼 */
            .video-bottom { z-index: 2; }
            .timeline-bar { width: 100%; height: 3px; background: rgba(255,255,255,0.2); border-radius: 2px; margin-bottom: 8px; position: relative; }
            .timeline-progress { width: 65%; height: 100%; background: #00e5ff; border-radius: 2px; }
            .video-cta-btn {
                width: 100%; background: linear-gradient(90deg, #ff007f, #7928ca); color: white; font-size: 9px; font-weight: 800;
                padding: 7px 0; text-align: center; border-radius: 8px; box-shadow: 0 4px 12px rgba(255,0,127,0.5);
            }

            /* ==================================================
               우측 포인트 리스트 (아이콘 + 텍스트)
               ================================================== */
            .content-right { position: absolute; top: 250px; right: 70px; width: 500px; z-index: 10; }
            
            .feature-item { display: flex; align-items: center; margin-bottom: 24px; }
            .feature-icon {
                width: 44px; height: 44px; background: rgba(0, 255, 255, 0.08); border: 1.5px solid #00e5ff;
                border-radius: 12px; display: flex; justify-content: center; align-items: center;
                margin-right: 18px; box-shadow: 0 0 12px rgba(0, 229, 255, 0.3); flex-shrink: 0;
            }
            .feature-text { font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; }

            /* 하단 네온 버튼 */
            .neon-button {
                position: absolute; bottom: 45px; left: 50%; transform: translateX(-50%);
                background: #060b26; border-radius: 40px; padding: 16px 50px;
                font-size: 26px; font-weight: 700; color: white; z-index: 10;
                box-shadow: 0 0 25px rgba(255, 0, 255, 0.6), inset 0 0 15px rgba(255, 0, 255, 0.3);
                border: none; cursor: pointer;
            }
            .neon-button::before {
                content: ''; position: absolute; top: -3px; left: -3px; right: -3px; bottom: -3px;
                border-radius: 43px; background: linear-gradient(135deg, #ff69b4, #ff0080); z-index: -1;
            }
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 1. 배경 그래픽 라인 (SVG) -->
            <svg class="bg-lines">
                <line x1="-100" y1="700" x2="1300" y2="0" stroke="#00ffff" stroke-width="2" />
                <line x1="-100" y1="550" x2="1300" y2="-150" stroke="#9d4edd" stroke-width="1.5" />
            </svg>
            
            <!-- 2. 헤더 로고 및 페이지 번호 -->
            <div class="header-logo">
                <div class="logo-main">ADPLANTERS</div>
                <div class="logo-sub">GENTLE STUDIO</div>
            </div>
            <div class="page-num">5</div>
            
            <!-- 3. 메인 슬로건 (상단 정중앙 2줄 배치) -->
            <div class="title-center">
                <div class="title-1">고객이 머무는 페이지</div>
                <div class="title-2">지갑을 여는 영상 콘텐츠</div>
            </div>
            
            <!-- 4. 좌측 디바이스 목업 그룹 -->
            <div class="mockup-group">
                
                <!-- 태블릿: 고퀄리티 브랜드 웹 상세페이지 UI -->
                <div class="web-tablet">
                    <div class="web-screen">
                        <div class="web-browser-bar">
                            <div class="dot dot-red"></div>
                            <div class="dot dot-yellow"></div>
                            <div class="dot dot-green"></div>
                            <div class="web-url-bar">https://adplanters.com/brand-store</div>
                        </div>
                        <div class="web-body">
                            <div class="web-hero-img">
                                <span class="hero-badge">BEST</span>
                                <div class="watch-graphic">⌚</div>
                                <div style="font-size:7px; font-weight:700; margin-top:4px;">SMART WATCH PRO</div>
                            </div>
                            <div class="web-info">
                                <div>
                                    <div class="web-prod-title">프리미엄 세라믹 워치 시리즈</div>
                                    <div class="web-stars">★★★★★ 4.9 (1,280)</div>
                                    <div class="web-prod-price">189,000원 <span>299,000원</span></div>
                                </div>
                                <div class="web-opt-box">
                                    <strong>구매 혜택:</strong> 무료배송 + 10% 쿠폰 적용 가능
                                </div>
                                <div>
                                    <div style="font-size:7px; color:#666; font-weight:700;">상세 이미지</div>
                                    <div class="web-thumb-list">
                                        <div class="web-thumb"></div>
                                        <div class="web-thumb"></div>
                                        <div class="web-thumb"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 스마트폰: 고효율 비디오 플레이어 UI -->
                <div class="phone-front">
                    <div class="phone-screen">
                        <div class="video-header">
                            <span class="video-tag">BRAND FILM</span>
                            <span style="font-size:8px; color:#aaa;">01:24</span>
                        </div>
                        
                        <div class="video-center">
                            <div class="play-btn-ring">
                                <div class="play-icon"></div>
                            </div>
                            <div class="video-title">지갑을 여는 몰입형 고효율 영상</div>
                        </div>
                        
                        <div class="video-bottom">
                            <div class="timeline-bar">
                                <div class="timeline-progress"></div>
                            </div>
                            <div class="video-cta-btn">지금 구매하고 혜택 받기 ></div>
                        </div>
                    </div>
                </div>

            </div>
            
            <!-- 5. 우측 포인트 리스트 (SVG 아이콘 적용) -->
            <div class="content-right">
                
                <!-- 1. 몰입도 높은 브랜드 영상부터 -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.2">
                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                    </div>
                    <div class="feature-text">몰입도 높은 브랜드 영상부터</div>
                </div>
                
                <!-- 2. 이탈률을 줄이고 -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                    </div>
                    <div class="feature-text">이탈률을 줄이고</div>
                </div>
                
                <!-- 3. 구매를 설득하는 고효율 -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.2">
                            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                            <polyline points="10 17 15 12 10 7"></polyline>
                            <line x1="15" y1="12" x2="3" y2="12"></line>
                        </svg>
                    </div>
                    <div class="feature-text">구매를 설득하는 고효율</div>
                </div>
                
                <!-- 4. 웹·상세페이지 제작까지 -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="3" y1="9" x2="21" y2="9"></line>
                            <line x1="9" y1="21" x2="9" y2="9"></line>
                        </svg>
                    </div>
                    <div class="feature-text">웹·상세페이지 제작까지</div>
                </div>

            </div>
            
            <!-- 6. 하단 네온 버튼 -->
            <button class="neon-button">지금 상담 시 무료 진단 제공</button>
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ 슬라이드 5 벡터 복원 완료! '{output_filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_vector_slide_5()