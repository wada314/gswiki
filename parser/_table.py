# -*- encoding: utf-8 -*-

_JSON_NAME_ORDER = [
    u'名称', u'弾種', u'レベル',
    u'格闘', u'N格', u'上格', u'左格', u'右格', u'下格', u'威力', u'解説',
    u'キャラクターデータ', u'よろけにくさ', u'ジャンプ上昇力', u'空中ダッシュ初速度',
    u'空中ダッシュ最終速度', u'腕力', u'格闘距離',
    u'コスチューム', u'シンボルチャット',
    u'ウェポンパック', u'コスト', u'耐久力', u'格闘補正', u'入手条件',
    u'右手武器', u'左手武器', u'サイド武器', u'タンデム武器',
    u'チューン', u'メリット', u'デメリット',
    u'攻撃力', u'攻撃力(爆風)', u'散弾攻撃力', u'吸引力', u'回復力', 
    u'連射間隔', u'装填数', u'リロード分子', u'リロード分母', 
    u'射程距離', u'散弾射程', u'攻撃範囲', u'_分裂数', u'_三点バースト', u'_状態異常',
    u'ロックオン時間', u'防御力', u'最低持続時間',
    u'シールド範囲', u'シールド展開時間',
    u'反動ダメージ割合', u'反動ダメージ量',
    u'弾薬補給割合', u'回復範囲', u'弾薬回復範囲', u'移動時間', u'効果時間', u'_チャージ',
    u'_備考', u'_サブトリガー', u'_サブウェポン',
]

def _json_name_priority(name):
    if isinstance(name, unicode):
        name = name.lstrip(u'_')
    try:
        return _JSON_NAME_ORDER.index(name)
    except ValueError:
        return len(_JSON_NAME_ORDER)

class _Table:
    def __init__(self):
        self.rows = []

    def toHtmlTable(self):
        rows = [_Row(r.cells) for r in self.rows]
        self._remove_empty_columns(rows)
        title_row = self._extract_title_row(rows)
        html_rows = []
        html_rows.append(title_row.toHtmlRow())
        for row in rows:
            html_rows.extend(row.toHtmlRows())
        return _HtmlTable(html_rows)

    @staticmethod
    def _remove_empty_columns(rows):
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
        title_row = _TitleRow()
        col_num = min([len(row.cells) for row in rows])
        column_title_lists = [[] for _ in range(col_num)]
        for row in rows:
            for i, cell in enumerate(row.cells):
                if cell and cell.title:
                    column_title_lists[i].append(cell.title)
        column_titles = [min(titles, key=_json_name_priority) for titles in column_title_lists]
        for row in rows:
            for column_title, cell in zip(column_titles, row.cells):
                if not cell:
                    continue
                if cell.title == column_title:
                    cell.title = None
        title_row.cells = [_TitleCell(text=title) for title in column_titles]
        return title_row

class _HtmlTable:
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

class _Row:
    def __init__(self, cells=[]):
        self.cells = [cell or _Cell() for cell in cells]

    def toHtmlRows(self):
        cell_pairs = [cell.toHtmlCells() for cell in self.cells]
        titles, texts = zip(*cell_pairs)
        texts = filter(None, texts)
        return [_HtmlRow(titles), _HtmlRow(texts)]

class _TitleRow:
    def __init__(self, cells=[]):
        self.cells = list(cells)

    def toHtmlRow(self):
        cells = [cell.toHtmlCell() for cell in self.cells]
        return _HtmlRow(cells)

class _HtmlRow:
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
        
class _Cell:
    def __init__(self, title=None, text=None, cls=[], attrs={}, formatted=False):
        self.title = title
        self.text = text
        self.cls = list(cls)
        self.attrs = dict(attrs)
        self.formatted = formatted

    def toHtmlCells(self):
        """
        returns (_HtmlCell, _HtmlCell).
        """
        if self.title:
            title_cell = _HtmlCell(self.title, self.cls + [u'subheader'],
                                   self.attrs, False)
            text_cell = _HtmlCell(self.text, self.cls, self.attrs, self.formatted)
            return (title_cell, text_cell)
        else:
            attrs = dict(self.attrs)
            attrs[u'rowspan'] = u'2'
            cell= _HtmlCell(self.text, self.cls, attrs, self.formatted)
            return (cell, None)

class _TitleCell:
    def __init__(self, text=None, cls=[], attrs={}, formatted=False):
        self.text = text
        self.cls = list(cls)
        self.attrs = dict(attrs)
        self.formatted = formatted

    def toHtmlCell(self):
        return _HtmlCell(self.text, self.cls + [u'header'],
                         self.attrs, self.formatted)

class _HtmlCell:
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
