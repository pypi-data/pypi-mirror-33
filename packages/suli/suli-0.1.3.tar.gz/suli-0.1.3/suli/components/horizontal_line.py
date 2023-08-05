from suli import StyleSheet


class HorizontalLine:
    def __init__(self, width, styles=None):
        self.width = width

        self.styles = StyleSheet()
        self.styles(margin=0)
        self.styles.override(styles)

    def draw(self, canv):
        canv.line(
            self.styles.margin_left,
            self.styles.margin_bottom,
            self.width + self.styles.margin_left,
            self.styles.margin_bottom
        )
