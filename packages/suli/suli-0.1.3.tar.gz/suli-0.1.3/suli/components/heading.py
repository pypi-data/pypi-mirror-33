from reportlab.platypus import Image

from .component import Component
from .text_line import TextLine
from suli.stylesheet import StyleSheet


class Heading(Component):
    def __init__(self, title, icon=None, stylesheet=None):
        super().__init__()

        self.title = title
        self.icon = icon

        self.stylesheet = self._generate_default_stylesheet()
        self.stylesheet.override(stylesheet)
        self.override_style(self.stylesheet)

        self.size = self.stylesheet.font_size * 1.4

    def wrap(self, avail_width, avail_height):
        self.width = avail_width
        self.height = self.stylesheet.font_size + self.stylesheet.padding_top + self.stylesheet.padding_bottom
        return self.width, self.height

    def draw(self):
        super().draw()

        self.canv.translate(self.stylesheet.padding_left, self.stylesheet.padding_bottom)

        if self.icon:
            top_offset = self.size - self.stylesheet.font_size * 1.1

            image = Image(
                self.icon,
                width=self.size,
                height=self.size,
            )

            image.canv = self.canv

            self.canv.translate(0, -top_offset)
            image.draw()
            self.canv.translate(self.size + 8, top_offset)

        tl = TextLine(self.title, stylesheet=StyleSheet()(
            font_family=self.stylesheet.font_family,
            font_weight=self.stylesheet.font_weight,
            font_size=self.stylesheet.font_size,
            color=self.stylesheet.color,
        ))
        tl.draw(self.canv)

    def on_draw(self):
        pass

    def override_style(self, style):
        return None

    def _generate_default_stylesheet(self):
        stylesheet = StyleSheet()

        stylesheet(
            font_family='OpenSans',
            font_size=16,
            padding=0,
            color='#000000'
        )

        return stylesheet
