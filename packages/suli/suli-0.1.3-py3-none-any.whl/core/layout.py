import xml.etree.ElementTree as ET


class Row:
    x = 0
    y = 0
    width = 0
    height = 0

    def __init__(self, height):
        self.height = height
        self.columns = []

    def __str__(self):
        return f"row(x={self.x} y={self.y} width={self.width} height={self.height})"

    def debug(self):
        print(self)
        for col in self.columns:
            col.debug()


class Column:
    x = 0
    y = 0
    width = 0
    height = 0

    def __init__(self, width, section=None):
        self.width = width
        self.rows = []
        self.section = section

    def __str__(self):
        return f"column(x={self.x} y={self.y} width={self.width} height={self.height} section={self.section})"

    def debug(self):
        print(self)
        for row in self.rows:
            row.debug()


class Layout:
    def __init__(self, xml):
        self.xml = xml

        self.tree = []
        self.main_rows = []
        self.sections = {}

    def process(self):
        tree = ET.parse(self.xml)
        self.process_node(tree.getroot())

    def process_node(self, node):
        for child in node:
            if child.tag == 'Row':
                self.row(int(child.attrib.get('height', 0)))
                self.process_node(child)
                self.pop()

            elif child.tag == 'Column':
                self.column(int(child.attrib.get('width', 0)), section=child.attrib.get('section', None))
                self.process_node(child)
                self.pop()

    def row(self, height=0):
        if len(self.tree) != 0:
            assert self.tree[-1].__class__.__name__ == 'Column'

        r = Row(height)
        if len(self.tree) == 0:
            self.main_rows.append(r)
        else:
            self.tree[-1].rows.append(r)
        self.tree.append(r)
        return self

    def column(self, width=0, section=None):
        assert self.tree[-1].__class__.__name__ == 'Row'

        c = Column(width, section=section)
        self.tree[-1].columns.append(c)
        self.tree.append(c)
        return self

    def pop(self):
        del self.tree[-1]
        return self

    def to_positions(self, page_width, page_height):
        self.order_rows(self.main_rows, 0, 0, page_width, page_height)

    def order_rows(self, rows, x, y, width, height):
        # obtain pending row and remaining height.
        pending = []
        remaining_height = height
        for row in rows:
            if row.height == 0:
                pending.append(row)
            else:
                remaining_height -= row.height

        for o in pending:
            o.height = remaining_height / len(pending)

        # transform to positions.
        for row in rows:
            row.width = width
            row.x = x
            row.y = y

            y += row.height

        for row in rows:
            self.order_columns(row.columns, row.x, row.y, row.width, row.height)

    def order_columns(self, columns, x, y, width, height):
        # obtain pending column and remaining height.
        pending = []
        remaining_width = width
        for column in columns:
            if column.width == 0:
                pending.append(column)
            else:
                remaining_width -= column.width

        for o in pending:
            o.width = remaining_width / len(pending)

        # transform to positions.
        for column in columns:
            column.height = height
            column.x = x
            column.y = y

            x += column.width

        for column in columns:
            if len(column.rows) != 0:
                self.order_rows(column.rows, column.x, column.y, column.width, column.height)
            else:
                self.sections[column.section] = column

    def invert(self, height):
        for section in self.sections.values():
            section.y = height - section.y - section.height


if __name__ == '__main__':
    l = Layout('example-xml/layout.xml')
    l.process()
    # l.row().column().row(100).column().pop().pop().row().column().pop().pop().pop().column(200).pop().pop()
    l.to_positions(500, 500)
    l.invert(500)

    for section in l.sections:
        print(section)
