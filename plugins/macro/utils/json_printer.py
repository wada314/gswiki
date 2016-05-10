# -*- encoding: utf-8 -*-

import collections
import json

_JSON_NAME_ORDER_LIST = [
    u'名称', u'携帯サイトID', u'弾種', u'レベル',
    u'格闘', u'N格', u'上格', u'左格', u'右格', u'下格', u'威力', u'解説',
    u'キャラクターデータ', u'よろけにくさ', u'ジャンプ上昇力', u'空中ダッシュ初速度',
    u'空中ダッシュ最終速度', u'腕力', u'格闘距離',
    u'コスチューム', u'シンボルチャット',
    u'ウェポンパック', u'コスト', u'耐久力', u'格闘補正', u'入手条件',
    u'右手武器', u'左手武器', u'サイド武器', u'タンデム武器',
    u'チューン', u'メリット', u'デメリット',
    u'攻撃力', u'攻撃力(爆風)', u'散弾攻撃力', u'吸引力', u'回復力', 
    u'連射間隔', u'装填数', u'リロード分子', u'リロード分母', 
    u'射程距離', u'散弾射程', u'攻撃範囲', u'分裂数', u'三点バースト', u'状態異常',
    u'ロックオン時間', u'防御力', u'最低持続時間',
    u'シールド範囲', u'シールド展開時間',
    u'反動ダメージ割合', u'反動ダメージ量',
    u'弾薬補給割合', u'回復範囲', u'弾薬回復範囲', u'移動時間', u'効果時間', u'チャージ',
    u'備考', u'サブトリガー', u'サブウェポン',
]
_JSON_NAME_ORDER_DICT = dict(map(
    lambda (i, name): (name, i),
    enumerate(_JSON_NAME_ORDER_LIST)))
_JSON_NAME_ORDER_TOTAL = len(_JSON_NAME_ORDER_LIST)

def json_name_priority(name):
    if isinstance(name, unicode):
        name = name.lstrip(u'_')
    return _JSON_NAME_ORDER_DICT.get(name, _JSON_NAME_ORDER_TOTAL)

# ensure_ascii is False by default.
def print_json(j, **kw):
    def sort_dict(d):
        l = d.items()
        l.sort(cmp=lambda x, y: cmp(json_name_priority(x[0]), json_name_priority(y[0])))
        return collections.OrderedDict(l)

    if kw.get('sort_keys', True):
        text = json.dumps(j, ensure_ascii=False)
        j = json.loads(text, object_hook=sort_dict)

    return json.dumps(j, ensure_ascii=kw.get('ensure_ascii', False), **kw)
