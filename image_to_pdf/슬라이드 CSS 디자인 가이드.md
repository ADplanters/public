# [GEM 참조용] 디자인 요소별 CSS/SVG 스타일링 가이드

슬라이드 이미지에 포함된 특수 효과들을 HTML/CSS로 똑같이 구현하기 위한 치트시트(Cheat Sheet)입니다.

## 1. 네온 빛 번짐 (Neon Glow) 효과
텍스트나 도형에서 빛이 뿜어져 나오는 효과는 `text-shadow`와 `box-shadow`를 겹쳐서 표현합니다.
*   **텍스트 네온:** `text-shadow: 0 0 10px rgba(0,255,255,0.8), 0 0 20px rgba(0,255,255,0.5);`
*   **도형/버튼 네온:** `box-shadow: 0 0 15px rgba(255,0,255,0.6), inset 0 0 10px rgba(255,0,255,0.3);` (inset을 넣으면 안쪽으로도 빛이 번짐)

## 2. 복잡한 다이어그램 연결선 (SVG Line)
div로 선을 그리기 어려울 때는 HTML `<svg>` 태그를 슬라이드 전체 크기로 덮은 뒤 좌표로 선을 긋습니다.
```html
<svg style="position: absolute; top:0; left:0; width: 100%; height: 100%;">
    <!-- x1, y1에서 시작해 x2, y2로 끝나는 두께 2px짜리 선 -->
    <line x1="200" y1="200" x2="400" y2="500" stroke="#00ffff" stroke-width="2" />
</svg>
```

## 3. 그라데이션 (Gradients)
*   **선형 그라데이션 (배경):** `background: linear-gradient(135deg, #111 0%, #333 100%);`
*   **원형 그라데이션 (빛 반사):** `background: radial-gradient(circle at center, #555 0%, #111 70%);`
*   **텍스트 그라데이션 (글씨에 색상 입히기):**
    ```css
    background: linear-gradient(to right, #ff8c00, #ff0080);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    ```

## 4. 아이콘 처리
비트맵 아이콘을 살리기 어려울 때는 고화질 이모지(Emoji)를 활용하거나, FontAwesome 같은 웹 아이콘 코드를 대체하여 삽입하면 벡터 특성을 유지할 수 있습니다.