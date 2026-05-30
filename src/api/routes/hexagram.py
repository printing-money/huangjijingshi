from __future__ import annotations
"""
卦象推演 API 路由
"""

from fastapi import APIRouter, Query
from typing import Optional

from ..schemas import (
    HexagramResponse, HexagramChainResponse, CoordinateResponse, DateTimeRequest,
)
from ...core.hexagram import Hexagram, get_hexagram, get_hexagram_by_name
from ...core.huangji_algorithm import HuangjiEngine, HexagramChain
from ...core.tiangan_dizhi import (
    year_to_coordinate, hour_to_shichen, year_ganzhi, day_ganzhi,
)

router = APIRouter()
engine = HuangjiEngine()


def hexagram_to_response(h: Hexagram) -> HexagramResponse:
    """转换卦象为响应模型"""
    return HexagramResponse(
        binary=h.binary,
        name=h.name,
        unicode=h.unicode,
        upper=h.upper,
        lower=h.lower,
        yang_count=h.yang_count,
        yin_count=h.yin_count,
    )


def chain_to_response(chain: HexagramChain) -> HexagramChainResponse:
    """转换卦象链为响应模型"""
    coord = chain.coordinate
    coord_resp = CoordinateResponse(
        hui=coord.hui,
        yun=coord.yun,
        global_yun=coord.global_yun,
        shi=coord.shi,
        global_shi=coord.global_shi,
        sui=coord.sui,
        huangji_year=coord.huangji_year,
        gregorian_year=coord.gregorian_year,
    )

    resp = HexagramChainResponse(
        coordinate=coord_resp,
        yuan=hexagram_to_response(chain.yuan),
        hui=hexagram_to_response(chain.hui),
        yun=hexagram_to_response(chain.yun),
        shi=hexagram_to_response(chain.shi),
        ten_year=hexagram_to_response(chain.ten_year),
        sui=hexagram_to_response(chain.sui),
    )

    if chain.yue_jing:
        resp.yue_jing = hexagram_to_response(chain.yue_jing)
    if chain.xun_wei:
        resp.xun_wei = hexagram_to_response(chain.xun_wei)
    if chain.ri:
        resp.ri = hexagram_to_response(chain.ri)
    if chain.shi_jing:
        resp.shi_jing = hexagram_to_response(chain.shi_jing)

    return resp


@router.get("/chain/{year}", response_model=HexagramChainResponse)
def get_hexagram_chain(year: int):
    """获取指定年份的完整九层卦象链"""
    chain = engine.compute_chain(year)
    return chain_to_response(chain)


@router.post("/datetime", response_model=HexagramChainResponse)
def get_hexagram_by_datetime(req: DateTimeRequest):
    """获取精确到时辰的卦象信息"""
    day_of_year = None
    shichen = None

    if req.month and req.day:
        # 简化计算皇极年内天数（每月30天）
        day_of_year = (req.month - 1) * 30 + req.day
        day_of_year = max(1, min(day_of_year, 360))

    if req.hour is not None:
        shichen = hour_to_shichen(req.hour)

    chain = engine.compute_chain(req.year, day_of_year, shichen)
    return chain_to_response(chain)


@router.get("/sui/{year}", response_model=HexagramResponse)
def get_sui_hexagram(year: int):
    """获取指定年份的岁卦"""
    h = engine.get_sui_hexagram(year)
    return hexagram_to_response(h)


@router.get("/timeline/{start}/{end}")
def get_timeline(start: int, end: int, step: int = Query(default=1, ge=1, le=100)):
    """获取时间段内的岁卦变化序列"""
    results = []
    for year in range(start, end + 1, step):
        h = engine.get_sui_hexagram(year)
        gz = year_ganzhi(year)
        results.append({
            'year': year,
            'ganzhi': gz.name,
            'hexagram': hexagram_to_response(h).model_dump(),
        })
    return {'start': start, 'end': end, 'step': step, 'data': results}


@router.get("/search/{name}")
def search_hexagram(name: str):
    """按卦名搜索卦象信息"""
    h = get_hexagram_by_name(name)
    if h is None:
        return {'error': f'未找到卦象: {name}'}
    return hexagram_to_response(h)
