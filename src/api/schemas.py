from __future__ import annotations
"""
FastAPI 数据模型（Pydantic schemas）
"""

from pydantic import BaseModel, Field
from typing import Optional


class HexagramResponse(BaseModel):
    """卦象响应"""
    binary: int
    name: str
    unicode: str
    upper: str
    lower: str
    yang_count: int
    yin_count: int


class CoordinateResponse(BaseModel):
    """皇极坐标响应"""
    yuan: int = 1
    hui: int
    yun: int
    global_yun: int
    shi: int
    global_shi: int
    sui: int
    huangji_year: int
    gregorian_year: int


class HexagramChainResponse(BaseModel):
    """九层卦象链响应"""
    coordinate: CoordinateResponse
    yuan: HexagramResponse
    hui: HexagramResponse
    yun: HexagramResponse
    shi: HexagramResponse
    ten_year: HexagramResponse
    sui: HexagramResponse
    yue_jing: Optional[HexagramResponse] = None
    xun_wei: Optional[HexagramResponse] = None
    ri: Optional[HexagramResponse] = None
    shi_jing: Optional[HexagramResponse] = None


class DateTimeRequest(BaseModel):
    """精确时间请求"""
    year: int = Field(..., description="公历年份")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份")
    day: Optional[int] = Field(None, ge=1, le=31, description="日")
    hour: Optional[int] = Field(None, ge=0, le=23, description="小时")


class CyclePointResponse(BaseModel):
    """周期数据点"""
    year: int
    hexagram: HexagramResponse
    yang_count: int
    upper_wuxing: str
    lower_wuxing: str
    wuxing_relation: str
    energy_level: float


class CycleAnalysisResponse(BaseModel):
    """周期分析响应"""
    start_year: int
    end_year: int
    level: str
    points: list[CyclePointResponse]
    turning_points: list[int]
    dominant_wuxing: str
    cycle_length: int


class TrendNodeResponse(BaseModel):
    """趋势节点"""
    year: int
    hexagram: HexagramResponse
    level: str
    event_type: str
    description: str
    energy: float
    significance: int


class TrendReportResponse(BaseModel):
    """趋势报告响应"""
    base_year: int
    target_years: int
    current_chain: HexagramChainResponse
    nodes: list[TrendNodeResponse]
    overall_trend: str
    key_years: list[int]


class HistoryEventResponse(BaseModel):
    """历史事件响应"""
    year: int
    name: str
    event_type: str
    description: str
    significance: int
    hexagram_chain: Optional[HexagramChainResponse] = None


class SimilarPeriodResponse(BaseModel):
    """相似时期响应"""
    event: HistoryEventResponse
    similarity: float
    matches: list[str]
