# make_test_pdf.py
from reportlab.pdfgen import canvas

p = "sample_test_doc.pdf"
c = canvas.Canvas(p)
c.setFont("Helvetica", 12)
c.drawString(72, 720, "This is a test document for the QA chatbot.")
c.drawString(72, 700, "It should be indexed and later retrieved.")
c.save()
print("Wrote", p)
