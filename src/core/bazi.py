"""
八字排盘引擎

基于四柱八字体系，提供完整的命理分析：
- 四柱排盘（年月日时）
- 十神关系
- 五行分数与强弱判断
- 大运排列
- 神煞标注
- 格局分析

数据来源：ref/bazi + src/data/ganzhi_relations.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..data.ganzhi_relations import (
    NAYIN, SHISHEN, CHANGSHENG, ZHI_CANGGAN,
    GAN_HE, GAN_CHONG, ZHI_CHONG, ZHI_LIUHE, ZHI_XING, ZHI_HAI,
    GAN_WUXING, ZHI_WUXING, WUXING_SHENG, WUXING_KE,
    RIZHU_DUANYU,
)

TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


@dataclass
class BaziResult:
    """八字排盘结果"""
    # 四柱
    year_gz: str = ''
    month_gz: str = ''
    day_gz: str = ''
    time_gz: str = ''

    # 基础信息
    gender: str = '男'
    lunar_str: str = ''
    gregorian_str: str = ''

    # 十神
    shishen: dict = field(default_factory=dict)  # {柱: 十神}

    # 五行
    wuxing_score: dict = field(default_factory=dict)  # {金木水火土: 分数}
    day_master: str = ''  # 日主
    day_master_wuxing: str = ''
    is_strong: bool = False  # 身强/身弱

    # 纳音
    nayin: dict = field(default_factory=dict)  # {柱: 纳音}

    # 关系
    relations: list = field(default_factory=list)  # 冲合刑害列表

    # 大运
    dayun: list = field(default_factory=list)

    # 神煞
    shenshas: list = field(default_factory=list)

    # 格局
    geju: str = ''

    # 日柱断语
    rizhu_duanyu: str = ''


class BaziEngine:
    """八字排盘引擎"""

    def calculate(self, gender: str, year_gz: str, month_gz: str,
                  day_gz: str, time_gz: str, lunar_str: str = '',
                  gregorian_str: str = '') -> BaziResult:
        """完整八字排盘"""
        result = BaziResult(
            gender=gender,
            year_gz=year_gz, month_gz=month_gz,
            day_gz=day_gz, time_gz=time_gz,
            lunar_str=lunar_str, gregorian_str=gregorian_str,
        )

        # 日主
        result.day_master = day_gz[0]
        result.day_master_wuxing = GAN_WUXING.get(day_gz[0], '土')

        # 十神
        result.shishen = self._calc_shishen(day_gz[0], year_gz, month_gz, day_gz, time_gz)

        # 五行分数
        result.wuxing_score = self._calc_wuxing_score(year_gz, month_gz, day_gz, time_gz)

        # 强弱判断
        my_wx = result.day_master_wuxing
        sheng_wx = [k for k, v in WUXING_SHENG.items() if v == my_wx][0]  # 生我的
        my_score = result.wuxing_score.get(my_wx, 0) + result.wuxing_score.get(sheng_wx, 0)
        total = sum(result.wuxing_score.values())
        result.is_strong = my_score > total / 2

        # 纳音
        result.nayin = {
            '年': NAYIN.get(year_gz, ''),
            '月': NAYIN.get(month_gz, ''),
            '日': NAYIN.get(day_gz, ''),
            '时': NAYIN.get(time_gz, ''),
        }

        # 关系（冲合刑害）
        result.relations = self._calc_relations(year_gz, month_gz, day_gz, time_gz)

        # 大运
        result.dayun = self._calc_dayun(gender, year_gz, month_gz)

        # 神煞
        result.shenshas = self._calc_shenshas(day_gz[0], year_gz, month_gz, day_gz, time_gz)

        # 日柱断语
        result.rizhu_duanyu = RIZHU_DUANYU.get(day_gz, '')

        # 格局
        result.geju = self._calc_geju(result)

        return result

    def _calc_shishen(self, ri_gan: str, year_gz: str, month_gz: str,
                      day_gz: str, time_gz: str) -> dict:
        """计算四柱十神"""
        ss_map = SHISHEN.get(ri_gan, {})
        result = {}
        pillars = [('年干', year_gz[0]), ('年支', year_gz[1]),
                   ('月干', month_gz[0]), ('月支', month_gz[1]),
                   ('日支', day_gz[1]),
                   ('时干', time_gz[0]), ('时支', time_gz[1])]

        for label, char in pillars:
            if char in ss_map:
                result[label] = ss_map[char]
            elif char in ZHI_CANGGAN:
                # 地支取本气（藏干第一个）
                main_gan = ZHI_CANGGAN[char][0]
                result[label] = ss_map.get(main_gan, '')

        return result

    def _calc_wuxing_score(self, year_gz: str, month_gz: str,
                           day_gz: str, time_gz: str) -> dict:
        """计算五行分数"""
        score = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}

        # 天干各1分
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            gan_wx = GAN_WUXING.get(gz[0], '土')
            score[gan_wx] += 1

        # 地支藏干按权重
        zhi_weights = {0: 5, 1: 2, 2: 1}  # 本气/中气/余气
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            zhi = gz[1]
            canggan = ZHI_CANGGAN.get(zhi, [])
            for i, gan in enumerate(canggan):
                wx = GAN_WUXING.get(gan, '土')
                weight = zhi_weights.get(i, 1)
                score[wx] += weight

        return score

    def _calc_relations(self, year_gz: str, month_gz: str,
                        day_gz: str, time_gz: str) -> list:
        """计算冲合刑害关系"""
        relations = []
        zhis = [('年支', year_gz[1]), ('月支', month_gz[1]),
                ('日支', day_gz[1]), ('时支', time_gz[1])]
        gans = [('年干', year_gz[0]), ('月干', month_gz[0]),
                ('日干', day_gz[0]), ('时干', time_gz[0])]

        # 天干合
        for i in range(len(gans)):
            for j in range(i + 1, len(gans)):
                key = (gans[i][1], gans[j][1])
                if key in GAN_HE:
                    relations.append(f'{gans[i][0]}{gans[i][1]}合{gans[j][0]}{gans[j][1]}化{GAN_HE[key]}')

        # 天干冲
        for i in range(len(gans)):
            for j in range(i + 1, len(gans)):
                if GAN_CHONG.get(gans[i][1]) == gans[j][1]:
                    relations.append(f'{gans[i][0]}{gans[i][1]}冲{gans[j][0]}{gans[j][1]}')

        # 地支六合
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                key = (zhis[i][1], zhis[j][1])
                if key in ZHI_LIUHE:
                    relations.append(f'{zhis[i][0]}{zhis[i][1]}合{zhis[j][0]}{zhis[j][1]}化{ZHI_LIUHE[key]}')

        # 地支冲
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                if ZHI_CHONG.get(zhis[i][1]) == zhis[j][1]:
                    relations.append(f'{zhis[i][0]}{zhis[i][1]}冲{zhis[j][0]}{zhis[j][1]}')

        # 地支刑
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                if ZHI_XING.get(zhis[i][1]) == zhis[j][1]:
                    relations.append(f'{zhis[i][0]}{zhis[i][1]}刑{zhis[j][0]}{zhis[j][1]}')

        # 地支害
        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                if ZHI_HAI.get(zhis[i][1]) == zhis[j][1]:
                    relations.append(f'{zhis[i][0]}{zhis[i][1]}害{zhis[j][0]}{zhis[j][1]}')

        return relations

    def _calc_dayun(self, gender: str, year_gz: str, month_gz: str) -> list:
        """计算大运（简化版：从月柱起排）"""
        year_gan = year_gz[0]
        is_yang = TIANGAN.index(year_gan) % 2 == 0

        # 阳男阴女顺排，阴男阳女逆排
        forward = (gender == '男' and is_yang) or (gender == '女' and not is_yang)

        month_gan_idx = TIANGAN.index(month_gz[0])
        month_zhi_idx = DIZHI.index(month_gz[1])

        dayun = []
        for i in range(1, 9):  # 8步大运
            if forward:
                gan_idx = (month_gan_idx + i) % 10
                zhi_idx = (month_zhi_idx + i) % 12
            else:
                gan_idx = (month_gan_idx - i) % 10
                zhi_idx = (month_zhi_idx - i) % 12

            gz = TIANGAN[gan_idx] + DIZHI[zhi_idx]
            start_age = i * 10  # 简化：每步10年
            dayun.append({
                'ganzhi': gz,
                'start_age': start_age,
                'nayin': NAYIN.get(gz, ''),
                'shishen': SHISHEN.get(year_gz[0], {}).get(TIANGAN[gan_idx], ''),
            })

        return dayun

    def _calc_shenshas(self, ri_gan: str, year_gz: str, month_gz: str,
                       day_gz: str, time_gz: str) -> list:
        """计算神煞（简化版）"""
        shenshas = []
        zhis = [year_gz[1], month_gz[1], day_gz[1], time_gz[1]]
        zhi_labels = ['年', '月', '日', '时']

        # 天乙贵人
        tianyi_map = {'甲': '丑未', '戊': '丑未', '庚': '丑未',
                      '乙': '子申', '己': '子申',
                      '丙': '酉亥', '丁': '酉亥',
                      '壬': '卯巳', '癸': '卯巳',
                      '辛': '寅午'}
        tianyi = tianyi_map.get(ri_gan, '')
        for i, zhi in enumerate(zhis):
            if zhi in tianyi:
                shenshas.append(f'{zhi_labels[i]}支{zhi}为天乙贵人')

        # 驿马
        yima_map = {'申子辰': '寅', '寅午戌': '申', '巳酉丑': '亥', '亥卯未': '巳'}
        year_zhi = year_gz[1]
        for group, ma in yima_map.items():
            if year_zhi in group:
                for i, zhi in enumerate(zhis):
                    if zhi == ma:
                        shenshas.append(f'{zhi_labels[i]}支{zhi}为驿马')

        # 桃花
        taohua_map = {'申子辰': '酉', '寅午戌': '卯', '巳酉丑': '午', '亥卯未': '子'}
        for group, hua in taohua_map.items():
            if year_zhi in group:
                for i, zhi in enumerate(zhis):
                    if zhi == hua:
                        shenshas.append(f'{zhi_labels[i]}支{zhi}为桃花')

        # 华盖
        huagai_map = {'申子辰': '辰', '寅午戌': '戌', '巳酉丑': '丑', '亥卯未': '未'}
        for group, gai in huagai_map.items():
            if year_zhi in group:
                for i, zhi in enumerate(zhis):
                    if zhi == gai:
                        shenshas.append(f'{zhi_labels[i]}支{zhi}为华盖')

        return shenshas

    def _calc_geju(self, result: BaziResult) -> str:
        """判断格局（简化版）"""
        month_ss = result.shishen.get('月干', '') or result.shishen.get('月支', '')

        if month_ss == '财' or month_ss == '才':
            return '财格'
        elif month_ss == '官':
            return '正官格'
        elif month_ss == '杀':
            return '七杀格'
        elif month_ss == '印' or month_ss == '枭':
            return '印格'
        elif month_ss == '食':
            return '食神格'
        elif month_ss == '伤':
            return '伤官格'
        elif month_ss == '比' or month_ss == '劫':
            return '比劫格'
        return '杂格'


# 全局实例
bazi_engine = BaziEngine()
