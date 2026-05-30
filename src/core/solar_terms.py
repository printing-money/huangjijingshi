"""
节气精确计算

基于寿星天文历算法，计算21世纪任意年份的24节气精确日期。
数据来源：ref/react-yhys/src/utils/solarTerms.ts
"""

from __future__ import annotations

import math
from datetime import date, datetime


# 24节气名称（从小寒开始）
SOLAR_TERM_NAMES = [
    '小寒', '大寒', '立春', '雨水', '惊蛰', '春分',
    '清明', '谷雨', '立夏', '小满', '芒种', '夏至',
    '小暑', '大暑', '立秋', '处暑', '白露', '秋分',
    '寒露', '霜降', '立冬', '小雪', '大雪', '冬至',
]

# 21世纪节气C值常数
C_VALUES_21 = [
    5.4055, 20.12, 3.87, 18.73, 5.63, 20.646,   # 小寒-春分
    4.81, 20.1, 5.52, 21.04, 5.678, 21.37,       # 清明-夏至
    7.108, 22.83, 7.5, 23.13, 7.646, 23.042,     # 小暑-秋分
    8.318, 23.438, 7.438, 22.36, 7.18, 21.94,    # 寒露-冬至
]

# 20世纪节气C值常数
C_VALUES_20 = [
    6.11, 20.84, 4.15, 19.04, 6.34, 20.93,
    5.59, 20.53, 5.52, 21.34, 5.678, 21.37,
    7.108, 23.13, 7.5, 23.13, 8.44, 23.822,
    8.318, 23.438, 8.438, 22.36, 7.18, 21.94,
]


def get_term_day(year: int, term_index: int) -> int:
    """
    计算指定年份第n个节气的日期（日）

    Args:
        year: 公历年份
        term_index: 节气索引（0=小寒, 1=大寒, ..., 23=冬至）

    Returns:
        该节气在对应月份中的日期（1-31）
    """
    if year >= 2000:
        c = C_VALUES_21[term_index]
    else:
        c = C_VALUES_20[term_index]

    y = year % 100
    d = 0.2422
    l = int(y / 4)

    # 通用公式
    day = int(y * d + c) - l

    return day


def get_term_date(year: int, term_index: int) -> date:
    """
    获取节气的完整日期

    Args:
        year: 公历年份
        term_index: 节气索引（0-23）

    Returns:
        date 对象
    """
    # 节气对应的月份：小寒大寒在1月，立春雨水在2月...
    month = (term_index // 2) + 1
    day = get_term_day(year, term_index)

    # 冬至特殊处理（在12月）
    if term_index >= 22:
        month = 12
    elif term_index >= 20:
        month = 11
    elif term_index >= 18:
        month = 10

    try:
        return date(year, month, day)
    except ValueError:
        # 日期溢出时取月末
        return date(year, month, min(day, 28))


def get_all_terms(year: int) -> list:
    """
    获取指定年份所有24节气的日期

    Returns:
        [(节气名, date), ...]
    """
    terms = []
    for i in range(24):
        d = get_term_date(year, i)
        terms.append((SOLAR_TERM_NAMES[i], d))
    return terms


def get_current_term(dt: datetime) -> dict:
    """
    获取指定日期所处的节气区间

    Returns:
        {'current': 当前节气名, 'date': 节气日期, 'next': 下一个节气名, 'next_date': 下一节气日期}
    """
    year = dt.year
    today = dt.date() if isinstance(dt, datetime) else dt

    terms = get_all_terms(year)
    # 加上下一年的小寒
    terms.append((SOLAR_TERM_NAMES[0], get_term_date(year + 1, 0)))

    current_term = terms[0]
    next_term = terms[1]

    for i in range(len(terms) - 1):
        if terms[i][1] <= today < terms[i + 1][1]:
            current_term = terms[i]
            next_term = terms[i + 1]
            break

    return {
        'current': current_term[0],
        'date': current_term[1],
        'next': next_term[0],
        'next_date': next_term[1],
        'days_to_next': (next_term[1] - today).days,
    }
