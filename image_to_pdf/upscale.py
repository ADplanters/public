import os

def create_true_vector_slide():
    output_filename = "Perfect_Vector_Slide.html"
    
    # 슬라이드의 모든 요소를 100% 벡터(텍스트, SVG 선, CSS 도형)로 새로 그리는 코드
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide</title>
        <style>
            /* 최고급 웹 폰트 (벡터) 적용 */
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; background-color: #111; 
            }
            
            /* 슬라이드 캔버스 세팅 */
            .slide {
                width: 1280px; height: 720px;
                background: linear-gradient(135deg, #020012 0%, #060b26 40%, #0f103b 100%);
                position: relative;
                font-family: 'Pretendard', sans-serif;
                color: #fff;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            }
            
            /* 배경 대각선 네온 효과 (SVG) */
            .bg-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; opacity: 0.4; }
            
            /* 로고 및 상단 번호 */
            .header { position: absolute; top: 40px; left: 0; width: 100%; text-align: center; z-index: 10; }
            .logo { font-size: 26px; font-weight: 800; color: #ff8c00; letter-spacing: 2px; }
            .logo span { color: #aaa; font-size: 13px; display: block; margin-top: 5px; font-weight: 400; letter-spacing: 4px; }
            .page-num { position: absolute; top: 40px; right: 50px; font-size: 65px; font-weight: 900; color: rgba(255,255,255,0.2); z-index: 10;}
            
            /* 좌측 텍스트 콘텐츠 (완벽한 벡터 폰트) */
            .content-left { position: absolute; top: 180px; left: 90px; z-index: 10; }
            .title-1 { font-size: 50px; font-weight: 700; margin-bottom: 10px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }
            .title-2 { font-size: 60px; font-weight: 900; margin-bottom: 50px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }
            .title-2 span { color: #e0f7fa; text-shadow: 0 0 15px rgba(0,255,255,0.6); }
            .desc { font-size: 28px; line-height: 1.6; font-weight: 400; color: #d0d0d0; }
            
            /* 하단 CTA 버튼 (CSS 벡터 도형) */
            .button {
                position: absolute; bottom: 60px; left: 50%; transform: translateX(-50%);
                border: 2px solid #00ffff;
                border-radius: 40px;
                padding: 16px 50px;
                font-size: 26px; font-weight: 700;
                color: #00ffff;
                box-shadow: 0 0 20px rgba(0,255,255,0.3), inset 0 0 15px rgba(0,255,255,0.2);
                background: rgba(0,30,50,0.4);
                z-index: 10;
            }
            
            /* 우측 원형 네온 다이어그램 */
            .diagram { position: absolute; top: 250px; right: 120px; width: 400px; height: 400px; z-index: 10; }
            .connectors { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
            
            .circle {
                position: absolute; border-radius: 50%;
                border: 2px solid #9d4edd;
                background: #11143a;
                display: flex; justify-content: center; align-items: center;
                box-shadow: 0 0 20px rgba(157,78,221,0.6);
            }
            .center-circle {
                width: 160px; height: 160px; top: 120px; left: 120px;
                border: 3px solid #00ffff; box-shadow: 0 0 40px rgba(0,255,255,0.5);
                background: #060b26;
            }
            .orbit { width: 80px; height: 80px; border-color: #00ffff; box-shadow: 0 0 15px rgba(0,255,255,0.4); }
            
            /* 노드 위치 계산 */
            .o1 { top: 0; left: 160px; }
            .o2 { top: 60px; left: 300px; }
            .o3 { top: 260px; left: 300px; }
            .o4 { top: 320px; left: 160px; }
            .o5 { top: 260px; left: 20px; }
            .o6 { top: 60px; left: 20px; }
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 배경 그래픽 -->
            <svg class="bg-lines">
                <line x1="-100" y1="700" x2="1300" y2="0" stroke="#00ffff" stroke-width="1.5" />
                <line x1="-100" y1="500" x2="1300" y2="-200" stroke="#9d4edd" stroke-width="1.5" />
            </svg>
            
            <div class="header">
                <div class="logo">ADPLANTERS<span>GENTLE STUDIO</span></div>
            </div>
            <div class="page-num">1</div>
            
            <div class="content-left">
                <div class="title-1">브랜드 성장의 시작</div>
                <div class="title-2">퍼포먼스부터 <span>브랜딩까지 한 번에</span></div>
                <div class="desc">
                    기획, 광고 운영, 콘텐츠 제작까지.<br>
                    당신의 비즈니스를 성공으로 이끄는<br>
                    올인원(All-in-One) IMC 파트너
                </div>
            </div>
            
            <div class="diagram">
                <!-- 다이어그램 연결선 (벡터) -->
                <svg class="connectors">
                    <line x1="200" y1="200" x2="200" y2="40" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                    <line x1="200" y1="200" x2="340" y2="100" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                    <line x1="200" y1="200" x2="340" y2="300" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                    <line x1="200" y1="200" x2="200" y2="360" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                    <line x1="200" y1="200" x2="60" y2="300" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                    <line x1="200" y1="200" x2="60" y2="100" stroke="#00ffff" stroke-width="2" opacity="0.6"/>
                </svg>
                
                <!-- 원형 노드 (이모지로 아이콘 대체) -->
                <div class="circle center-circle"><div style="font-size: 60px;">📈</div></div>
                <div class="circle orbit o1"><div style="font-size: 35px;">🛡️</div></div>
                <div class="circle orbit o2"><div style="font-size: 35px;">💻</div></div>
                <div class="circle orbit o3"><div style="font-size: 35px;">▶️</div></div>
                <div class="circle orbit o4"><div style="font-size: 35px;">🎯</div></div>
                <div class="circle orbit o5"><div style="font-size: 35px;">📷</div></div>
                <div class="circle orbit o6"><div style="font-size: 35px;">⚙️</div></div>
            </div>
            
            <div class="button">지금 상담 시 무료 진단 제공</div>
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"⭐ 100% 벡터 포맷 생성 완료! '{output_filename}' 파일이 생성되었습니다.")
    print("해당 HTML 파일을 더블클릭하여 웹 브라우저(크롬 등)로 열어보세요.")

if __name__ == "__main__":
    create_true_vector_slide()