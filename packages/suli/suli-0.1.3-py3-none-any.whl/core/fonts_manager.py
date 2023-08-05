from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def load_fonts():
    pdfmetrics.registerFont(TTFont('OpenSans', 'OpenSans-Light.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans-Italic', 'OpenSans-LightItalic.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans-Bold', 'OpenSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans-BoldItalic', 'OpenSans-BoldItalic.ttf'))

    addMapping('OpenSans', 0, 0, 'OpenSans')
    addMapping('OpenSans', 0, 1, 'OpenSans-Italic')
    addMapping('OpenSans', 1, 0, 'OpenSans-Bold')
    addMapping('OpenSans', 1, 1, 'OpenSans-BoldItalic')
