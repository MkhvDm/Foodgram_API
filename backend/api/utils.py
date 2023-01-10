import io
from reportlab.lib.pagesizes import A4, letter

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from datetime import date


def gen_pdf(list_of_strings) -> io.BytesIO:
    buffer = io.BytesIO()
    p = Canvas(buffer, pagesize=letter)
    font = 'Bonche-Light'
    pdfmetrics.registerFont(TTFont(font, f'{font}.ttf', 'UTF-8'))
    width, height = letter
    x, y = 250, height - 75  # start point

    # header:
    p.setFont(font, 20)
    p.drawString(x, y, 'SHOP LIST')
    x = 75
    y -= 40

    # body
    p.setFont(font, 14)
    for elem in list_of_strings:
        p.drawString(x, y, elem)
        y -= 20

    # bottom
    x = 255
    y -= 50
    p.setFont(font, 10)
    p.drawString(x, y, f'© FoodGram {date.today().year}')

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
