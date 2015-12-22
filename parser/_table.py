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

    def format(self, formatter):
        self._remove_empty_columns()
        self.rows = [self._extract_title_row()] + self.rows
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

    def _extract_title_row(self):
        title_row = _Row(is_header=True)
        col_num = min([len(row.cells) for row in self.rows])
        column_title_lists = [[] for _ in range(col_num)]
        for row in self.rows:
            for i, cell in enumerate(row.cells):
                if cell and cell.title:
                    column_title_lists[i].append(cell.title)
        column_titles = [min(titles, key=_json_name_priority) for titles in column_title_lists]
        for row in self.rows:
            for column_title, cell in zip(column_titles, row.cells):
                if not cell:
                    continue
                if cell.title == column_title:
                    cell.title = None
        title_row.cells = [_Cell(title=None, text=title) for title in column_titles]
        return title_row

class _Row:
    def __init__(self, is_header=False):
        self.cells = []
        self.is_header = is_header

    def format(self, formatter):
        body_cells = []
        text = u''
        if (not self.is_header) and any(map(lambda c: c and c.title, self.cells)):
            # create subheader row
            sh_cells = []
            for cell in self.cells:
                if not cell:
                    cell = _Cell()
                if cell.title:
                    sh_cells.append(_Cell(text=cell.title, attrs={u'class': u'subheader'}))
                    cell.title = None
                    body_cells.append(cell)
                else:
                    cell.attrs[u'rowspan'] = u'2'
                    sh_cells.append(cell)
                    body_cells.append(None)
            
            text += formatter.table_row(True)
            for cell in sh_cells:
                text += u'\n' + cell.format(formatter)
            text += formatter.table_row(False)

        else:
            body_cells = [(c or _Cell()) for c in self.cells]

        text += formatter.table_row(True, {u'rowclass': u'header'} if self.is_header else {})
        for cell in body_cells:
            if cell:
                text += u'\n' + cell.format(formatter)
        text += formatter.table_row(False)
        return text
        
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
