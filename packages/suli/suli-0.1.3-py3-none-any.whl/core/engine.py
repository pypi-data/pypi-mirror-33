import os
import xml.etree.ElementTree as ET

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from wand.color import Color
from wand.image import Image

from suli import handlers
from suli.layout import Layout
from suli.core import Section
from suli.core import StyleSheet

RESERVED_STYLESHEET_WORDS = ['name']


class SuliEngine:
    def __init__(self, pdf_file, png_file, directory):
        self.directory = directory

        self.classes = {}

        self.pdf_file = pdf_file
        self.png_file = png_file

        self.canvas = Canvas(self.pdf_file, pagesize=letter)
        self.canvas.setCreator('curriculumpro.io')
        self.canvas.setTitle('Curriculum Vitae')
        self.canvas.setAuthor('curriculumpro.io')
        self.canvas.setSubject('Curriculum Vitae')
        self.canvas.setKeywords('cv, resume, curriculum vitae, curriculumpro.io')
        self.canvas._doc.info.producer = 'curriculumpro.io'

        self.page_width, self.page_height = self.canvas._pagesize

        self.layout = None
        self.handlers = None

        self.master_stylesheet = StyleSheet()

    def process_and_save(self):
        self.read_layout()
        self.read_classes()
        self.read_document()
        self.save()

    def read_layout(self):
        layout_path = os.path.join(self.directory, 'layout.xml')
        self.layout = Layout(layout_path)
        self.layout.process()
        self.layout.to_positions(self.page_width, self.page_height)
        self.layout.invert(self.page_height)

    def read_classes(self):
        stylesheet_path = os.path.join(self.directory, 'stylesheet.xml')
        tree = ET.parse(stylesheet_path)
        root = tree.getroot()

        for child in root:
            self._read_class(child)

        self.handlers = handlers.Handlers(self.classes, self.directory)

    def read_document(self):
        document_path = os.path.join(self.directory, 'document.xml')

        tree = ET.parse(document_path)
        root = tree.getroot()

        if 'class' in root.attrib:
            self.master_stylesheet = self.classes[root.attrib['class']]
            self.handlers.master_stylesheet = self.master_stylesheet

        for child in root:
            self._handle_section(child)

    def save(self):
        self.canvas.save()

        with Image(filename=self.pdf_file, resolution=100) as img:
            with Image(width=img.width, height=img.height, background=Color("white")) as bg:
                bg.composite(img, 0, 0)
                bg.save(filename=self.png_file)

    def _handle_section(self, section_node):
        """
        Reads a section and every component inside.

        :param section_node:
        :return:
        """
        section_layout = self.layout.sections[section_node.attrib['name']]

        x = section_layout.x
        y = section_layout.y
        width = section_layout.width
        height = section_layout.height

        stylesheet = None
        if 'class' in section_node.attrib:
            stylesheet = self.master_stylesheet.copy().override(self.classes[section_node.attrib['class']])

        section = Section(x=x, y=y, width=width, height=height, stylesheet=stylesheet)

        for component_node in section_node:
            component = self.handlers.make(component_node)
            section.add(component)

        section.render(self.canvas)

    def _read_class(self, node, parent_name=''):
        """
        Reads a stylesheet class from the XML node.

        :param node: the XML node to inspect.
        :param parent_name: prefix for the class name: Sample.Subsample
        """
        if parent_name != '':
            name = f"{parent_name}.{node.get('name')}"
        else:
            name = node.get('name')

        #  create stylesheet.
        stylesheet = self._make_stylesheet(node)

        # register stylesheet class.
        self.classes[name] = stylesheet

        # read inner classes.
        for child in node:
            self._read_class(child, name)

    def _make_stylesheet(self, node):
        stylesheet = StyleSheet()
        for attrib in node.attrib:
            # ignore reserved words.
            if attrib in RESERVED_STYLESHEET_WORDS:
                continue

            # store the value.
            stylesheet.set(attrib, self._handle_attr(node.attrib[attrib]))
        return stylesheet

    def _handle_attr(self, val):
        """
        Inspects a value and parses to respective type if needed.

        :param val: string representing the value.
        :return: the converted value.
        """
        # parse if the value is an integer.
        if val.isdigit():
            val = int(val)

        try:
            # parse if the value is a float.
            val = float(val)
        except ValueError:
            pass

        return val
