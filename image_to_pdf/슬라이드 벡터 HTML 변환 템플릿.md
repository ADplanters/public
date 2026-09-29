# [GEM 참조용] 슬라이드 -> 벡터 HTML 재구성 파이썬 템플릿

이 파일은 복잡한 비트맵 슬라이드 이미지를 완벽한 벡터(HTML/CSS/SVG)로 변환할 때 기준이 되는 파이썬 템플릿입니다. GEM은 새로운 이미지를 분석할 때 이 구조를 바탕으로 내용을 채워넣어야 합니다.

```python
import os

def create_true_vector_slide():
    output_filename = "Vector_Slide_Output.html"
    
    # 캔버스 크기는 보통 1280x720 (16:9 비율)을 기준으로 합니다.
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Vector Slide</title>
        <style>
            /* 1. 기본 폰트 세팅 (필수) */
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; background-color: #333; 
            }
            
            /* 2. 슬라이드 본체 (여기에 배경색이나 그라데이션 적용) */
            .slide {
                width: 1280px; height: 720px;
                background: linear-gradient(135deg, #020012 0%, #060b26 40%, #0f103b 100%);
                position: relative; /* 자식 요소들의 절대 위치 기준점 */
                font-family: 'Pretendard', sans-serif;
                overflow: hidden;
            }
            
            /* 3. 요소 배치 (position: absolute를 사용하여 픽셀 단위로 정밀하게 배치) */
            .header-text {
                position: absolute; top: 50px; left: 100px;
                color: #ffffff; font-size: 40px; font-weight: bold;
                text-shadow: 0 2px 10px rgba(0,0,0,0.5); /* 가독성을 위한 그림자 */
            }

            /* 4. 네온 글로우 효과 예시 (버튼이나 강조 도형) */
            .neon-button {
                position: absolute; bottom: 50px; left: 500px;
                border: 2px solid #00ffff; border-radius: 30px;
                padding: 15px 40px; color: #00ffff;
                box-shadow: 0 0 15px rgba(0,255,255,0.4), inset 0 0 10px rgba(0,255,255,0.2);
            }

            /* 5. SVG 배경이나 선을 위한 컨테이너 */
            .svg-layer {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;
            }
        </style>
    </head>
    <body>
        <div class="slide">
            <!-- 배경 그래픽 라인 (SVG 활용) -->
            <svg class="svg-layer">
                <line x1="0" y1="0" x2="1280" y2="720" stroke="#9d4edd" stroke-width="2" opacity="0.3" />
            </svg>
            
            <!-- 텍스트 및 도형 요소 -->
            <div class="header-text">샘플 텍스트</div>
            <div class="neon-button">클릭하세요</div>
        </div>
    </body>
    </html>
    """

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"완료! '{output_filename}' 파일을 브라우저로 열고, PDF(배경 그래픽 포함)로 인쇄하세요.")

if __name__ == "__main__":
    create_true_vector_slide()
```