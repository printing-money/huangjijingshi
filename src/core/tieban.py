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

# 14-1: 农历月份 → 数值（直接等于月份数）
MONTH_VALUES = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12,
}

# 14-2: 时支 → 数值
TIME_VALUES = {
    '子': 1, '丑': 2, '寅': 3, '卯': 4, '辰': 5, '巳': 6,
    '午': 7, '未': 8, '申': 9, '酉': 10, '戌': 11, '亥': 12,
}

# 14-4: 五音 → 数值
TONE_VALUES = {'宫': 5, '商': 4, '角': 3, '徵': 2, '羽': 1}

# 14-5: 日柱纳音五行 × 求测时干 → 日命数（来自 ref 14-5.csv）
DAY_LIFE_TABLE = {
    ('水', '甲'): 1, ('水', '乙'): 2, ('水', '丙'): 3, ('水', '丁'): 4, ('水', '戊'): 5,
    ('水', '己'): 1, ('水', '庚'): 2, ('水', '辛'): 3, ('水', '壬'): 4, ('水', '癸'): 5,
    ('火', '甲'): 2, ('火', '乙'): 3, ('火', '丙'): 4, ('火', '丁'): 5, ('火', '戊'): 1,
    ('火', '己'): 2, ('火', '庚'): 3, ('火', '辛'): 4, ('火', '壬'): 5, ('火', '癸'): 1,
    ('木', '甲'): 3, ('木', '乙'): 4, ('木', '丙'): 5, ('木', '丁'): 1, ('木', '戊'): 2,
    ('木', '己'): 3, ('木', '庚'): 4, ('木', '辛'): 5, ('木', '壬'): 1, ('木', '癸'): 2,
    ('金', '甲'): 4, ('金', '乙'): 5, ('金', '丙'): 1, ('金', '丁'): 2, ('金', '戊'): 3,
    ('金', '己'): 4, ('金', '庚'): 5, ('金', '辛'): 1, ('金', '壬'): 2, ('金', '癸'): 3,
    ('土', '甲'): 5, ('土', '乙'): 1, ('土', '丙'): 2, ('土', '丁'): 3, ('土', '戊'): 4,
    ('土', '己'): 5, ('土', '庚'): 1, ('土', '辛'): 2, ('土', '壬'): 3, ('土', '癸'): 4,
}

# 14-6: 求测时柱纳音五行 → 时运数
TIME_LUCK_TABLE = {'水': 1, '火': 2, '木': 3, '金': 4, '土': 5}

# 14-3: (先天命数, 年干组) → 五音（来自 ref 14-3.csv）
WUYIN_TABLE = {
    (1, '甲己'): '羽', (1, '乙庚'): '徵', (1, '丙辛'): '宫', (1, '丁壬'): '角', (1, '戊癸'): '商',
    (2, '甲己'): '羽', (2, '乙庚'): '徵', (2, '丙辛'): '宫', (2, '丁壬'): '角', (2, '戊癸'): '商',
    (3, '甲己'): '徵', (3, '乙庚'): '宫', (3, '丙辛'): '角', (3, '丁壬'): '商', (3, '戊癸'): '羽',
    (4, '甲己'): '徵', (4, '乙庚'): '宫', (4, '丙辛'): '角', (4, '丁壬'): '商', (4, '戊癸'): '羽',
    (5, '甲己'): '角', (5, '乙庚'): '商', (5, '丙辛'): '羽', (5, '丁壬'): '徵', (5, '戊癸'): '宫',
    (6, '甲己'): '角', (6, '乙庚'): '商', (6, '丙辛'): '羽', (6, '丁壬'): '徵', (6, '戊癸'): '宫',
    (7, '甲己'): '宫', (7, '乙庚'): '角', (7, '丙辛'): '商', (7, '丁壬'): '羽', (7, '戊癸'): '徵',
    (8, '甲己'): '宫', (8, '乙庚'): '角', (8, '丙辛'): '商', (8, '丁壬'): '羽', (8, '戊癸'): '徵',
    (9, '甲己'): '商', (9, '乙庚'): '羽', (9, '丙辛'): '徵', (9, '丁壬'): '宫', (9, '戊癸'): '角',
    (10, '甲己'): '商', (10, '乙庚'): '羽', (10, '丙辛'): '徵', (10, '丁壬'): '宫', (10, '戊癸'): '角',
    (11, '甲己'): '徵', (11, '乙庚'): '宫', (11, '丙辛'): '角', (11, '丁壬'): '商', (11, '戊癸'): '羽',
    (12, '甲己'): '徵', (12, '乙庚'): '宫', (12, '丙辛'): '角', (12, '丁壬'): '商', (12, '戊癸'): '羽',
}

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
                  is_leap: bool = False,
                  query_time_gz: str = '') -> TiebanResult:
        """
        铁板神数完整排盘

        Args:
            gender: '男' 或 '女'
            lunar_month: 农历月份 (1-12)
            lunar_day: 农历日 (1-30)
            year_gan/year_zhi: 年干支
            month_gz: 月柱干支
            day_gz: 日柱干支
            time_gz: 出生时柱干支
            is_leap: 是否闰月
            query_time_gz: 求测时间的时柱干支（不传则用出生时柱）
        """
        result = TiebanResult(
            gender=gender,
            birth_bazi={'year': year_gan + year_zhi, 'month': month_gz,
                        'day': day_gz, 'time': time_gz},
            lunar_month=lunar_month,
            lunar_day=lunar_day,
        )

        time_zhi = time_gz[1] if len(time_gz) >= 2 else '子'
        # 求测时间：用于计算日命数和时运数
        q_time_gz = query_time_gz if query_time_gz else time_gz
        q_time_gan = q_time_gz[0] if len(q_time_gz) >= 2 else '甲'
        q_time_zhi = q_time_gz[1] if len(q_time_gz) >= 2 else '子'

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

        # Step 2: 五音命数（查 14-3 表）
        gan_group = self._get_gan_group(year_gan)
        tone = WUYIN_TABLE.get((xiantian, gan_group), '宫')
        result.wuyin_num = TONE_VALUES.get(tone, 5)

        # Step 3: 日命数 & 时运数
        # 日命数 = 出生日柱纳音五行 × 求测时干
        day_nayin_wx = NAYIN_WUXING.get(day_gz, '土')
        result.day_life = DAY_LIFE_TABLE.get((day_nayin_wx, q_time_gan), 3)

        # 时运数 = 求测时柱纳音五行
        q_time_nayin_wx = NAYIN_WUXING.get(q_time_gz, '土')
        result.time_luck = TIME_LUCK_TABLE.get(q_time_nayin_wx, 3)

        # Step 4: 考刻（查 14-7 规则表）
        sum_val = result.day_life + result.time_luck
        is_yang = year_gan in '甲丙戊庚壬'
        if (gender == '男' and is_yang) or (gender == '女' and not is_yang):
            # 阳男阴女：sum>6→初刻，sum<=6→正刻
            result.moment = '初刻' if sum_val > 6 else '正刻'
        else:
            # 阴男阳女：sum>6→正刻，sum<=6→初刻
            result.moment = '正刻' if sum_val > 6 else '初刻'

        # Step 5: 本命数
        base_val = result.wuyin_num * 5 + result.day_life + result.time_luck
        if sum_val <= 6:
            fact = base_val - 1
        else:
            fact = base_val - 6
        result.benming_num = fact * 30 + lunar_day

        # Step 6: 十二辟卦（优先用14-9精确映射：刻别+本命数）
        from ..data.tieban_benming import get_hexagram_by_benming, get_benming_tiaowen, HEXAGRAM_DETAIL_MAP
        mapped_hex = HEXAGRAM_DETAIL_MAP.get((result.moment, result.benming_num), '')
        if not mapped_hex:
            mapped_hex = get_hexagram_by_benming(result.benming_num)
        if mapped_hex:
            result.hexagram = mapped_hex
        else:
            hex_idx = (result.benming_num - 1) % 12
            result.hexagram = TWELVE_HEXAGRAMS[hex_idx]

        # Step 7: 后天命数
        pn_sum = xiantian + result.benming_num
        result.houtian_num = pn_sum % 8
        if result.houtian_num == 0:
            result.houtian_num = 8

        # Step 7.5: 本命条文（一生总论）
        benming_nums = get_benming_tiaowen(result.hexagram, xiantian, result.moment)
        if benming_nums:
            parts = []
            for category, nums in benming_nums.items():
                label = {'xingge': '性格', 'caiqian': '才能前程', 'caiyun': '财运', 'xiongdi': '兄弟'}
                for num in nums:
                    tw = get_tiaowen(num)
                    if tw and tw.get('断词'):
                        parts.append(f"【{label.get(category, category)}】{tw['断词']}")
            result.benming_tiaowen = '\n'.join(parts)

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

            # Step 4: 条文编号（字母+岁数→基数+加数）+ 校正
            tiaowen_num = 0
            corrected_num = 0
            formula = ''
            if letter != '?' and (letter, age) in FORTUNE_TABLE:
                from ..data.tieban_benming import calculate_correction
                base, add, correction = FORTUNE_TABLE[(letter, age)]
                tiaowen_num = base + add
                formula = f'{base}+{add}={tiaowen_num}'

                # 校正：根据年龄段调整校正数，查校正后条文
                corrected_correction = calculate_correction(correction, age)
                if corrected_correction > 0:
                    # 在 FORTUNE_TABLE 中查找校正后的条文
                    for (lt, ag), (b, a, c) in FORTUNE_TABLE.items():
                        if c == corrected_correction and ag == age:
                            corrected_num = b + a
                            break

            # Step 5: 查断词（优先用校正后的）
            final_num = corrected_num if corrected_num > 0 else tiaowen_num
            tiaowen = get_tiaowen(final_num) if final_num > 0 else {}

            liunian.append({
                'age': age,
                'ganzhi': cur_gz,
                'sound': sound,
                'marker': marker,
                'letter': letter,
                'tiaowen_num': final_num,
                'formula': formula,
                'duanyu': tiaowen.get('断词', ''),
                'duanyu_age': tiaowen.get('年龄', ''),
            })

        return liunian


# 全局引擎实例
tieban_engine = TiebanEngine()
