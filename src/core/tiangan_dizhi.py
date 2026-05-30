from __future__ import annotations
"""
天干地支计算与历法转换

支持：
- 六十甲子循环
- 公历 ↔ 皇极历转换
- 年月日时干支计算
- 节气计算（简化版）
"""

from dataclasses import dataclass
from typing import Optional
import math

# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行
WUXING = ['木', '火', '土', '金', '水']

# 天干五行对应
TIANGAN_WUXING = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]  # 甲乙木、丙丁火、戊己土、庚辛金、壬癸水

# 地支五行对应
DIZHI_WUXING = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]  # 子水、丑土、寅卯木...


@dataclass(frozen=True)
class GanZhi:
    """干支"""
    gan_index: int   # 天干索引 0-9
    zhi_index: int   # 地支索引 0-11

    @property
    def gan(self) -> str:
        return TIANGAN[self.gan_index]

    @property
    def zhi(self) -> str:
        return DIZHI[self.zhi_index]

    @property
    def name(self) -> str:
        return f"{self.gan}{self.zhi}"

    @property
    def index_60(self) -> int:
        """六十甲子中的索引（0-59）"""
        # 天干和地支同奇同偶才合法
        for i in range(60):
            if i % 10 == self.gan_index and i % 12 == self.zhi_index:
                return i
        return 0

    @property
    def gan_wuxing(self) -> str:
        """天干五行"""
        return WUXING[TIANGAN_WUXING[self.gan_index]]

    @property
    def zhi_wuxing(self) -> str:
        """地支五行"""
        return WUXING[DIZHI_WUXING[self.zhi_index]]

    def __repr__(self) -> str:
        return self.name


def index_to_ganzhi(index: int) -> GanZhi:
    """六十甲子索引转干支"""
    idx = index % 60
    return GanZhi(gan_index=idx % 10, zhi_index=idx % 12)


def ganzhi_from_name(name: str) -> Optional[GanZhi]:
    """从干支名称解析"""
    if len(name) < 2:
        return None
    gan_idx = TIANGAN.index(name[0]) if name[0] in TIANGAN else -1
    zhi_idx = DIZHI.index(name[1]) if name[1] in DIZHI else -1
    if gan_idx < 0 or zhi_idx < 0:
        return None
    return GanZhi(gan_index=gan_idx, zhi_index=zhi_idx)


# === 皇极历转换 ===

# 皇极历元年对应公历：皇极第1年 = 公元前 67016 年
# 即 gregorian_year = huangji_year - 67017
HUANGJI_EPOCH_OFFSET = 67017


def gregorian_to_huangji(year: int) -> int:
    """公历年转皇极年"""
    return year + HUANGJI_EPOCH_OFFSET


def huangji_to_gregorian(huangji_year: int) -> int:
    """皇极年转公历年"""
    return huangji_year - HUANGJI_EPOCH_OFFSET


@dataclass
class HuangjiCoordinate:
    """皇极时间坐标"""
    yuan: int = 1           # 元（固定为1，当前元）
    hui: int = 0            # 会（1-12）
    yun: int = 0            # 运（1-30，会内）
    global_yun: int = 0     # 全元运序（1-360）
    shi: int = 0            # 世（1-12，运内）
    global_shi: int = 0     # 全元世序（1-4320）
    sui: int = 0            # 岁（1-30，世内）
    huangji_year: int = 0   # 皇极年（1-129600）
    gregorian_year: int = 0 # 公历年


def year_to_coordinate(gregorian_year: int) -> HuangjiCoordinate:
    """
    公历年转皇极时间坐标

    基于 ref/saoyong/main.py 的算法：
    - 公元1744年 = 第192运第1年
    """
    if gregorian_year >= 0:
        y = gregorian_year
    else:
        y = gregorian_year + 1  # 没有公元0年

    # 计算全元运序
    if y >= 1744:
        global_yun = (y - 1744) // 360 + 192
    else:
        global_yun = (y - 1743) // 360 + 191

    if global_yun < 1 or global_yun > 360:
        # 超出本元范围，仍然计算但标记
        pass

    # 会序（1-12）
    hui = (global_yun - 1) // 30 + 1

    # 运在会内的序号（1-30）
    yun_in_hui = global_yun - (hui - 1) * 30

    # 年在运内的位置
    huangji_year = gregorian_to_huangji(gregorian_year)
    year_in_yun = y - ((global_yun - 192) * 360 + 1744)

    # 世（1-12）
    shi_in_yun = year_in_yun // 30 + 1

    # 年在世内（1-30）
    sui_in_shi = year_in_yun % 30 + 1

    # 全元世序
    global_shi = (global_yun - 1) * 12 + shi_in_yun

    return HuangjiCoordinate(
        yuan=1,
        hui=hui,
        yun=yun_in_hui,
        global_yun=global_yun,
        shi=shi_in_yun,
        global_shi=global_shi,
        sui=sui_in_shi,
        huangji_year=huangji_year,
        gregorian_year=gregorian_year,
    )


# === 年干支计算 ===

def year_ganzhi(gregorian_year: int) -> GanZhi:
    """
    计算年干支（以1984年甲子年为基准）

    注意：这里使用简化计算，不区分立春/冬至分年
    """
    offset = (gregorian_year - 1984) % 60
    if offset < 0:
        offset += 60
    return index_to_ganzhi(offset)


# === 日干支计算 ===

def day_ganzhi_index(year: int, month: int, day: int) -> int:
    """
    计算日干支索引（0-59）

    基准：2000年1月1日 = 戊午日（索引54）
    """
    from datetime import date
    base = date(2000, 1, 1)
    target = date(year, month, day)
    diff_days = (target - base).days
    idx = (54 + diff_days) % 60
    if idx < 0:
        idx += 60
    return idx


def day_ganzhi(year: int, month: int, day: int) -> GanZhi:
    """计算日干支"""
    return index_to_ganzhi(day_ganzhi_index(year, month, day))


# === 时辰计算 ===

def hour_to_shichen(hour: int) -> int:
    """
    小时转时辰地支索引（0-11）

    子时(23:00-00:59)=0, 丑时(01:00-02:59)=1, 寅时(03:00-04:59)=2,
    卯时(05:00-06:59)=3, 辰时(07:00-08:59)=4, 巳时(09:00-10:59)=5,
    午时(11:00-12:59)=6, 未时(13:00-14:59)=7, 申时(15:00-16:59)=8,
    酉时(17:00-18:59)=9, 戌时(19:00-20:59)=10, 亥时(21:00-22:59)=11
    """
    if hour >= 23 or hour == 0:
        return 0   # 子时
    return (hour + 1) // 2
