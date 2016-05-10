# -*- encoding: utf-8 -*-

import copy
from json_printer import json_name_priority

class Table:
    def __init__(self):
        self.rows = []

    def __unicode__(self):
        return '\n'.join([unicode(r) for r in self.rows])

    def toHtmlTable(self, **kw):
        rows = copy.deepcopy(self.rows)
        if kw.get('remove_empty_columns', True):
            self.remove_empty_columns(rows)
        html_rows = []
        if kw.get('generate_header', True):
            title_row = self._extract_title_row(rows)
            html_rows.append(title_row.toHtmlRow())
        else:
            for row in rows:
                for cell in row.cells:
                    cell.title = None
        for row in rows:
            html_rows.extend(row.toHtmlRows())
        return HtmlTable(html_rows)

    @staticmethod
    def remove_empty_columns(rows):
        """
        param rows might be modified to remove the empty columns.
        """
        col_num = min([len(row.cells) for row in rows])
        is_empty = [True] * col_num
        for row in rows:
            for i, cell in enumerate(row.cells):
                is_empty[i] = is_empty[i] and not (cell and cell.text)
        for row in rows:
            newcells = []
            for i, cell in enumerate(row.cells):
                if not is_empty[i]:
                    newcells.append(cell)
            row.cells = newcells

    @staticmethod
    def _extract_title_row(rows):
        """
        returns a newly generated title row of the table.
        param rows might be modified to remove the title of each cells.
        """
        title_row = TitleRow()
        if not rows:
            return title_row
        col_num = min([len(row.cells) for row in rows])
        column_title_lists = [[] for _ in range(col_num)]
        for row in rows:
            for i, cell in enumerate(row.cells):
                if cell and cell.title:
                    column_title_lists[i].append(cell.title)
        column_titles = [min(titles + [u''], key=json_name_priority) for titles in column_title_lists]
        for row in rows:
            for column_title, cell in zip(column_titles, row.cells):
                if not cell:
                    continue
                if cell.title == column_title:
                    cell.title = None
        title_row.cells = [TitleCell(text=title) for title in column_titles]
        return title_row

class HtmlTable:
    def __init__(self, rows, cls=[], attrs={}):
        self.rows = list(rows)
        self.cls = cls or []
        self.attrs = attrs or {}

    def format(self, formatter):
        attrs = dict(self.attrs)
        attrs[u'tableclass'] = u' '.join(self.cls)
        return (formatter.table(True, attrs)
                + u'\n'.join([row.format(formatter) for row in self.rows])
                + formatter.table(False))

class Row:
    def __init__(self, cells=[], cls=[]):
        self.cells = [cell or Cell() for cell in cells]
        self.cls = list(cls)

    def __unicode__(self):
        return ('%d:[' % len(self.cells)) + ', '.join([unicode(c) for c in self.cells]) + ']'

    def toHtmlRows(self):
        cell_pairs = [cell.toHtmlCells() if cell else Cell.getEmptyHtmlCells()
                      for cell in self.cells]
        titles, texts = zip(*cell_pairs)
        texts = filter(None, texts)
        return [HtmlRow(titles, cls=self.cls), HtmlRow(texts, cls=self.cls)]

class TitleRow:
    def __init__(self, cells=[], cls=[]):
        self.cells = list(cells)
        self.cls = list(cls)

    def toHtmlRow(self):
        cells = [cell.toHtmlCell() for cell in self.cells]
        return HtmlRow(cells)

    def toHtmlRows(self):
        return [self.toHtmlRow()]

class HtmlRow:
    def __init__(self, cells, cls=[], attrs={}):
        self.cells = list(cells)
        self.cls = list(cls)
        self.attrs = dict(attrs)

    def format(self, formatter):
        text = u''
        attrs = dict(self.attrs)
        attrs[u'rowclass'] = u' '.join(self.cls)
        text += formatter.table_row(True, attrs)
        for cell in self.cells:
            if cell:
                text += u'\n' + cell.format(formatter)
        text += formatter.table_row(False)
        return text
        
class Cell:
    def __init__(self, title=None, text=None, cls=[], attrs={}, formatted=False):
        self.title = title
        self.text = text
        self.cls = list(cls)
        self.attrs = dict(attrs)
        self.formatted = formatted

    def __unicode__(self):
        return '(%s/%s)' % (self.title or self.title, self.text or self.text)

    def toHtmlCells(self):
        """
        returns (HtmlCell, HtmlCell).
        """
        if self.title:
            title_cell = HtmlCell(self.title, self.cls + [u'sheader'],
                                   self.attrs, False)
            text_cell = HtmlCell(self.text, self.cls, self.attrs, self.formatted)
            return (title_cell, text_cell)
        else:
            attrs = dict(self.attrs)
            attrs[u'rowspan'] = u'2'
            cell= HtmlCell(self.text, self.cls, attrs, self.formatted)
            return (cell, None)

    @staticmethod
    def getEmptyHtmlCells():
        attrs = { u'rowspan': u'2' }
        cell= HtmlCell(attrs=attrs)
        return (cell, None)

class TitleCell:
    def __init__(self, text=None, cls=[], attrs={}, formatted=False):
        self.text = text
        self.title = None  # dummy
        self.cls = list(cls)
        self.attrs = dict(attrs)
        self.formatted = formatted

    def toHtmlCell(self):
        return HtmlCell(self.text, self.cls + [u'header'],
                         self.attrs, self.formatted)

class HtmlCell:
    def __init__(self, text=None, cls=[], attrs={}, formatted=False):
        self.text = text
        self.cls = list(cls)
        self.attrs = dict(attrs)
        self.formatted = formatted

    def format(self, formatter):
        attrs = dict(self.attrs)
        attrs['class'] = u' '.join(self.cls)
        return (formatter.table_cell(True, attrs)
                + (self.text if self.formatted else formatter.text(self.text))
                + formatter.table_cell(False))
