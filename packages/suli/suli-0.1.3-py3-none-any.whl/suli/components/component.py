from reportlab.platypus import Flowable


class Component(Flowable):
    def draw(self):
        self.on_draw()

    def on_draw(self):
        pass

    def override_style(self, style):
        return None
