

class _Table:
    def __init__(self):
        self.rows = []

    def format(self, formatter):
        return (formatter.table(True)
                + u'\n'.join([row.format(formatter) for row in self.rows])
                + formatter.table(False))

class _Row:
    def __init__(self):
        self.cells = []

    def format(self, formatter):
        return (formatter.table_row(True)
                + u'\n'.join([(cell or _Cell()).format(formatter) for cell in self.cells])
                + formatter.table_row(False))
        
class _Cell:
    def __init__(self, title=None, text=None, attrs={}, formatted=False):
        self.title = title
        self.text = text
        self.attrs = attrs
        self.formatted = formatted

    def format(self, formatter):
        return (formatter.table_cell(True, self.attrs)
                + (self.text if self.formatted else formatter.text(self.text))
                + formatter.table_cell(False))
