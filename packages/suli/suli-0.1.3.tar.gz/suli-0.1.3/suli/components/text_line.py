from reportlab.lib.colors import toColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from suli.stylesheet import StyleSheet


class TextLine:
    def __init__(self, text, stylesheet=None):
        super().__init__()

        self.text = text

        self.stylesheet = StyleSheet()(
            font_family='Helvetica',
            padding=0,
            color='#000000',
            font_size=16,
            font_weight='normal',
        ).override(stylesheet)

    def draw(self, canv):
        font_name = self.stylesheet.font_family

        if self.stylesheet.font_weight == 'bold':
            font_name += '-Bold'

        text_obj = canv.beginText()
        text_obj.setFont(font_name, self.stylesheet.font_size)
        text_obj.setFillColor(toColor(self.stylesheet.color))
        text_obj.setTextOrigin(self.stylesheet.padding_left, 0)
        text_obj.textLine(self.text)
        canv.drawText(text_obj)

    def as_flowable(self):
        return Paragraph(self.text, style=ParagraphStyle(
            name=None,
            fontFamily=self.stylesheet.font_family,
            fontSize=self.stylesheet.font_size,
            leading=self.stylesheet.font_size,
            spaceAfter=self.stylesheet.padding_bottom,
            spaceBefore=self.stylesheet.padding_top,
        ))
