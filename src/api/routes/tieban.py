"""
铁板神数 API 路由
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ...core.tieban import tieban_engine, TiebanResult

router = APIRouter()


class TiebanRequest(BaseModel):
    """铁板神数排盘请求"""
    gender: str                          # 男/女
    lunar_month: int                     # 农历月 1-12
    lunar_day: int                       # 农历日 1-30
    year_gan: str                        # 年干
    year_zhi: str                        # 年支
    month_gz: str                        # 月柱干支
    day_gz: str                          # 日柱干支
    time_gz: str                         # 时柱干支
    is_leap: bool = False                # 是否闰月
    # 铁板神数考刻用
    father_zodiac: Optional[str] = None  # 父亲属相
    mother_zodiac: Optional[str] = None  # 母亲属相
    sibling_count: Optional[int] = None  # 兄弟姐妹数
    sibling_rank: Optional[int] = None   # 排行


@router.post("/paipan")
def tieban_paipan(req: TiebanRequest):
    """铁板神数排盘"""
    result = tieban_engine.calculate(
        gender=req.gender,
        lunar_month=req.lunar_month,
        lunar_day=req.lunar_day,
        year_gan=req.year_gan,
        year_zhi=req.year_zhi,
        month_gz=req.month_gz,
        day_gz=req.day_gz,
        time_gz=req.time_gz,
        is_leap=req.is_leap,
    )

    return {
        'basic': {
            'gender': result.gender,
            'bazi': result.birth_bazi,
            'lunar': f"农历{result.lunar_month}月{result.lunar_day}日",
        },
        'calculation': {
            'xiantian_num': result.xiantian_num,
            'wuyin_num': result.wuyin_num,
            'day_life': result.day_life,
            'time_luck': result.time_luck,
            'moment': result.moment,
            'benming_num': result.benming_num,
            'hexagram': result.hexagram,
            'houtian_num': result.houtian_num,
        },
        'liunian': result.liunian[:20],  # 前20年预览
        'liunian_count': len(result.liunian),
    }


@router.post("/liunian")
def tieban_liunian(req: TiebanRequest, start_age: int = 1, end_age: int = 100):
    """获取完整流年条文"""
    result = tieban_engine.calculate(
        gender=req.gender,
        lunar_month=req.lunar_month,
        lunar_day=req.lunar_day,
        year_gan=req.year_gan,
        year_zhi=req.year_zhi,
        month_gz=req.month_gz,
        day_gz=req.day_gz,
        time_gz=req.time_gz,
        is_leap=req.is_leap,
    )

    filtered = [l for l in result.liunian if start_age <= l['age'] <= end_age]
    return {
        'hexagram': result.hexagram,
        'benming_num': result.benming_num,
        'liunian': filtered,
    }
