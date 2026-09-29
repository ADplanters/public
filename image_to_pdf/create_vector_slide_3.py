import os

def create_vector_slide_3():
    output_filename = "Vector_Slide_3.html"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide 3 - 고해상도 복원</title>
        <style>
            /* 1. 기본 폰트 세팅 */
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; background-color: #222; 
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
            .bg-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.35; }
            
            /* 로고 및 페이지 번호 */
            .header-logo { position: absolute; top: 30px; left: 50%; transform: translateX(-50%); text-align: center; z-index: 10; }
            .logo-main { font-size: 26px; font-weight: 800; color: #ff8c00; letter-spacing: 2px; }
            .logo-sub { font-size: 13px; font-weight: 400; color: #aaa; letter-spacing: 4px; display: block; margin-top: 5px; }
            .page-num { position: absolute; top: 30px; right: 50px; font-size: 65px; font-weight: 900; color: rgba(255,255,255,0.2); z-index: 10; }
            
            /* 메인 타이틀 */
            .content-left { position: absolute; top: 140px; left: 100px; z-index: 10; }
            .title-1 { font-size: 46px; font-weight: 800; margin-bottom: 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.8); letter-spacing: -1px; }
            .title-2 { font-size: 46px; font-weight: 800; text-shadow: 0 2px 8px rgba(0,0,0,0.8); letter-spacing: -1px; }
            
            /* 좌측 리스트 그룹 */
            .feature-group { position: absolute; top: 320px; left: 100px; z-index: 10; }
            .feature-intro { font-size: 24px; color: #d0d0d0; margin-bottom: 25px; font-weight: 400; }
            
            .feature-item { display: flex; align-items: center; margin-bottom: 20px; }
            .feature-icon {
                width: 42px; height: 42px; background: rgba(0, 255, 255, 0.08); border: 1.5px solid #00e5ff;
                border-radius: 10px; display: flex; justify-content: center; align-items: center;
                margin-right: 18px; box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
            }
            .feature-text { font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; }
            
            /* 우측 목업 (스마트폰 2개) */
            .mockup-container { position: absolute; top: 220px; right: 90px; width: 480px; height: 400px; z-index: 5; }
            
            /* 스마트폰 프레임 공통 */
            .phone-frame {
                background: #111; border: 3px solid #333; border-radius: 32px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.7); overflow: hidden; position: absolute; box-sizing: border-box;
            }
            
            /* 1. 좌측 폰 (릴스 / 숏폼 비디오 UI) */
            .phone-left { width: 210px; height: 380px; top: 0; left: 30px; z-index: 2; transform: rotate(-2deg); }
            .reels-screen {
                width: 100%; height: 100%; background: linear-gradient(180deg, #2b1055 0%, #7597de 100%);
                position: relative; padding: 12px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;
            }
            .reels-notch { width: 60px; height: 10px; background: #000; border-radius: 10px; margin: 0 auto; }
            
            /* 비디오 그래픽 오버레이 */
            .reels-content-box {
                position: absolute; top: 50px; left: 20px; right: 20px; height: 200px;
                background: rgba(255,255,255,0.15); backdrop-filter: blur(5px); border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.3); display: flex; flex-direction: column; justify-content: center; align-items: center;
            }
            .reels-avatar { width: 50px; height: 50px; border-radius: 50%; background: #ff8c00; margin-bottom: 10px; border: 2px solid #fff; }
            .reels-play-btn { width: 30px; height: 30px; fill: white; opacity: 0.9; }
            
            .reels-side-bar { position: absolute; right: 10px; bottom: 40px; display: flex; flex-direction: column; gap: 14px; align-items: center; }
            .side-icon { width: 18px; height: 18px; fill: white; opacity: 0.9; }
            
            .reels-bottom-info { position: absolute; bottom: 15px; left: 12px; right: 50px; }
            .reels-user { font-size: 11px; font-weight: 700; color: #fff; margin-bottom: 4px; }
            .reels-desc { font-size: 9px; color: rgba(255,255,255,0.8); }

            /* 2. 우측 폰 (피드 / 쇼퍼블 커머스 UI) */
            .phone-right { width: 210px; height: 370px; top: 20px; right: 20px; z-index: 1; }
            .feed-screen { width: 100%; height: 100%; background: #ffffff; position: relative; font-family: sans-serif; }
            .feed-header { height: 30px; border-bottom: 1px solid #eee; display: flex; align-items: center; padding: 0 10px; justify-content: space-between; }
            .feed-logo { font-size: 10px; font-weight: 800; color: #1877f2; }
            
            .feed-post { padding: 8px; }
            .feed-user-bar { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
            .feed-user-img { width: 18px; height: 18px; background: #00e5ff; border-radius: 50%; }
            .feed-user-name { font-size: 9px; font-weight: 700; color: #333; }
            
            .feed-image-box { width: 100%; height: 120px; background: #f0f2f5; border-radius: 6px; position: relative; overflow: hidden; display: flex; justify-content: center; align-items: center; }
            .feed-tag-badge {
                position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.7); color: #fff;
                font-size: 7px; padding: 3px 6px; border-radius: 4px; font-weight: 600; display: flex; align-items: center; gap: 3px;
            }
            .feed-post-text { font-size: 8px; color: #444; margin-top: 6px; line-height: 1.3; }

            /* 하단 네온 버튼 */
            .neon-button {
                position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%);
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
            
            <!-- 2. 상단 헤더 & 로고 -->
            <div class="header-logo">
                <div class="logo-main">ADPLANTERS</div>
                <div class="logo-sub">GENTLE STUDIO</div>
            </div>
            <div class="page-num">3</div>
            
            <!-- 3. 메인 타이틀 -->
            <div class="content-left">
                <div class="title-1">피드를 멈추게 하는 비주얼</div>
                <div class="title-2">매출로 이어지는 타겟팅</div>
            </div>
            
            <!-- 4. 좌측 포인트 리스트 (아이콘 + 텍스트) -->
            <div class="feature-group">
                <div class="feature-intro">시선을 사로잡는 감각적인 소재와</div>
                
                <!-- scroll stop -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2">
                            <rect x="5" y="2" width="14" height="20" rx="3"></rect>
                            <line x1="12" y1="18" x2="12" y2="18.01"></line>
                            <path d="M12 6v6m0 0l-2-2m2 2l2-2"></path>
                        </svg>
                    </div>
                    <div class="feature-text">scroll stop</div>
                </div>
                
                <!-- engagement metrics -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                            <polyline points="4 8 10 2 14 6 20 0"></polyline>
                        </svg>
                    </div>
                    <div class="feature-text">engagement metrics</div>
                </div>
                
                <!-- shoppable feed -->
                <div class="feature-item">
                    <div class="feature-icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2">
                            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                            <line x1="7" y1="7" x2="7.01" y2="7"></line>
                        </svg>
                    </div>
                    <div class="feature-text">shoppable feed</div>
                </div>
            </div>
            
            <!-- 5. 우측 모바일 목업 그룹 -->
            <div class="mockup-container">
                
                <!-- 좌측 스마트폰: 릴스/숏폼 UI -->
                <div class="phone-frame phone-left">
                    <div class="reels-screen">
                        <div class="reels-notch"></div>
                        <div class="reels-content-box">
                            <div class="reels-avatar"></div>
                            <svg class="reels-play-btn" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        </div>
                        <div class="reels-side-bar">
                            <svg class="side-icon" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                            <svg class="side-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            <svg class="side-icon" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                        </div>
                        <div class="reels-bottom-info">
                            <div class="reels-user">@adplanters_official</div>
                            <div class="reels-desc">구매 전환율 300% 상승 비결 공개!</div>
                        </div>
                    </div>
                </div>

                <!-- 우측 스마트폰: 피드/쇼퍼블 UI -->
                <div class="phone-frame phone-right">
                    <div class="feed-screen">
                        <div class="feed-header">
                            <div class="feed-logo">Social Feed</div>
                        </div>
                        <div class="feed-post">
                            <div class="feed-user-bar">
                                <div class="feed-user-img"></div>
                                <div class="feed-user-name">ADPLANTERS</div>
                            </div>
                            <div class="feed-image-box">
                                <div style="width:50px; height:50px; background:#e0e0e0; border-radius:8px;"></div>
                                <div class="feed-tag-badge">
                                    🛍️ 제품 보기
                                </div>
                            </div>
                            <div class="feed-post-text">
                                <strong>시선을 사로잡는 비주얼!</strong><br>
                                실질적인 구매로 연결되는 프리미엄 쇼퍼블 피드 광고.
                            </div>
                        </div>
                    </div>
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
        
    print(f"✅ 벡터 복원 완료! '{output_filename}' 파일이 생성되었습니다.")

if __name__ == "__main__":
    create_vector_slide_3()