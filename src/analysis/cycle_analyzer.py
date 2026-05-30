from __future__ import annotations
"""
周期分析引擎

基于卦象的阴阳消长、五行生克，建立时间周期模型：
- 阴阳消长周期：十二消息卦的阴阳爻数变化
- 卦气升降：运卦/世卦的阳爻数随时间变化
- 五行周期：卦象上下卦五行属性的周期性变化
- 重卦周期：同一卦象在不同层级重复出现的规律
"""

from dataclasses import dataclass, field
from typing import Optional

from ..core.hexagram import Hexagram, get_hexagram, TWELVE_SOVEREIGN, TRIGRAM_NAMES
from ..core.huangji_algorithm import HuangjiEngine
from ..core.tiangan_dizhi import WUXING, TIANGAN_WUXING, DIZHI_WUXING


# 八卦五行对应
TRIGRAM_WUXING = {
    '乾': '金', '兑': '金',
    '离': '火',
    '震': '木', '巽': '木',
    '坎': '水',
    '艮': '土', '坤': '土',
}

# 五行生克关系
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 生
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}    # 克


@dataclass
class CyclePoint:
    """周期分析数据点"""
    year: int
    hexagram: Hexagram
    yang_count: int          # 阳爻数
    upper_wuxing: str        # 上卦五行
    lower_wuxing: str        # 下卦五行
    wuxing_relation: str     # 五行关系（生/克/比和）
    energy_level: float      # 能量水平（0-1）


@dataclass
class CycleAnalysis:
    """周期分析结果"""
    start_year: int
    end_year: int
    level: str               # 分析层级（运/世/岁）
    points: list[CyclePoint] = field(default_factory=list)
    turning_points: list[int] = field(default_factory=list)  # 转折年份
    dominant_wuxing: str = ''     # 主导五行
    cycle_length: int = 0         # 周期长度


class CycleAnalyzer:
    """周期分析器"""

    def __init__(self):
        self.engine = HuangjiEngine()

    def get_wuxing_relation(self, upper: str, lower: str) -> str:
        """判断上下卦五行关系"""
        upper_wx = TRIGRAM_WUXING.get(upper, '土')
        lower_wx = TRIGRAM_WUXING.get(lower, '土')

        if upper_wx == lower_wx:
            return '比和'
        elif WUXING_SHENG.get(lower_wx) == upper_wx:
            return '下生上'
        elif WUXING_SHENG.get(upper_wx) == lower_wx:
            return '上生下'
        elif WUXING_KE.get(upper_wx) == lower_wx:
            return '上克下'
        elif WUXING_KE.get(lower_wx) == upper_wx:
            return '下克上'
        return '无关'

    def compute_energy(self, hexagram: Hexagram) -> float:
        """
        计算卦象能量水平

        综合考虑：
        - 阳爻数（阳气强度）
        - 五行关系（生为顺，克为逆）
        - 卦象在消息卦中的位置
        """
        # 基础能量：阳爻比例
        yang_ratio = hexagram.yang_count / 6.0

        # 五行关系修正
        relation = self.get_wuxing_relation(hexagram.upper, hexagram.lower)
        relation_factor = {
            '比和': 1.0,
            '下生上': 0.9,
            '上生下': 0.8,
            '上克下': 0.6,
            '下克上': 0.4,
        }.get(relation, 0.7)

        return yang_ratio * 0.7 + relation_factor * 0.3

    def analyze_yun_cycle(self, start_year: int, end_year: int) -> CycleAnalysis:
        """
        分析运级周期（每360年一运）

        返回指定时间范围内运卦的变化趋势
        """
        points = []
        turning_points = []
        prev_yang = -1

        for year in range(start_year, end_year + 1, 360):
            chain = self.engine.compute_chain(year)
            hex_ = chain.yun
            yang = hex_.yang_count
            upper_wx = TRIGRAM_WUXING.get(hex_.upper, '土')
            lower_wx = TRIGRAM_WUXING.get(hex_.lower, '土')
            relation = self.get_wuxing_relation(hex_.upper, hex_.lower)
            energy = self.compute_energy(hex_)

            point = CyclePoint(
                year=year,
                hexagram=hex_,
                yang_count=yang,
                upper_wuxing=upper_wx,
                lower_wuxing=lower_wx,
                wuxing_relation=relation,
                energy_level=energy,
            )
            points.append(point)

            # 检测转折点（阳爻数变化方向改变）
            if prev_yang >= 0 and yang != prev_yang:
                if len(points) >= 3:
                    p1 = points[-3].yang_count
                    p2 = points[-2].yang_count
                    p3 = yang
                    if (p2 > p1 and p2 > p3) or (p2 < p1 and p2 < p3):
                        turning_points.append(points[-2].year)
            prev_yang = yang

        return CycleAnalysis(
            start_year=start_year,
            end_year=end_year,
            level='运',
            points=points,
            turning_points=turning_points,
        )

    def analyze_sui_cycle(self, start_year: int, end_year: int) -> CycleAnalysis:
        """
        分析岁级周期（逐年）

        返回指定时间范围内岁卦的变化趋势
        """
        points = []
        turning_points = []
        prev_energy = -1.0
        prev_direction = 0  # 1=上升, -1=下降

        for year in range(start_year, end_year + 1):
            hex_ = self.engine.get_sui_hexagram(year)
            upper_wx = TRIGRAM_WUXING.get(hex_.upper, '土')
            lower_wx = TRIGRAM_WUXING.get(hex_.lower, '土')
            relation = self.get_wuxing_relation(hex_.upper, hex_.lower)
            energy = self.compute_energy(hex_)

            point = CyclePoint(
                year=year,
                hexagram=hex_,
                yang_count=hex_.yang_count,
                upper_wuxing=upper_wx,
                lower_wuxing=lower_wx,
                wuxing_relation=relation,
                energy_level=energy,
            )
            points.append(point)

            # 检测能量转折点
            if prev_energy >= 0:
                direction = 1 if energy > prev_energy else (-1 if energy < prev_energy else 0)
                if direction != 0 and prev_direction != 0 and direction != prev_direction:
                    turning_points.append(year - 1)
                if direction != 0:
                    prev_direction = direction
            prev_energy = energy

        # 统计主导五行
        wuxing_count: dict[str, int] = {}
        for p in points:
            for wx in [p.upper_wuxing, p.lower_wuxing]:
                wuxing_count[wx] = wuxing_count.get(wx, 0) + 1
        dominant = max(wuxing_count, key=wuxing_count.get) if wuxing_count else '土'

        return CycleAnalysis(
            start_year=start_year,
            end_year=end_year,
            level='岁',
            points=points,
            turning_points=turning_points,
            dominant_wuxing=dominant,
            cycle_length=60,  # 六十甲子循环
        )

    def analyze_消息卦_cycle(self, start_year: int, end_year: int) -> list[dict]:
        """
        分析十二消息卦的阴阳消长周期

        返回每个会（10800年）的阴阳状态
        """
        results = []
        for hui_idx in range(12):
            binary = TWELVE_SOVEREIGN[hui_idx]
            hex_ = get_hexagram(binary)
            results.append({
                'hui_index': hui_idx,
                'hexagram': hex_,
                'yang_count': hex_.yang_count,
                'phase': '阳长' if hui_idx < 6 else '阴长',
                'description': f"第{hui_idx + 1}会 {hex_.name}卦 阳爻{hex_.yang_count}",
            })
        return results
