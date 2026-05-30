from __future__ import annotations
"""
周期分析 API 路由
"""

from fastapi import APIRouter, Query

from ..schemas import (
    CycleAnalysisResponse, CyclePointResponse, HexagramResponse,
    TrendReportResponse, TrendNodeResponse, HexagramChainResponse,
    CoordinateResponse,
)
from ...analysis.cycle_analyzer import CycleAnalyzer
from ...analysis.trend_engine import TrendEngine
from .hexagram import hexagram_to_response, chain_to_response

router = APIRouter()
cycle_analyzer = CycleAnalyzer()
trend_engine = TrendEngine()


@router.get("/cycle/sui")
def analyze_sui_cycle(
    start: int = Query(..., description="起始年份"),
    end: int = Query(..., description="结束年份"),
):
    """分析岁级周期（逐年卦象变化）"""
    if end - start > 200:
        return {'error': '时间范围不能超过200年（岁级分析）'}

    result = cycle_analyzer.analyze_sui_cycle(start, end)

    points = []
    for p in result.points:
        points.append(CyclePointResponse(
            year=p.year,
            hexagram=hexagram_to_response(p.hexagram),
            yang_count=p.yang_count,
            upper_wuxing=p.upper_wuxing,
            lower_wuxing=p.lower_wuxing,
            wuxing_relation=p.wuxing_relation,
            energy_level=p.energy_level,
        ))

    return CycleAnalysisResponse(
        start_year=result.start_year,
        end_year=result.end_year,
        level=result.level,
        points=points,
        turning_points=result.turning_points,
        dominant_wuxing=result.dominant_wuxing,
        cycle_length=result.cycle_length,
    )


@router.get("/cycle/yun")
def analyze_yun_cycle(
    start: int = Query(default=-2000, description="起始年份"),
    end: int = Query(default=2100, description="结束年份"),
):
    """分析运级周期（每360年）"""
    result = cycle_analyzer.analyze_yun_cycle(start, end)

    points = []
    for p in result.points:
        points.append(CyclePointResponse(
            year=p.year,
            hexagram=hexagram_to_response(p.hexagram),
            yang_count=p.yang_count,
            upper_wuxing=p.upper_wuxing,
            lower_wuxing=p.lower_wuxing,
            wuxing_relation=p.wuxing_relation,
            energy_level=p.energy_level,
        ))

    return CycleAnalysisResponse(
        start_year=result.start_year,
        end_year=result.end_year,
        level=result.level,
        points=points,
        turning_points=result.turning_points,
        dominant_wuxing=result.dominant_wuxing,
        cycle_length=result.cycle_length,
    )


@router.get("/cycle/xiaoxi")
def analyze_xiaoxi_cycle():
    """分析十二消息卦的阴阳消长周期"""
    results = cycle_analyzer.analyze_消息卦_cycle(0, 0)
    return {'cycle': results}


@router.get("/trend/{year}")
def get_trend_report(
    year: int,
    years: int = Query(default=60, ge=1, le=360, description="推演年数"),
):
    """从指定年份起的趋势推演"""
    report = trend_engine.generate_report(year, years)

    nodes = []
    for n in report.nodes:
        nodes.append(TrendNodeResponse(
            year=n.year,
            hexagram=hexagram_to_response(n.hexagram),
            level=n.level,
            event_type=n.event_type,
            description=n.description,
            energy=n.energy,
            significance=n.significance,
        ))

    return TrendReportResponse(
        base_year=report.base_year,
        target_years=report.target_years,
        current_chain=chain_to_response(report.current_chain),
        nodes=nodes,
        overall_trend=report.overall_trend,
        key_years=report.key_years,
    )
