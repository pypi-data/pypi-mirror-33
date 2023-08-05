from reportlab.platypus import Image

from suli.components import Text
from suli.components import Component
from suli.core import StyleSheet


class IconText(Component):
    def __init__(self, text, icon, stylesheet=None):
        super().__init__()

        self.stylesheet = StyleSheet()(
            padding=0,
        ).override(stylesheet)

        self.text = Text(text, stylesheet=StyleSheet()(
            font_family=self.stylesheet.font_family,
            font_size=self.stylesheet.get_or('font_size', 10),
        ))

        self.size = self.text.stylesheet.font_size * 1.6

        self.image = Image(
            icon,
            width=self.size,
            height=self.size,
        )

    def wrap(self, availWidth, availHeight):
        width, height = self.text.wrap(availWidth, availHeight)
        return width, height + self.stylesheet.padding_top + self.stylesheet.padding_bottom

    def draw(self):
        self.image.canv = self.canv
        self.text.canv = self.canv

        self.canv.translate(self.stylesheet.padding_left, self.stylesheet.padding_bottom)

        self.image.draw()

        self.canv.translate(self.size + 8, self.size - self.text.stylesheet.font_size)
        self.text.draw()
