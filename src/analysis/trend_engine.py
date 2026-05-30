from __future__ import annotations
"""
趋势推演引擎

基于当前时间点的卦象链，分析未来的卦象变化节点：
- 识别关键转折点（运/世交替、卦气极值、五行转换）
- 输出未来 N 年的卦象趋势报告
- 与历史相似卦象组合进行对照分析
"""

from dataclasses import dataclass, field
from typing import Optional

from ..core.hexagram import Hexagram, get_hexagram
from ..core.huangji_algorithm import HuangjiEngine, HexagramChain
from ..core.tiangan_dizhi import year_to_coordinate, HuangjiCoordinate
from .cycle_analyzer import CycleAnalyzer, TRIGRAM_WUXING, WUXING_SHENG, WUXING_KE


@dataclass
class TrendNode:
    """趋势节点"""
    year: int
    hexagram: Hexagram
    level: str                   # 变化层级
    event_type: str              # 节点类型
    description: str             # 描述
    energy: float                # 能量水平
    significance: int = 5        # 重要性（1-10）


@dataclass
class TrendReport:
    """趋势推演报告"""
    base_year: int
    target_years: int
    current_chain: HexagramChain
    nodes: list[TrendNode] = field(default_factory=list)
    overall_trend: str = ''      # 总体趋势描述
    key_years: list[int] = field(default_factory=list)  # 关键年份


class TrendEngine:
    """趋势推演引擎"""

    def __init__(self):
        self.engine = HuangjiEngine()
        self.cycle_analyzer = CycleAnalyzer()

    def find_transition_points(self, start_year: int, years: int) -> list[TrendNode]:
        """
        查找时间范围内的转折节点

        转折类型：
        - 运交替（每360年）
        - 世交替（每30年）
        - 十年律卦交替（每10年）
        - 岁卦阴阳极值
        - 五行转换
        """
        nodes = []
        end_year = start_year + years

        prev_coord = year_to_coordinate(start_year)
        prev_sui = self.engine.get_sui_hexagram(start_year)
        prev_energy = self.cycle_analyzer.compute_energy(prev_sui)

        for year in range(start_year + 1, end_year + 1):
            coord = year_to_coordinate(year)
            sui = self.engine.get_sui_hexagram(year)
            energy = self.cycle_analyzer.compute_energy(sui)

            # 运交替
            if coord.global_yun != prev_coord.global_yun:
                yun_hex = self.engine.get_yun_hexagram(coord.hui - 1, coord.yun - 1)
                nodes.append(TrendNode(
                    year=year,
                    hexagram=yun_hex,
                    level='运',
                    event_type='运交替',
                    description=f"进入第{coord.global_yun}运 {yun_hex.name}卦",
                    energy=self.cycle_analyzer.compute_energy(yun_hex),
                    significance=9,
                ))

            # 世交替
            elif coord.global_shi != prev_coord.global_shi:
                shi_hex = self.engine.get_shi_hexagram(
                    coord.hui - 1, coord.yun - 1, coord.shi - 1
                )
                nodes.append(TrendNode(
                    year=year,
                    hexagram=shi_hex,
                    level='世',
                    event_type='世交替',
                    description=f"进入第{coord.shi}世 {shi_hex.name}卦",
                    energy=self.cycle_analyzer.compute_energy(shi_hex),
                    significance=7,
                ))

            # 十年律卦交替
            elif coord.sui % 10 == 1 and coord.sui > 1:
                chain = self.engine.compute_chain(year)
                nodes.append(TrendNode(
                    year=year,
                    hexagram=chain.ten_year,
                    level='十年',
                    event_type='律卦交替',
                    description=f"十年律卦转为 {chain.ten_year.name}卦",
                    energy=self.cycle_analyzer.compute_energy(chain.ten_year),
                    significance=5,
                ))

            # 岁卦阴阳极值（纯阳或纯阴附近）
            if sui.yang_count == 6:
                nodes.append(TrendNode(
                    year=year,
                    hexagram=sui,
                    level='岁',
                    event_type='阳极',
                    description=f"岁卦{sui.name} 纯阳之象，物极必反",
                    energy=1.0,
                    significance=6,
                ))
            elif sui.yang_count == 0:
                nodes.append(TrendNode(
                    year=year,
                    hexagram=sui,
                    level='岁',
                    event_type='阴极',
                    description=f"岁卦{sui.name} 纯阴之象，阳气将生",
                    energy=0.0,
                    significance=6,
                ))

            # 能量突变（大幅变化）
            if abs(energy - prev_energy) > 0.3:
                direction = '升' if energy > prev_energy else '降'
                nodes.append(TrendNode(
                    year=year,
                    hexagram=sui,
                    level='岁',
                    event_type=f'能量突{direction}',
                    description=f"岁卦{sui.name} 能量{direction}变 {prev_energy:.2f}→{energy:.2f}",
                    energy=energy,
                    significance=4,
                ))

            prev_coord = coord
            prev_sui = sui
            prev_energy = energy

        return nodes

    def generate_report(self, base_year: int, years: int = 60) -> TrendReport:
        """
        生成趋势推演报告

        Args:
            base_year: 起始年份
            years: 推演年数（默认60年，一个甲子）
        """
        current_chain = self.engine.compute_chain(base_year)
        nodes = self.find_transition_points(base_year, years)

        # 提取关键年份（重要性 >= 7 的节点）
        key_years = sorted(set(n.year for n in nodes if n.significance >= 7))

        # 分析总体趋势
        cycle = self.cycle_analyzer.analyze_sui_cycle(base_year, base_year + years)
        if cycle.points:
            avg_energy = sum(p.energy_level for p in cycle.points) / len(cycle.points)
            start_energy = cycle.points[0].energy_level
            end_energy = cycle.points[-1].energy_level

            if end_energy > start_energy + 0.1:
                overall = f"总体上升趋势，平均能量{avg_energy:.2f}，主导五行{cycle.dominant_wuxing}"
            elif end_energy < start_energy - 0.1:
                overall = f"总体下降趋势，平均能量{avg_energy:.2f}，主导五行{cycle.dominant_wuxing}"
            else:
                overall = f"总体平稳，平均能量{avg_energy:.2f}，主导五行{cycle.dominant_wuxing}"
        else:
            overall = "数据不足"

        return TrendReport(
            base_year=base_year,
            target_years=years,
            current_chain=current_chain,
            nodes=nodes,
            overall_trend=overall,
            key_years=key_years,
        )

    def compare_with_history(self, target_year: int,
                             history_events: list) -> list[dict]:
        """
        将目标年份的卦象与历史事件对比

        查找卦象组合相似的历史时期
        """
        target_chain = self.engine.compute_chain(target_year)

        comparisons = []
        for event in history_events:
            event_chain = self.engine.compute_chain(event.year)

            # 计算多维相似度
            similarity = 0.0
            matches = []

            if target_chain.sui.binary == event_chain.sui.binary:
                similarity += 0.4
                matches.append('岁卦相同')
            if target_chain.yun.binary == event_chain.yun.binary:
                similarity += 0.3
                matches.append('运卦相同')
            if target_chain.shi.binary == event_chain.shi.binary:
                similarity += 0.2
                matches.append('世卦相同')
            if target_chain.sui.yang_count == event_chain.sui.yang_count:
                similarity += 0.1
                matches.append('阳爻数相同')

            if similarity > 0:
                comparisons.append({
                    'event': event,
                    'similarity': similarity,
                    'matches': matches,
                    'event_chain': event_chain,
                })

        comparisons.sort(key=lambda x: x['similarity'], reverse=True)
        return comparisons[:10]  # 返回前10个最相似的
