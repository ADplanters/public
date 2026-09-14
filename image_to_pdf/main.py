from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import HexColor

# 1. 페이지 크기를 엄청나게 크게 설정 (가로 1000mm, 세로 300mm)
pdf_filename = "kims_entertainment_banner_HighRes.pdf"
page_width = 1000 * mm
page_height = 300 * mm

c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))

# 2. 둥근 배경 그리기 (여백 10mm)
c.setFillColor(HexColor("#111111"))
c.roundRect(10 * mm, 10 * mm, 980 * mm, 280 * mm, 50, stroke=0, fill=1)

# 3. 서브타이틀
c.setFillColor(HexColor("#b3b3b3"))
c.setFont("Helvetica", 50) # 폰트 크기 대폭 확대 (12 -> 50)
c.drawString(70 * mm, 200 * mm, "R E P R E S E N T A T I V E   D I R E C T O R")

# 4. 메인타이틀
c.setFillColor(HexColor("#d4af37"))
c.setFont("Helvetica-Bold", 160) # 폰트 크기 대폭 확대 (38 -> 160)
c.drawString(70 * mm, 100 * mm, "KIMS ENTERTAINMENT")

# 5. PDF 완성 및 저장
c.save()
print("성공! 훨씬 거대하고 선명하게 보이는 고해상도 PDF가 생성되었습니다.")