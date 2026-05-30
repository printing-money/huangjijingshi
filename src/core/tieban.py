"""
铁板神数计算引擎

移植自 ref/tiebanshenshu，核心算法：
1. 先天命数 = 农历月份 + 3 - 时支数
2. 五音命数 = 查表(先天命数, 年干组)
3. 日命数 & 时运数 = 查表(日柱纳音, 时柱纳音)
4. 考刻 = 根据阴阳男女判断初刻/正刻
5. 本命数 = (五音×5 + 日命 + 时运 - 偏移) × 30 + 农历日
6. 十二辟卦 = 查表(刻别, 本命数)
7. 流年条文 = 按干支循环查表得到条文编号 → 查断词库
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .tiangan_dizhi import (
    TIANGAN, DIZHI, GanZhi, index_to_ganzhi, year_ganzhi,
    hour_to_shichen,
)
from ..data.ganzhi_relations import NAYIN, GAN_WUXING
from ..data.tieban_tiaowen import get_tiaowen, get_ji_name


# === 铁板神数静态常量 ===

# 纳音五行（从纳音名称提取五行属性）
NAYIN_WUXING = {}
for _gz, _nay in NAYIN.items():
    if '金' in _nay: NAYIN_WUXING[_gz] = '金'
    elif '木' in _nay: NAYIN_WUXING[_gz] = '木'
    elif '水' in _nay: NAYIN_WUXING[_gz] = '水'
    elif '火' in _nay: NAYIN_WUXING[_gz] = '火'
    elif '土' in _nay: NAYIN_WUXING[_gz] = '土'

# 14-1: 农历月份 → 数值
MONTH_VALUES = {
    '1': 4, '2': 5, '3': 6, '4': 7, '5': 8, '6': 9,
    '7': 10, '8': 11, '9': 12, '10': 1, '11': 2, '12': 3,
}

# 14-2: 时支 → 数值
TIME_VALUES = {
    '子': 1, '丑': 2, '寅': 3, '卯': 4, '辰': 5, '巳': 6,
    '午': 7, '未': 8, '申': 9, '酉': 10, '戌': 11, '亥': 12,
}

# 14-4: 五音 → 数值
TONE_VALUES = {'宫': 5, '商': 4, '角': 3, '徵': 2, '羽': 1}

# 14-5: 日柱纳音五行 × 时干 → 日命数（简化）
DAY_LIFE_TABLE = {
    ('金', '甲'): 4, ('金', '乙'): 3, ('金', '丙'): 2, ('金', '丁'): 1, ('金', '戊'): 5,
    ('金', '己'): 4, ('金', '庚'): 3, ('金', '辛'): 2, ('金', '壬'): 1, ('金', '癸'): 5,
    ('木', '甲'): 3, ('木', '乙'): 2, ('木', '丙'): 1, ('木', '丁'): 5, ('木', '戊'): 4,
    ('木', '己'): 3, ('木', '庚'): 2, ('木', '辛'): 1, ('木', '壬'): 5, ('木', '癸'): 4,
    ('水', '甲'): 1, ('水', '乙'): 5, ('水', '丙'): 4, ('水', '丁'): 3, ('水', '戊'): 2,
    ('水', '己'): 1, ('水', '庚'): 5, ('水', '辛'): 4, ('水', '壬'): 3, ('水', '癸'): 2,
    ('火', '甲'): 2, ('火', '乙'): 1, ('火', '丙'): 5, ('火', '丁'): 4, ('火', '戊'): 3,
    ('火', '己'): 2, ('火', '庚'): 1, ('火', '辛'): 5, ('火', '壬'): 4, ('火', '癸'): 3,
    ('土', '甲'): 5, ('土', '乙'): 4, ('土', '丙'): 3, ('土', '丁'): 2, ('土', '戊'): 1,
    ('土', '己'): 5, ('土', '庚'): 4, ('土', '辛'): 3, ('土', '壬'): 2, ('土', '癸'): 1,
}

# 14-6: 时柱纳音五行 → 时运数
TIME_LUCK_TABLE = {'金': 4, '木': 3, '水': 1, '火': 2, '土': 5}

# 十二辟卦名
TWELVE_HEXAGRAMS = ['复', '临', '泰', '大壮', '夬', '乾', '姤', '遁', '否', '观', '剥', '坤']


@dataclass
class TiebanResult:
    """铁板神数排盘结果"""
    # 基础信息
    gender: str
    birth_bazi: dict
    lunar_month: int
    lunar_day: int

    # 计算结果
    xiantian_num: int = 0        # 先天命数
    wuyin_num: int = 0           # 五音命数
    day_life: int = 0            # 日命数
    time_luck: int = 0           # 时运数
    moment: str = ''             # 考刻（初刻/正刻）
    benming_num: int = 0         # 本命数
    hexagram: str = ''           # 十二辟卦
    houtian_num: int = 0         # 后天命数

    # 流年条文
    liunian: list = field(default_factory=list)

    # 本命条文
    benming_tiaowen: str = ''


class TiebanEngine:
    """铁板神数计算引擎"""

    def calculate(self, gender: str, lunar_month: int, lunar_day: int,
                  year_gan: str, year_zhi: str,
                  month_gz: str, day_gz: str, time_gz: str,
                  is_leap: bool = False) -> TiebanResult:
        """
        铁板神数完整排盘

        Args:
            gender: '男' 或 '女'
            lunar_month: 农历月份 (1-12)
            lunar_day: 农历日 (1-30)
            year_gan/year_zhi: 年干支
            month_gz: 月柱干支
            day_gz: 日柱干支
            time_gz: 时柱干支
            is_leap: 是否闰月
        """
        result = TiebanResult(
            gender=gender,
            birth_bazi={'year': year_gan + year_zhi, 'month': month_gz,
                        'day': day_gz, 'time': time_gz},
            lunar_month=lunar_month,
            lunar_day=lunar_day,
        )

        time_zhi = time_gz[1] if len(time_gz) >= 2 else '子'
        time_gan = time_gz[0] if len(time_gz) >= 2 else '甲'

        # Step 1: 先天命数
        calc_month = lunar_month + (1 if is_leap else 0)
        if calc_month > 12:
            calc_month = 1
        month_val = MONTH_VALUES.get(str(calc_month), calc_month)
        time_val = TIME_VALUES.get(time_zhi, 1)
        xiantian = month_val + 3 - time_val
        if xiantian <= 0:
            xiantian += 12
        result.xiantian_num = xiantian

        # Step 2: 五音命数
        gan_group = self._get_gan_group(year_gan)
        # 简化：五音按先天命数取模
        tone_idx = (xiantian - 1) % 5
        tone_names = ['宫', '商', '角', '徵', '羽']
        tone = tone_names[tone_idx]
        result.wuyin_num = TONE_VALUES.get(tone, 5)

        # Step 3: 日命数 & 时运数
        day_nayin_wx = NAYIN_WUXING.get(day_gz, '土')
        result.day_life = DAY_LIFE_TABLE.get((day_nayin_wx, time_gan), 3)

        time_nayin_wx = NAYIN_WUXING.get(time_gz, '土')
        result.time_luck = TIME_LUCK_TABLE.get(time_nayin_wx, 3)

        # Step 4: 考刻
        sum_val = result.day_life + result.time_luck
        is_yang = year_gan in '甲丙戊庚壬'
        if (gender == '男' and is_yang) or (gender == '女' and not is_yang):
            # 阳男阴女
            result.moment = '初刻' if sum_val <= 6 else '正刻'
        else:
            # 阴男阳女
            result.moment = '正刻' if sum_val <= 6 else '初刻'

        # Step 5: 本命数
        base_val = result.wuyin_num * 5 + result.day_life + result.time_luck
        if sum_val <= 6:
            fact = base_val - 1
        else:
            fact = base_val - 6
        result.benming_num = fact * 30 + lunar_day

        # Step 6: 十二辟卦
        hex_idx = (result.benming_num - 1) % 12
        result.hexagram = TWELVE_HEXAGRAMS[hex_idx]

        # Step 7: 后天命数
        pn_sum = xiantian + result.benming_num
        result.houtian_num = pn_sum % 8
        if result.houtian_num == 0:
            result.houtian_num = 8

        # Step 8: 流年条文（1-100岁）
        result.liunian = self._calc_liunian(
            year_gan, year_zhi, xiantian, result.houtian_num,
            moment=result.moment,
            sum_val=result.day_life + result.time_luck,
            gender=gender,
        )

        return result

    def _get_gan_group(self, gan: str) -> str:
        """天干五合分组"""
        groups = ['甲己', '乙庚', '丙辛', '丁壬', '戊癸']
        idx = TIANGAN.index(gan) if gan in TIANGAN else 0
        return groups[idx % 5]

    def _calc_liunian(self, year_gan: str, year_zhi: str,
                      xiantian: int, houtian: int,
                      moment: str = '初刻', sum_val: int = 5,
                      gender: str = '男') -> list:
        """
        计算流年条文（正确的查表逻辑）

        流程：
        1. 四声 = 查 LIUNIAN_SEQ（先天命数+天干→12四声序列）
        2. 标记 = 查 MARKER_TABLE（流年地支+后天命数→标记）
        3. 字母 = 查 LETTER_TABLE（考刻+奇偶+四声+标记→字母）
        4. 条文号 = 查 FORTUNE_TABLE（字母+岁数→基数+加数）
        5. 断词 = 查条文库
        """
        from ..data.tieban_tables import (
            LIUNIAN_START, LIUNIAN_SEQ, MARKER_TABLE, LETTER_TABLE, FORTUNE_TABLE,
        )

        liunian = []
        st_tg = TIANGAN.index(year_gan)
        st_dz = DIZHI.index(year_zhi)

        # Step 1: 确定四声序列
        # 查起始数
        if year_zhi in '寅午戌':
            zhi_group = '寅午戌'
        elif year_zhi in '申子辰':
            zhi_group = '申子辰'
        elif year_zhi in '巳酉丑':
            zhi_group = '巳酉丑'
        else:
            zhi_group = '亥卯未'

        start = LIUNIAN_START.get((zhi_group, gender), 1)

        # 查四声原始序列
        raw_seq = LIUNIAN_SEQ.get((xiantian, year_gan), [])
        if not raw_seq:
            # fallback: 尝试用天干组
            for gan in TIANGAN:
                raw_seq = LIUNIAN_SEQ.get((xiantian, gan), [])
                if raw_seq:
                    break

        # 按起始数偏移
        final_seq = ['?'] * 12
        if raw_seq and len(raw_seq) >= 12:
            off = (13 - start) % 12
            final_seq = [raw_seq[(i + off) % 12] for i in range(12)]

        # 奇偶性
        parity = '奇数' if sum_val % 2 != 0 else '偶数'

        for age in range(1, 101):
            cur_tg = TIANGAN[(st_tg + age - 1) % 10]
            cur_dz = DIZHI[(st_dz + age - 1) % 12]
            cur_gz = cur_tg + cur_dz

            # Step 1: 四声（按12循环）
            sound = final_seq[(age - 1) % 12] if final_seq[0] != '?' else '?'

            # Step 2: 标记（地支+后天命数）
            marker = MARKER_TABLE.get((cur_dz, houtian), '?')

            # Step 3: 字母（考刻+奇偶+四声+标记）
            age_parity = '奇数' if age % 2 != 0 else '偶数'
            letter = LETTER_TABLE.get((moment, age_parity, sound, marker), '?')

            # Step 4: 条文编号（字母+岁数→基数+加数）
            tiaowen_num = 0
            formula = ''
            if letter != '?' and (letter, age) in FORTUNE_TABLE:
                base, add, correction = FORTUNE_TABLE[(letter, age)]
                tiaowen_num = base + add
                formula = f'{base}+{add}={tiaowen_num}'

            # Step 5: 查断词
            tiaowen = get_tiaowen(tiaowen_num) if tiaowen_num > 0 else {}

            liunian.append({
                'age': age,
                'ganzhi': cur_gz,
                'sound': sound,
                'marker': marker,
                'letter': letter,
                'tiaowen_num': tiaowen_num,
                'formula': formula,
                'duanyu': tiaowen.get('断词', ''),
                'duanyu_age': tiaowen.get('年龄', ''),
            })

        return liunian


# 全局引擎实例
tieban_engine = TiebanEngine()
