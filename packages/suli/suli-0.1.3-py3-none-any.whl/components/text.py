from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from suli.core import StyleSheet


class Text(Paragraph):
    def __init__(self, text, stylesheet=None):
        self.stylesheet = self._get_style(stylesheet)
        super().__init__(text, style=self._get_paragraph_style(self.stylesheet))
        self.text = text

    def _get_style(self, stylesheet):
        if stylesheet and 'font_family' in stylesheet:
            font_family = stylesheet.font_family
            if stylesheet.font_weight == 'bold':
                font_family += '-Bold'
        else:
            font_family = 'Helvetica'

        return StyleSheet()(
            font_size=10,
            padding=0,
            padding_bottom=16,
        ).override(stylesheet)(
            font_family=font_family,
        )

    def _get_paragraph_style(self, stylesheet):
        return ParagraphStyle(
            name=None,
            alignment=stylesheet.reportlab_text_align(),
            fontName=stylesheet.font_family,
            fontSize=stylesheet.font_size,
            leading=stylesheet.font_size,
            spaceAfter=stylesheet.padding_bottom,
            spaceBefore=stylesheet.padding_top,
        )
