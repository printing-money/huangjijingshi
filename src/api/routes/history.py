from __future__ import annotations
"""
历史验证 API 路由
"""

from fastapi import APIRouter, Query
from typing import Optional

from ..schemas import HistoryEventResponse, HexagramChainResponse, SimilarPeriodResponse
from ...analysis.history_validator import HistoryValidator, HISTORY_EVENTS
from .hexagram import hexagram_to_response, chain_to_response

router = APIRouter()
validator = HistoryValidator()


@router.get("/events")
def list_events(
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    min_significance: int = Query(default=1, ge=1, le=10),
):
    """列出所有历史事件及其卦象"""
    events = HISTORY_EVENTS

    if event_type:
        events = [e for e in events if e.event_type.value == event_type]

    events = [e for e in events if e.significance >= min_significance]

    results = []
    for event in events:
        mapping = validator.map_event(event)
        results.append({
            'year': event.year,
            'name': event.name,
            'event_type': event.event_type.value,
            'description': event.description,
            'significance': event.significance,
            'coordinate': {
                'hui': mapping.coordinate.hui,
                'yun': mapping.coordinate.yun,
                'global_yun': mapping.coordinate.global_yun,
                'shi': mapping.coordinate.shi,
            },
            'hexagrams': {
                'sui': mapping.chain.sui.name,
                'yun': mapping.chain.yun.name,
                'shi': mapping.chain.shi.name,
            },
        })

    return {'count': len(results), 'events': results}


@router.get("/validate")
def validate_all():
    """验证所有历史事件与卦象的关联"""
    mappings = validator.validate_all()

    results = []
    for m in mappings:
        results.append({
            'year': m.event.year,
            'name': m.event.name,
            'event_type': m.event.type.value if hasattr(m.event, 'type') else m.event.event_type.value,
            'sui_hexagram': m.chain.sui.name,
            'yun_hexagram': m.chain.yun.name,
            'shi_hexagram': m.chain.shi.name,
            'sui_yang_count': m.analysis['sui_yang_count'],
        })

    return {'count': len(results), 'mappings': results}


@router.get("/search/{hexagram_name}")
def search_by_hexagram(
    hexagram_name: str,
    level: str = Query(default='sui', description="层级: sui/yun/shi"),
):
    """按卦象搜索历史事件"""
    mappings = validator.find_events_by_hexagram(hexagram_name, level)

    results = []
    for m in mappings:
        results.append({
            'year': m.event.year,
            'name': m.event.name,
            'event_type': m.event.event_type.value,
            'significance': m.event.significance,
        })

    return {
        'hexagram': hexagram_name,
        'level': level,
        'count': len(results),
        'events': results,
    }


@router.get("/similar/{year}")
def find_similar(
    year: int,
    depth: int = Query(default=3, ge=1, le=3, description="匹配深度"),
):
    """查找历史上与指定年份卦象组合相似的时期"""
    similar = validator.find_similar_periods(year, depth)

    results = []
    for s in similar:
        results.append({
            'year': s['event'].year,
            'name': s['event'].name,
            'event_type': s['event'].event_type.value,
            'similarity': s['match_ratio'],
            'matches': s['match_count'],
        })

    return {
        'target_year': year,
        'depth': depth,
        'similar_periods': results,
    }


@router.get("/statistics")
def get_statistics():
    """按事件类型统计卦象分布"""
    stats = validator.statistics_by_type()
    return {'statistics': stats}
