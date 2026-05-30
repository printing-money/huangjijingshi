"""
祝泌算法 - 先天60卦序列平推法

祝泌《观物篇解》的岁卦推演方式：
- 运卦/世卦：与黄畿相同
- 岁卦：从世卦在先天60卦序中的位置开始，逐年步进（平推）
- 60年一循环，恰好对应六十甲子

与黄畿算法的区别：
- 黄畿：运卦→变爻→经卦(60年)→挨六十卦次→年卦
- 祝泌：世卦→定位先天圆图→逐年平推步进

验证数据（来自 ref/react-yhys）：
  1984=鼎, 1985=恒, 1986=巽, 2025=革, 2026=同人
"""

from __future__ import annotations

from .hexagram import (
    Hexagram, get_hexagram,
    XIANTIAN_60_SEQUENCE,
)
from .huangji_algorithm import HuangjiEngine


class ZhubiEngine:
    """祝泌推演引擎"""

    def __init__(self):
        self._huangji = HuangjiEngine()

    def get_yun_hexagram(self, hui_index: int, yun_in_hui: int) -> Hexagram:
        """运卦：与黄畿相同"""
        return self._huangji.get_yun_hexagram(hui_index, yun_in_hui)

    def get_shi_hexagram(self, hui_index: int, yun_in_hui: int, shi_in_yun: int) -> Hexagram:
        """世卦：与黄畿相同"""
        return self._huangji.get_shi_hexagram(hui_index, yun_in_hui, shi_in_yun)

    def get_sui_hexagram(self, gregorian_year: int) -> Hexagram:
        """
        祝泌岁卦：先天60卦序列平推法

        核心规则：
        1. 以甲子年(1984)所在世的世卦在先天60卦序中的位置为固定起点
        2. 从该位置开始，按年份偏移逐年步进
        3. 60卦序列循环使用（对应60甲子周期）
        """
        # 找到甲子年(1984)所在世的世卦
        jiazi_huangji = 1984 + 67017  # 69001
        global_shi = max(1, (jiazi_huangji + 29) // 30)
        hui_index = ((global_shi - 1) // 360) % 12
        shi_in_hui = (global_shi - 1) % 360
        yun_in_hui = shi_in_hui // 12
        shi_in_yun = shi_in_hui % 12

        jiazi_shi_hex = self.get_shi_hexagram(hui_index, yun_in_hui, shi_in_yun)

        # 世卦在先天60卦序中的起始位置
        try:
            start_index = XIANTIAN_60_SEQUENCE.index(jiazi_shi_hex.binary)
        except ValueError:
            start_index = 0

        # 计算年份偏移（相对于1984），60年周期内连续步进
        year_offset = (gregorian_year - 1984) % 60
        if year_offset < 0:
            year_offset += 60

        # 平推
        sui_index = (start_index + year_offset) % 60
        return get_hexagram(XIANTIAN_60_SEQUENCE[sui_index])


# 全局实例
zhubi_engine = ZhubiEngine()
