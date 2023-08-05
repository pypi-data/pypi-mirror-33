from reportlab.lib.colors import toColor

from suli.components import Component


class Floating(Component):
    def __init__(self, type, translateX=0, translateY=0, **kwargs):
        super().__init__()

        self.type = type
        self.translateX = translateX
        self.translateY = translateY
        self.kwargs = kwargs

    def wrap(self, availWidth, availHeight):
        self.avail_width = availWidth
        return 0, 0

    def draw(self):
        if self.type == 'line':
            self.draw_line()

    def draw_line(self):
        width = self.kwargs['width'] if 'width' in self.kwargs else self.avail_width - self.translateX

        self.canv.translate(self.translateX, self.translateY)
        self.canv.setStrokeColor(toColor(self.kwargs['color']))
        self.canv.line(0, 0, width, 0)
