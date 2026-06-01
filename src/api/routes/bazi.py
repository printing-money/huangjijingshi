"""
八字排盘 API 路由
"""

from __future__ import annotations

import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from ...core.bazi import bazi_engine

router = APIRouter()


def convert_to_bazi(dt_obj):
    """公历→八字"""
    import cnlunar
    a = cnlunar.Lunar(dt_obj, godType='8char')
    return {
        'year_gz': a.year8Char,
        'month_gz': a.month8Char,
        'day_gz': a.day8Char,
        'time_gz': a.twohour8Char,
        'lunar_str': f"{a.lunarYearCn}年 {a.lunarMonthCn}{a.lunarDayCn}",
    }


class BaziRequest(BaseModel):
    gender: str = Field(default='男', description="性别：男/女")
    birth_time: str = Field(default='', description="出生时间 YYYY-MM-DD HH:MM")


@router.post("/paipan")
def bazi_paipan(req: BaziRequest):
    """八字排盘"""
    if req.birth_time:
        try:
            dt = datetime.datetime.strptime(req.birth_time, '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                dt = datetime.datetime.strptime(req.birth_time, '%Y-%m-%d')
                dt = dt.replace(hour=12)
            except ValueError:
                return {'error': '时间格式错误，请使用 YYYY-MM-DD HH:MM'}
    else:
        dt = datetime.datetime.now()

    bazi_info = convert_to_bazi(dt)

    result = bazi_engine.calculate(
        gender=req.gender,
        year_gz=bazi_info['year_gz'],
        month_gz=bazi_info['month_gz'],
        day_gz=bazi_info['day_gz'],
        time_gz=bazi_info['time_gz'],
        lunar_str=bazi_info['lunar_str'],
        gregorian_str=dt.strftime('%Y-%m-%d %H:%M'),
        birth_dt=dt,
    )

    return {
        'input': {
            'gender': req.gender,
            'birth_time': dt.strftime('%Y-%m-%d %H:%M'),
            'lunar': result.lunar_str,
            'bazi': f"{result.year_gz} {result.month_gz} {result.day_gz} {result.time_gz}",
        },
        'day_master': {
            'gan': result.day_master,
            'wuxing': result.day_master_wuxing,
            'is_strong': result.is_strong,
            'strength': '身强' if result.is_strong else '身弱',
        },
        'shishen': result.shishen,
        'wuxing_score': result.wuxing_score,
        'nayin': result.nayin,
        'relations': result.relations,
        'dayun': result.dayun,
        'shenshas': result.shenshas,
        'geju': result.geju,
        'rizhu_duanyu': result.rizhu_duanyu,
        'canggan_detail': result.canggan_detail,
        'changsheng_detail': result.changsheng_detail,
        'kongwang': result.kongwang,
        'liuqin': result.liuqin,
        'xingge': result.xingge,
    }
