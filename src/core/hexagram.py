"""
六十四卦数据与基础运算

卦象用6位二进制表示（从初爻到上爻）：
- 阳爻 = 1, 阴爻 = 0
- 乾卦 = 111111 = 63, 坤卦 = 000000 = 0

核心运算：
- 变爻（XOR）
- 先天64卦序 / 先天60卦序
- 四正卦处理
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class Hexagram:
    """卦象数据"""
    binary: int       # 6位二进制值 (0-63)
    name: str         # 卦名
    unicode: str      # Unicode 卦象符号
    upper: str        # 上卦名（外卦）
    lower: str        # 下卦名（内卦）

    def __repr__(self) -> str:
        return f"{self.unicode}{self.name}"

    @property
    def yang_count(self) -> int:
        """阳爻数量"""
        return bin(self.binary).count('1')

    @property
    def yin_count(self) -> int:
        """阴爻数量"""
        return 6 - self.yang_count

    @property
    def yao_list(self) -> List[int]:
        """从初爻到上爻的爻列表（1=阳, 0=阴）"""
        return [(self.binary >> i) & 1 for i in range(6)]


# 八卦（三爻）
TRIGRAM_NAMES = ['坤', '震', '坎', '兑', '艮', '离', '巽', '乾']

# 六十四卦名（按二进制顺序 0-63）
HEXAGRAM_NAMES: dict[int, str] = {
    0: '坤', 1: '复', 2: '师', 3: '临', 4: '谦', 5: '明夷', 6: '升', 7: '泰',
    8: '豫', 9: '震', 10: '解', 11: '归妹', 12: '小过', 13: '丰', 14: '恒', 15: '大壮',
    16: '比', 17: '屯', 18: '坎', 19: '节', 20: '蹇', 21: '既济', 22: '井', 23: '需',
    24: '萃', 25: '随', 26: '困', 27: '兑', 28: '咸', 29: '革', 30: '大过', 31: '夬',
    32: '剥', 33: '颐', 34: '蒙', 35: '损', 36: '艮', 37: '贲', 38: '蛊', 39: '大畜',
    40: '晋', 41: '噬嗑', 42: '未济', 43: '睽', 44: '旅', 45: '离', 46: '鼎', 47: '大有',
    48: '观', 49: '益', 50: '涣', 51: '中孚', 52: '渐', 53: '家人', 54: '巽', 55: '小畜',
    56: '否', 57: '无妄', 58: '讼', 59: '履', 60: '遁', 61: '同人', 62: '姤', 63: '乾',
}

# Unicode 卦象符号（U+4DC0 - U+4DFF，按周易序映射到二进制）
BINARY_TO_UNICODE: dict[int, str] = {
    0: '䷁', 1: '䷗', 2: '䷆', 3: '䷒', 4: '䷎', 5: '䷣', 6: '䷭', 7: '䷊',
    8: '䷏', 9: '䷲', 10: '䷧', 11: '䷵', 12: '䷽', 13: '䷶', 14: '䷟', 15: '䷡',
    16: '䷇', 17: '䷂', 18: '䷜', 19: '䷻', 20: '䷦', 21: '䷾', 22: '䷯', 23: '䷄',
    24: '䷬', 25: '䷐', 26: '䷮', 27: '䷹', 28: '䷞', 29: '䷰', 30: '䷛', 31: '䷪',
    32: '䷖', 33: '䷚', 34: '䷃', 35: '䷨', 36: '䷳', 37: '䷕', 38: '䷑', 39: '䷙',
    40: '䷢', 41: '䷔', 42: '䷿', 43: '䷥', 44: '䷷', 45: '䷝', 46: '䷱', 47: '䷍',
    48: '䷓', 49: '䷩', 50: '䷺', 51: '䷼', 52: '䷴', 53: '䷤', 54: '䷸', 55: '䷈',
    56: '䷋', 57: '䷘', 58: '䷅', 59: '䷉', 60: '䷠', 61: '䷌', 62: '䷫', 63: '䷀',
}
# 四正卦（乾坤坎离）二进制值
FOUR_PRINCIPAL = frozenset([63, 0, 18, 45])  # 乾、坤、坎、离

# 十二辟卦（消息卦）按子丑寅卯辰巳午未申酉戌亥顺序
TWELVE_SOVEREIGN = [
    1,   # 子：复（地雷复）000001
    3,   # 丑：临（地泽临）000011
    7,   # 寅：泰（地天泰）000111
    15,  # 卯：大壮（雷天大壮）001111
    31,  # 辰：夬（泽天夬）011111
    63,  # 巳：乾（乾为天）111111
    62,  # 午：姤（天风姤）111110
    60,  # 未：遁（天山遁）111100
    56,  # 申：否（天地否）111000
    48,  # 酉：观（风地观）110000
    32,  # 戌：剥（山地剥）100000
    0,   # 亥：坤（坤为地）000000
]

# 先天六十四卦序（邵雍方圆图，从乾开始顺时针）
XIANTIAN_64_SEQUENCE = [
    63, 62, 30, 46, 14, 54, 22, 38, 6, 58, 26, 42, 10, 50, 18, 34, 2,
    60, 28, 44, 12, 52, 20, 36, 4, 56, 24, 40, 8, 48, 16, 32,
    0, 1, 33, 17, 49, 9, 41, 25, 57, 5, 37, 21, 53, 13, 45, 29, 61,
    3, 35, 19, 51, 11, 43, 27, 59, 7, 39, 23, 55, 15, 47, 31,
]

# 先天六十卦序（剔除四正卦：乾坤坎离）
XIANTIAN_60_SEQUENCE = [b for b in XIANTIAN_64_SEQUENCE if b not in FOUR_PRINCIPAL]


def get_hexagram(binary: int) -> Hexagram:
    """根据二进制值获取卦象信息"""
    b = binary & 0x3F
    lower = b & 0x07
    upper = (b >> 3) & 0x07
    return Hexagram(
        binary=b,
        name=HEXAGRAM_NAMES.get(b, '未知'),
        unicode=BINARY_TO_UNICODE.get(b, '?'),
        upper=TRIGRAM_NAMES[upper],
        lower=TRIGRAM_NAMES[lower],
    )


def change_yao(binary: int, yao: int) -> int:
    """
    变爻：翻转指定爻的阴阳状态

    Args:
        binary: 卦的二进制值
        yao: 爻位（1-6，从初爻到上爻）

    Returns:
        变化后的卦二进制值
    """
    if yao < 1 or yao > 6:
        return binary
    mask = 1 << (yao - 1)
    return (binary ^ mask) & 0x3F


def find_pos_in_60(binary: int) -> int:
    """
    在先天60卦序中查找位置，处理四正卦 fallback

    当变爻结果为四正卦时，回退到64卦序定位再映射回60序。
    """
    try:
        return XIANTIAN_60_SEQUENCE.index(binary)
    except ValueError:
        pass

    # 四正卦 fallback
    try:
        pos64 = XIANTIAN_64_SEQUENCE.index(binary)
    except ValueError:
        return 0

    # 计算64序位置之前有几个四正卦
    principals_before = sum(
        1 for i in range(pos64)
        if XIANTIAN_64_SEQUENCE[i] in FOUR_PRINCIPAL
    )
    return pos64 - principals_before


def is_four_principal(binary: int) -> bool:
    """判断是否为四正卦"""
    return binary in FOUR_PRINCIPAL


def get_hexagram_by_name(name: str) -> Optional[Hexagram]:
    """根据卦名获取卦象"""
    for binary, n in HEXAGRAM_NAMES.items():
        if n == name:
            return get_hexagram(binary)
    return None
