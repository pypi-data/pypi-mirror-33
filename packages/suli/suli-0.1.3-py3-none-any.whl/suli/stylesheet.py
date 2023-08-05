from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY


class StyleSheet(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            self.set(k, v)
        return self

    def set(self, k, v):
        self[k] = v

        if k == 'padding':
            self._spread_padding(v)

    def override(self, other):
        if other is not None:
            self(**other)
        return self

    def __getattr__(self, item):
        if item not in self:
            return None
        return self[item]

    def get_or(self, item, default):
        if item not in self:
            return default
        return self[item]

    def reportlab_text_align(self):
        if 'text_align' not in self:
            return TA_LEFT
        if self.text_align == 'left':
            return TA_LEFT
        if self.text_align == 'right':
            return TA_RIGHT
        if self.text_align == 'center':
            return TA_CENTER
        if self.text_align == 'justify':
            return TA_JUSTIFY
        return TA_LEFT

    def _spread_padding(self, value):
        self['padding_bottom'] = value
        self['padding_top'] = value
        self['padding_left'] = value
        self['padding_right'] = value

    def copy(self):
        return StyleSheet().override(self)
