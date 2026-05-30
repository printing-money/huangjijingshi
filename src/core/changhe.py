"""
声音唱和系统

实现邵雍《皇极经世书》卷七至卷十的声音唱和图：
- 十二律吕（音高系统）
- 天声（韵母部类，10组）
- 地音（声母部类，12组）
- 10×12 唱和千字发音矩阵
- 干支与声音的对应关系
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# === 十二律吕 ===

@dataclass(frozen=True)
class LvLv:
    """律吕"""
    name: str
    type: str        # '律'(阳) 或 '吕'(阴)
    index: int       # 序号 0-11
    frequency_ratio: float  # 相对黄钟的频率比

    @property
    def is_yang(self) -> bool:
        return self.type == '律'


TWELVE_LVLV = [
    LvLv('黄钟', '律', 0, 1.000),
    LvLv('大吕', '吕', 1, 1.053),
    LvLv('太簇', '律', 2, 1.125),
    LvLv('夹钟', '吕', 3, 1.185),
    LvLv('姑洗', '律', 4, 1.266),
    LvLv('仲吕', '吕', 5, 1.333),
    LvLv('蕤宾', '律', 6, 1.405),
    LvLv('林钟', '吕', 7, 1.500),
    LvLv('夷则', '律', 8, 1.580),
    LvLv('南吕', '吕', 9, 1.688),
    LvLv('无射', '律', 10, 1.778),
    LvLv('应钟', '吕', 11, 1.872),
]

# 天干对应律吕（五正律）
# 甲己=黄钟, 乙庚=太簇, 丙辛=姑洗, 丁壬=蕤宾, 戊癸=夷则
TIANGAN_LV_MAP = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]

# 地支对应律吕（十二律吕完整对应）
DIZHI_LV_MAP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def get_year_lv(gan_index: int) -> LvLv:
    """获取年律（按天干）"""
    return TWELVE_LVLV[TIANGAN_LV_MAP[gan_index % 10]]


def get_month_lv(zhi_index: int) -> LvLv:
    """获取月律（按地支）"""
    return TWELVE_LVLV[DIZHI_LV_MAP[zhi_index % 12]]


def get_day_lv(gan_index: int) -> LvLv:
    """获取日律（按天干）"""
    return TWELVE_LVLV[TIANGAN_LV_MAP[gan_index % 10]]


def get_hour_lv(zhi_index: int) -> LvLv:
    """获取时律（按地支）"""
    return TWELVE_LVLV[DIZHI_LV_MAP[zhi_index % 12]]


# === 天声（韵母部类）===

@dataclass
class TianShengGroup:
    """天声组"""
    index: int           # 组序号 0-9（对应天干）
    name: str            # 组名
    four_tones: list = field(default_factory=list)  # 四声（平上去入）
    attribute: str = ''  # 属性描述


TIAN_SHENG_GROUPS = [
    TianShengGroup(0, '第一声', ['平声辟清', '上声辟清', '去声辟清', '入声辟清'], '日象·辟·清'),
    TianShengGroup(1, '第二声', ['平声辟浊', '上声辟浊', '去声辟浊', '入声辟浊'], '月象·辟·浊'),
    TianShengGroup(2, '第三声', ['平声翕清', '上声翕清', '去声翕清', '入声翕清'], '星象·翕·清'),
    TianShengGroup(3, '第四声', ['平声翕浊', '上声翕浊', '去声翕浊', '入声翕浊'], '辰象·翕·浊'),
    TianShengGroup(4, '第五声', ['平声辟清', '上声辟清', '去声辟清', '入声辟清'], '日象·辟·清'),
    TianShengGroup(5, '第六声', ['平声辟浊', '上声辟浊', '去声辟浊', '入声辟浊'], '月象·辟·浊'),
    TianShengGroup(6, '第七声', ['平声翕清', '上声翕清', '去声翕清', '入声翕清'], '星象·翕·清'),
    TianShengGroup(7, '第八声', ['平声翕浊', '上声翕浊', '去声翕浊', '入声翕浊'], '辰象·翕·浊'),
    TianShengGroup(8, '第九声', ['平声辟清', '上声辟清', '去声辟清', '入声辟清'], '日象·辟·清'),
    TianShengGroup(9, '第十声', ['平声辟浊', '上声辟浊', '去声辟浊', '入声辟浊'], '月象·辟·浊'),
]


# === 地音（声母部类）===

@dataclass
class DiYinGroup:
    """地音组"""
    index: int           # 组序号 0-11（对应地支）
    name: str            # 组名
    element: str         # 四象属性
    method: str          # 发音方法
    clarity: str         # 清浊


DI_YIN_GROUPS = [
    DiYinGroup(0, '第一音', '水', '开', '清'),
    DiYinGroup(1, '第二音', '水', '开', '浊'),
    DiYinGroup(2, '第三音', '水', '发', '清'),
    DiYinGroup(3, '第四音', '水', '发', '浊'),
    DiYinGroup(4, '第五音', '火', '收', '清'),
    DiYinGroup(5, '第六音', '火', '收', '浊'),
    DiYinGroup(6, '第七音', '火', '闭', '清'),
    DiYinGroup(7, '第八音', '火', '闭', '浊'),
    DiYinGroup(8, '第九音', '土', '开', '清'),
    DiYinGroup(9, '第十音', '土', '开', '浊'),
    DiYinGroup(10, '第十一音', '石', '发', '清'),
    DiYinGroup(11, '第十二音', '石', '发', '浊'),
]


# === 唱和矩阵（10×12 精选字例）===
# 行=天声组(0-9), 列=地音组(0-11)
# 每个位置对应一个代表字（空位用○标记）

CHANGHE_MATRIX = [
    # 第一声 × 十二地音
    ['多', '内', '乃', '良', '千', '刀', '妻', '高', '交', '○', '○', '○'],
    # 第二声 × 十二地音
    ['陀', '泥', '来', '○', '田', '桃', '齐', '毫', '○', '○', '○', '○'],
    # 第三声 × 十二地音
    ['都', '奴', '鲁', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第四声 × 十二地音
    ['回', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第五声 × 十二地音
    ['波', '莫', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第六声 × 十二地音
    ['婆', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第七声 × 十二地音
    ['布', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第八声 × 十二地音
    ['蒲', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第九声 × 十二地音
    ['巴', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
    # 第十声 × 十二地音
    ['爬', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○', '○'],
]


@dataclass
class ChangheResult:
    """唱和查询结果"""
    tian_sheng: TianShengGroup   # 天声组
    di_yin: DiYinGroup           # 地音组
    character: str               # 对应字例
    lv: LvLv                     # 对应律吕
    description: str             # 描述


class ChangheSystem:
    """声音唱和系统"""

    def query_by_ganzhi(self, gan_index: int, zhi_index: int) -> ChangheResult:
        """
        根据干支查询唱和位置

        天干(0-9) → 天声组
        地支(0-11) → 地音组
        """
        tian_sheng = TIAN_SHENG_GROUPS[gan_index % 10]
        di_yin = DI_YIN_GROUPS[zhi_index % 12]
        char = CHANGHE_MATRIX[gan_index % 10][zhi_index % 12]
        lv = get_day_lv(gan_index)

        desc = (
            f"天声{tian_sheng.name}({tian_sheng.attribute}) × "
            f"地音{di_yin.name}({di_yin.element}·{di_yin.method}·{di_yin.clarity})"
        )

        return ChangheResult(
            tian_sheng=tian_sheng,
            di_yin=di_yin,
            character=char,
            lv=lv,
            description=desc,
        )

    def get_daily_changhe(self, day_gan_index: int, day_zhi_index: int) -> dict:
        """获取某日的声音唱和信息"""
        result = self.query_by_ganzhi(day_gan_index, day_zhi_index)
        day_lv = get_day_lv(day_gan_index)
        hour_lv = get_hour_lv(day_zhi_index)

        return {
            'tian_sheng': {
                'group': result.tian_sheng.name,
                'attribute': result.tian_sheng.attribute,
            },
            'di_yin': {
                'group': result.di_yin.name,
                'element': result.di_yin.element,
                'method': result.di_yin.method,
                'clarity': result.di_yin.clarity,
            },
            'character': result.character,
            'lv': {
                'name': day_lv.name,
                'type': day_lv.type,
                'frequency_ratio': day_lv.frequency_ratio,
            },
            'description': result.description,
        }

    def get_full_matrix(self) -> dict:
        """获取完整的唱和矩阵"""
        return {
            'rows': [{'index': g.index, 'name': g.name, 'attribute': g.attribute}
                     for g in TIAN_SHENG_GROUPS],
            'cols': [{'index': g.index, 'name': g.name, 'element': g.element,
                      'method': g.method, 'clarity': g.clarity}
                     for g in DI_YIN_GROUPS],
            'matrix': CHANGHE_MATRIX,
        }

    def get_lvlv_info(self, gan_index: int, zhi_index: int) -> dict:
        """获取完整的四柱律吕信息"""
        return {
            'year_lv': {'name': get_year_lv(gan_index).name, 'type': get_year_lv(gan_index).type},
            'month_lv': {'name': get_month_lv(zhi_index).name, 'type': get_month_lv(zhi_index).type},
            'day_lv': {'name': get_day_lv(gan_index).name, 'type': get_day_lv(gan_index).type},
            'hour_lv': {'name': get_hour_lv(zhi_index).name, 'type': get_hour_lv(zhi_index).type},
        }
