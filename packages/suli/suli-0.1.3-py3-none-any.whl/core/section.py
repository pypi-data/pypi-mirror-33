from reportlab.lib.colors import toColor
from reportlab.platypus import Frame

from suli.core import StyleSheet


class Section:
    def __init__(self, *, x, y, width, height, stylesheet=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.stylesheet = self._generate_default_stylesheet()
        if stylesheet is not None:
            self.stylesheet.override(stylesheet)

        self.story = []

    def add(self, flowable):
        self.story.append(flowable)

    def render(self, canvas):
        if self.stylesheet.background_color is not None:
            canvas.saveState()
            canvas.setFillColor(toColor(self.stylesheet.background_color))
            canvas.rect(self.x, self.y, self.width, self.height, stroke=0, fill=1)
            canvas.restoreState()

        frame = Frame(
            self.x, self.y, self.width, self.height,
            leftPadding=self.stylesheet.padding_left,
            rightPadding=self.stylesheet.padding_right,
            topPadding=self.stylesheet.padding_top,
            bottomPadding=self.stylesheet.padding_bottom
        )

        frame.addFromList(self.story, canvas)

    def _generate_default_stylesheet(self):
        stylesheet = StyleSheet()
        stylesheet(padding=0)
        return stylesheet
