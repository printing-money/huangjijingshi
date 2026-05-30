from __future__ import annotations
"""
历史验证引擎

将历史重大事件与皇极经世卦象对应，验证推演规律：
- 内置中国历史重大事件数据库
- 事件→卦象映射
- 统计分析：特定卦象出现时的事件类型分布
- 模式匹配：相似卦象组合的历史对照
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from ..core.hexagram import Hexagram
from ..core.huangji_algorithm import HuangjiEngine, HexagramChain
from ..core.tiangan_dizhi import year_to_coordinate, HuangjiCoordinate


class EventType(Enum):
    """历史事件类型"""
    DYNASTY_CHANGE = "朝代更替"
    WAR = "战争"
    REFORM = "变革"
    PROSPERITY = "盛世"
    DECLINE = "衰落"
    DISASTER = "灾难"
    CULTURAL = "文化"
    TECHNOLOGY = "科技"
    FOUNDING = "建国"
    COLLAPSE = "灭亡"


@dataclass
class HistoryEvent:
    """历史事件"""
    year: int                    # 公历年份
    name: str                    # 事件名称
    event_type: EventType        # 事件类型
    description: str = ''        # 描述
    significance: int = 5        # 重要性（1-10）


@dataclass
class EventHexagramMapping:
    """事件与卦象的映射"""
    event: HistoryEvent
    coordinate: HuangjiCoordinate
    chain: HexagramChain
    analysis: dict = field(default_factory=dict)


# 内置历史事件数据库（精选重大事件）
HISTORY_EVENTS: list[HistoryEvent] = [
    # 上古
    HistoryEvent(-2070, "夏朝建立", EventType.FOUNDING, "禹建立夏朝", 9),
    HistoryEvent(-1600, "商汤灭夏", EventType.DYNASTY_CHANGE, "商朝建立", 9),
    HistoryEvent(-1046, "武王伐纣", EventType.DYNASTY_CHANGE, "周朝建立", 10),
    HistoryEvent(-771, "西周灭亡", EventType.COLLAPSE, "犬戎攻破镐京", 8),
    HistoryEvent(-770, "东周建立", EventType.FOUNDING, "平王东迁洛邑", 7),

    # 春秋战国
    HistoryEvent(-551, "孔子诞生", EventType.CULTURAL, "儒学创始人", 10),
    HistoryEvent(-403, "三家分晋", EventType.DYNASTY_CHANGE, "战国开始", 8),
    HistoryEvent(-221, "秦统一六国", EventType.FOUNDING, "秦始皇统一天下", 10),

    # 秦汉
    HistoryEvent(-206, "秦朝灭亡", EventType.COLLAPSE, "刘邦入关", 9),
    HistoryEvent(-202, "西汉建立", EventType.FOUNDING, "刘邦称帝", 9),
    HistoryEvent(8, "王莽篡汉", EventType.DYNASTY_CHANGE, "新朝建立", 7),
    HistoryEvent(25, "东汉建立", EventType.FOUNDING, "光武中兴", 8),
    HistoryEvent(220, "东汉灭亡", EventType.COLLAPSE, "曹丕篡汉", 8),

    # 三国两晋南北朝
    HistoryEvent(220, "三国鼎立", EventType.WAR, "魏蜀吴三分天下", 8),
    HistoryEvent(280, "西晋统一", EventType.FOUNDING, "司马炎统一", 7),
    HistoryEvent(316, "西晋灭亡", EventType.COLLAPSE, "五胡乱华", 8),
    HistoryEvent(420, "南朝宋建立", EventType.DYNASTY_CHANGE, "刘裕代晋", 6),
    HistoryEvent(581, "隋朝建立", EventType.FOUNDING, "杨坚代周", 8),

    # 隋唐
    HistoryEvent(618, "唐朝建立", EventType.FOUNDING, "李渊建唐", 10),
    HistoryEvent(627, "贞观之治", EventType.PROSPERITY, "唐太宗治世", 9),
    HistoryEvent(713, "开元盛世", EventType.PROSPERITY, "唐玄宗前期", 9),
    HistoryEvent(755, "安史之乱", EventType.WAR, "唐朝由盛转衰", 9),
    HistoryEvent(907, "唐朝灭亡", EventType.COLLAPSE, "朱温篡唐", 8),

    # 宋元
    HistoryEvent(960, "北宋建立", EventType.FOUNDING, "赵匡胤陈桥兵变", 9),
    HistoryEvent(1011, "邵雍诞生", EventType.CULTURAL, "皇极经世作者", 8),
    HistoryEvent(1069, "王安石变法", EventType.REFORM, "熙宁变法", 7),
    HistoryEvent(1127, "靖康之变", EventType.COLLAPSE, "北宋灭亡", 9),
    HistoryEvent(1127, "南宋建立", EventType.FOUNDING, "赵构南渡", 8),
    HistoryEvent(1206, "蒙古帝国建立", EventType.FOUNDING, "成吉思汗统一蒙古", 9),
    HistoryEvent(1271, "元朝建立", EventType.DYNASTY_CHANGE, "忽必烈建元", 8),
    HistoryEvent(1279, "南宋灭亡", EventType.COLLAPSE, "崖山之战", 8),

    # 明清
    HistoryEvent(1368, "明朝建立", EventType.FOUNDING, "朱元璋建明", 9),
    HistoryEvent(1405, "郑和下西洋", EventType.CULTURAL, "七次远航", 7),
    HistoryEvent(1644, "明朝灭亡", EventType.COLLAPSE, "李自成入京", 9),
    HistoryEvent(1644, "清朝入关", EventType.DYNASTY_CHANGE, "满清入主中原", 9),
    HistoryEvent(1661, "康熙即位", EventType.PROSPERITY, "康乾盛世开始", 8),
    HistoryEvent(1840, "鸦片战争", EventType.WAR, "近代史开端", 10),
    HistoryEvent(1851, "太平天国", EventType.WAR, "洪秀全起义", 8),
    HistoryEvent(1898, "戊戌变法", EventType.REFORM, "百日维新", 7),
    HistoryEvent(1911, "辛亥革命", EventType.DYNASTY_CHANGE, "推翻帝制", 10),
    HistoryEvent(1912, "中华民国建立", EventType.FOUNDING, "亚洲第一个共和国", 9),

    # 现代
    HistoryEvent(1937, "全面抗战", EventType.WAR, "七七事变", 9),
    HistoryEvent(1945, "抗战胜利", EventType.WAR, "日本投降", 9),
    HistoryEvent(1949, "新中国成立", EventType.FOUNDING, "中华人民共和国", 10),
    HistoryEvent(1966, "文化大革命", EventType.REFORM, "十年动荡", 8),
    HistoryEvent(1978, "改革开放", EventType.REFORM, "邓小平改革", 10),
    HistoryEvent(2001, "加入WTO", EventType.PROSPERITY, "融入全球经济", 7),
    HistoryEvent(2008, "北京奥运", EventType.CULTURAL, "百年奥运梦", 6),
    HistoryEvent(2020, "新冠疫情", EventType.DISASTER, "全球大流行", 8),
]


class HistoryValidator:
    """历史验证引擎"""

    def __init__(self):
        self.engine = HuangjiEngine()
        self.events = HISTORY_EVENTS

    def map_event(self, event: HistoryEvent) -> EventHexagramMapping:
        """将历史事件映射到卦象"""
        coord = year_to_coordinate(event.year)
        chain = self.engine.compute_chain(event.year)

        # 分析卦象特征
        analysis = {
            'sui_yang_count': chain.sui.yang_count,
            'yun_yang_count': chain.yun.yang_count,
            'shi_yang_count': chain.shi.yang_count,
            'sui_upper_trigram': chain.sui.upper,
            'sui_lower_trigram': chain.sui.lower,
        }

        return EventHexagramMapping(
            event=event,
            coordinate=coord,
            chain=chain,
            analysis=analysis,
        )

    def validate_all(self) -> list[EventHexagramMapping]:
        """验证所有历史事件"""
        return [self.map_event(e) for e in self.events]

    def find_events_by_hexagram(self, hexagram_name: str,
                                level: str = 'sui') -> list[EventHexagramMapping]:
        """
        查找特定卦象对应的历史事件

        Args:
            hexagram_name: 卦名
            level: 层级（sui/yun/shi）
        """
        results = []
        for event in self.events:
            chain = self.engine.compute_chain(event.year)
            target_hex = getattr(chain, level, None)
            if target_hex and target_hex.name == hexagram_name:
                mapping = self.map_event(event)
                results.append(mapping)
        return results

    def find_similar_periods(self, target_year: int, depth: int = 3) -> list[dict]:
        """
        查找历史上与目标年份卦象组合相似的时期

        Args:
            target_year: 目标年份
            depth: 匹配深度（匹配几层卦象）
        """
        target_chain = self.engine.compute_chain(target_year)
        target_features = [
            target_chain.sui.binary,
            target_chain.yun.binary,
            target_chain.shi.binary,
        ][:depth]

        similar = []
        for event in self.events:
            chain = self.engine.compute_chain(event.year)
            features = [
                chain.sui.binary,
                chain.yun.binary,
                chain.shi.binary,
            ][:depth]

            # 计算相似度
            match_count = sum(1 for a, b in zip(target_features, features) if a == b)
            if match_count > 0:
                similar.append({
                    'event': event,
                    'match_count': match_count,
                    'match_ratio': match_count / depth,
                    'chain': chain,
                })

        similar.sort(key=lambda x: x['match_ratio'], reverse=True)
        return similar

    def statistics_by_type(self) -> dict[str, dict]:
        """
        按事件类型统计卦象分布

        返回每种事件类型中各卦象出现的频率
        """
        stats: dict[str, dict] = {}

        for event in self.events:
            chain = self.engine.compute_chain(event.year)
            type_name = event.event_type.value

            if type_name not in stats:
                stats[type_name] = {
                    'count': 0,
                    'hexagrams': {},
                    'avg_yang': 0,
                    'total_yang': 0,
                }

            stats[type_name]['count'] += 1
            stats[type_name]['total_yang'] += chain.sui.yang_count

            hex_name = chain.sui.name
            stats[type_name]['hexagrams'][hex_name] = \
                stats[type_name]['hexagrams'].get(hex_name, 0) + 1

        # 计算平均阳爻数
        for type_name, data in stats.items():
            if data['count'] > 0:
                data['avg_yang'] = data['total_yang'] / data['count']

        return stats
