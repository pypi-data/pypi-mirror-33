import os

from suli.components import Floating
from suli.components import Text
from suli.components import Heading
from suli.components import IconText
from suli.core import StyleSheet
from suli.core.utils import to_snake_case, to_rich_text


class Handlers:
    def __init__(self, classes, directory, master_stylesheet=StyleSheet()):
        self.classes = classes
        self.directory = directory
        self.master_stylesheet = master_stylesheet

    def make(self, node):
        tag = to_snake_case(node.tag)
        handler = getattr(self, f'create_{tag}')
        return handler(node)

    def create_text(self, node):
        return Text(to_rich_text(node.text.strip()), stylesheet=self._get_stylesheet(node))

    def create_heading(self, node):
        icon = self._get_asset(node.attrib.get('icon', None))
        return Heading(node.text.strip(), icon=icon, stylesheet=self._get_stylesheet(node))

    def create_icon_text(self, node):
        return IconText(
            node.text.strip(),
            self._get_asset(node.attrib['icon']),
            stylesheet=self._get_stylesheet(node)
        )

    def create_floating(self, node):
        attribs = node.attrib.copy()
        del attribs['type']
        del attribs['translateX']
        del attribs['translateY']

        return Floating(
            node.attrib['type'],
            translateX=int(node.attrib['translateX']),
            translateY=int(node.attrib['translateY']),
            **attribs,
        )

    def _get_asset(self, path):
        if path is None:
            return None
        return os.path.join(self.directory, path)

    def _get_stylesheet(self, node):
        stylesheet = self.master_stylesheet.copy()
        if 'class' in node.attrib:
            stylesheet.override(self.classes[node.attrib['class']])
        return stylesheet
