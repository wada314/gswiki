

class _Table:
    def __init__(self):
        self.rows = []

    def format(self, formatter):
        self._remove_empty_columns()
        return (formatter.table(True)
                + u'\n'.join([row.format(formatter) for row in self.rows])
                + formatter.table(False))

    def _remove_empty_columns(self):
        col_num = min([len(row.cells) for row in self.rows])
        is_empty = [True] * col_num
        for row in self.rows:
            for i, cell in enumerate(row.cells):
                is_empty[i] = is_empty[i] and not (cell and cell.text)
        for row in self.rows:
            newcells = []
            for i, cell in enumerate(row.cells):
                if not is_empty[i]:
                    newcells.append(cell)
            row.cells = newcells
        

class _Row:
    def __init__(self, is_header=False):
        self.cells = []
        self.is_header = is_header

    def format(self, formatter):
        return (formatter.table_row(True, {u'class': u'header'} if self.is_header else {})
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
