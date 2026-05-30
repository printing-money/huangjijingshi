"""
铁板神数 API 路由

用户只需输入公历出生时间，系统自动完成：
公历 → 农历 → 八字 → 铁板排盘 → 条文查询
"""

from __future__ import annotations

import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from ...core.tieban import tieban_engine

router = APIRouter()


def convert_to_bazi(dt_obj: datetime.datetime) -> dict:
    """公历时间 → 农历 + 八字（自动转换）"""
    import cnlunar
    a = cnlunar.Lunar(dt_obj, godType='8char')
    try:
        lm, ld = int(a.lunarMonth), int(a.lunarDay)
    except (ValueError, TypeError):
        lm, ld = 1, 1
    return {
        'lunar_month': lm,
        'lunar_day': ld,
        'is_leap': '闰' in a.lunarMonthCn,
        'year_gz': a.year8Char,
        'month_gz': a.month8Char,
        'day_gz': a.day8Char,
        'time_gz': a.twohour8Char,
        'lunar_str': f"{a.lunarYearCn}年 {a.lunarMonthCn}{a.lunarDayCn}",
    }


class TiebanRequest(BaseModel):
    """铁板神数请求 — 只需公历时间"""
    gender: str = Field(default='男', description="性别：男/女")
    birth_time: str = Field(default='', description="出生时间 YYYY-MM-DD HH:MM，留空用当前时间")
    father_zodiac: Optional[str] = Field(None, description="父亲属相")
    mother_zodiac: Optional[str] = Field(None, description="母亲属相")
    sibling_count: Optional[int] = Field(None, description="兄弟姐妹数")
    sibling_rank: Optional[int] = Field(None, description="排行")


@router.post("/paipan")
def tieban_paipan(req: TiebanRequest):
    """
    铁板神数排盘

    只需输入性别和公历出生时间，系统自动完成农历/八字转换。
    出生时间留空则默认使用当前时间。
    """
    # 解析时间
    if req.birth_time:
        try:
            dt = datetime.datetime.strptime(req.birth_time, '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                dt = datetime.datetime.strptime(req.birth_time, '%Y-%m-%d')
                dt = dt.replace(hour=12)  # 默认正午
            except ValueError:
                return {'error': '时间格式错误，请使用 YYYY-MM-DD HH:MM'}
    else:
        dt = datetime.datetime.now()

    # 自动转换
    bazi_info = convert_to_bazi(dt)
    year_gz = bazi_info['year_gz']

    # 排盘
    result = tieban_engine.calculate(
        gender=req.gender,
        lunar_month=bazi_info['lunar_month'],
        lunar_day=bazi_info['lunar_day'],
        year_gan=year_gz[0],
        year_zhi=year_gz[1],
        month_gz=bazi_info['month_gz'],
        day_gz=bazi_info['day_gz'],
        time_gz=bazi_info['time_gz'],
        is_leap=bazi_info['is_leap'],
    )

    return {
        'input': {
            'gender': req.gender,
            'birth_time': dt.strftime('%Y-%m-%d %H:%M'),
            'lunar': bazi_info['lunar_str'],
            'bazi': f"{bazi_info['year_gz']} {bazi_info['month_gz']} {bazi_info['day_gz']} {bazi_info['time_gz']}",
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
        'liunian': result.liunian,
        'liunian_count': len(result.liunian),
    }


@router.post("/liunian")
def tieban_liunian(req: TiebanRequest, start_age: int = 1, end_age: int = 100):
    """获取完整流年条文"""
    if req.birth_time:
        try:
            dt = datetime.datetime.strptime(req.birth_time, '%Y-%m-%d %H:%M')
        except ValueError:
            dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.now()

    bazi_info = convert_to_bazi(dt)
    year_gz = bazi_info['year_gz']

    result = tieban_engine.calculate(
        gender=req.gender,
        lunar_month=bazi_info['lunar_month'],
        lunar_day=bazi_info['lunar_day'],
        year_gan=year_gz[0],
        year_zhi=year_gz[1],
        month_gz=bazi_info['month_gz'],
        day_gz=bazi_info['day_gz'],
        time_gz=bazi_info['time_gz'],
        is_leap=bazi_info['is_leap'],
    )

    filtered = [l for l in result.liunian if start_age <= l['age'] <= end_age]
    return {
        'hexagram': result.hexagram,
        'benming_num': result.benming_num,
        'liunian': filtered,
    }
