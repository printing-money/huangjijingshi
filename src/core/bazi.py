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

    # 调候用神
    tiaohou: str = ''
    jinbuhuan: str = ''

    # 扩展信息
    canggan_detail: list = field(default_factory=list)   # 四柱藏干详情
    changsheng_detail: list = field(default_factory=list) # 四柱长生状态
    kongwang: list = field(default_factory=list)          # 空亡
    liuqin: dict = field(default_factory=dict)           # 六亲
    xingge: list = field(default_factory=list)           # 性格描述

class BaziEngine:
    """八字排盘引擎"""

    def calculate(self, gender: str, year_gz: str, month_gz: str,
                  day_gz: str, time_gz: str, lunar_str: str = '',
                  gregorian_str: str = '', birth_dt=None) -> BaziResult:
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

        # 大运（传入日干和四柱用于十神和关系计算）
        result.dayun = self._calc_dayun(gender, year_gz, month_gz,
                                        birth_dt=birth_dt, ri_gan=day_gz[0],
                                        day_gz=day_gz, time_gz=time_gz)

        # 神煞
        result.shenshas = self._calc_shenshas(day_gz[0], year_gz, month_gz, day_gz, time_gz)

        # 日柱断语
        result.rizhu_duanyu = RIZHU_DUANYU.get(day_gz, '')

        # 调候用神
        from ..data.bazi_advanced import get_tiaohou, get_jinbuhuan
        result.tiaohou = get_tiaohou(day_gz[0], month_gz[1])
        result.jinbuhuan = get_jinbuhuan(day_gz[0], month_gz[1])

        # 格局
        result.geju = self._calc_geju(result)

        # === 扩展信息 ===
        # 藏干详情
        ri_gan = day_gz[0]
        ss_map = SHISHEN.get(ri_gan, {})
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            zhi = gz[1]
            canggan = ZHI_CANGGAN.get(zhi, [])
            detail = []
            for gan in canggan:
                wx = GAN_WUXING.get(gan, '')
                ss = ss_map.get(gan, '')
                detail.append({'gan': gan, 'wuxing': wx, 'shishen': ss})
            result.canggan_detail.append({'zhi': zhi, 'canggan': detail})

        # 长生状态
        cs_map = CHANGSHENG.get(ri_gan, {})
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            state = cs_map.get(gz[1], '')
            result.changsheng_detail.append({'zhi': gz[1], 'state': state})

        # 空亡（简化：以日柱查旬空）
        day_gan_idx = TIANGAN.index(day_gz[0])
        day_zhi_idx = DIZHI.index(day_gz[1])
        xun_start = (day_zhi_idx - day_gan_idx) % 12
        kong1 = DIZHI[(xun_start + 10) % 12]
        kong2 = DIZHI[(xun_start + 11) % 12]
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            if gz[1] in (kong1, kong2):
                result.kongwang.append(gz[1])

        # 六亲
        result.liuqin = {
            '父亲': '偏财' if TIANGAN.index(ri_gan) % 2 == 0 else '正财',
            '母亲': '正印' if TIANGAN.index(ri_gan) % 2 == 0 else '偏印',
            '配偶': '正财' if gender == '男' else '正官',
            '子女': '正官' if gender == '女' else '食神',
        }

        # 性格描述（基于日主十神组合）
        month_ss = result.shishen.get('月干', '') or result.shishen.get('月支', '')
        xingge_map = {
            '比': '自信独立，重义气，但固执己见。',
            '劫': '积极进取，善交际，但争强好胜。',
            '食': '温和聪慧，有才华，乐观开朗。',
            '伤': '才华横溢，不拘一格，但叛逆不羁。',
            '才': '勤劳务实，善理财，但过于精打细算。',
            '财': '稳重踏实，重信用，人缘好。',
            '杀': '果断刚毅，有魄力，但性急冲动。',
            '官': '正直守规，有责任感，适合管理。',
            '枭': '聪明多思，直觉强，但多疑孤僻。',
            '印': '仁慈宽厚，好学习，受人尊重。',
        }
        if month_ss:
            result.xingge.append(xingge_map.get(month_ss, ''))
        # 日支十神性格补充
        day_zhi_ss = result.shishen.get('日支', '')
        day_zhi_map = {
            '比': '配偶性格与自己相似。', '劫': '婚姻中易有竞争。',
            '食': '家庭生活愉快。', '伤': '配偶有才但个性强。',
            '才': '配偶能干，善持家。', '财': '配偶贤惠，助力事业。',
            '杀': '配偶强势，婚姻有压力。', '官': '配偶正派，家庭稳定。',
            '枭': '配偶聪明但关系需经营。', '印': '配偶关爱有加。',
        }
        if day_zhi_ss:
            result.xingge.append(day_zhi_map.get(day_zhi_ss, ''))

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
        """
        计算五行分数（与 ref/bazi 一致）

        规则：
        1. 四柱天干各 5 分
        2. 四柱地支藏干按精确权重
        3. 月支额外再算一次（月令加权）
        """
        score = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}

        # 地支藏干权重（与 ref/bazi zhi5 一致）
        ZHI_WEIGHTS = {
            '子': [('癸', 8)],
            '丑': [('己', 5), ('癸', 2), ('辛', 1)],
            '寅': [('甲', 5), ('丙', 2), ('戊', 1)],
            '卯': [('乙', 8)],
            '辰': [('戊', 5), ('乙', 2), ('癸', 1)],
            '巳': [('丙', 5), ('戊', 2), ('庚', 1)],
            '午': [('丁', 5), ('己', 3)],
            '未': [('己', 5), ('丁', 2), ('乙', 1)],
            '申': [('庚', 5), ('壬', 2), ('戊', 1)],
            '酉': [('辛', 8)],
            '戌': [('戊', 5), ('辛', 2), ('丁', 1)],
            '亥': [('壬', 5), ('甲', 3)],
        }

        # 天干各 5 分
        for gz in [year_gz, month_gz, day_gz, time_gz]:
            wx = GAN_WUXING.get(gz[0], '土')
            score[wx] += 5

        # 四柱地支 + 月支额外一次（月令加权）
        zhis = [year_gz[1], month_gz[1], day_gz[1], time_gz[1], month_gz[1]]
        for zhi in zhis:
            for gan, weight in ZHI_WEIGHTS.get(zhi, []):
                wx = GAN_WUXING.get(gan, '土')
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

    def _calc_dayun(self, gender: str, year_gz: str, month_gz: str,
                    birth_dt=None, ri_gan: str = '',
                    day_gz: str = '', time_gz: str = '') -> list:
        """
        计算大运

        起运年龄 = 出生日到最近节气的天数 ÷ 3
        阳男阴女顺排（数到下一节），阴男阳女逆排（数到上一节）
        """
        year_gan = year_gz[0]
        is_yang = TIANGAN.index(year_gan) % 2 == 0
        forward = (gender == '男' and is_yang) or (gender == '女' and not is_yang)

        # 计算起运年龄
        start_age = 1  # 默认
        if birth_dt:
            try:
                import cnlunar
                a = cnlunar.Lunar(birth_dt, godType='8char')
                jie_names = ['小寒', '立春', '惊蛰', '清明', '立夏', '芒种',
                             '小暑', '立秋', '白露', '寒露', '立冬', '大雪']
                birth_date = birth_dt.date() if hasattr(birth_dt, 'date') else birth_dt

                if forward:
                    # 顺排：到下一个节的天数
                    days = a.nextSolarNum if a.nextSolarNum else 15
                else:
                    # 逆排：到上一个节的天数
                    terms = a.thisYearSolarTermsDic
                    prev_jie_date = None
                    for name, d in sorted(terms.items(), key=lambda x: x[1]):
                        if name in jie_names:
                            term_date = d if isinstance(d, type(birth_date)) else \
                                        type(birth_date)(birth_dt.year, d[0], d[1])
                            if term_date <= birth_date:
                                prev_jie_date = term_date
                    if prev_jie_date:
                        days = (birth_date - prev_jie_date).days
                    else:
                        days = 15

                start_age = max(1, days // 3)
            except Exception:
                start_age = 5  # fallback

        # 排大运干支
        month_gan_idx = TIANGAN.index(month_gz[0])
        month_zhi_idx = DIZHI.index(month_gz[1])
        direction = 1 if forward else -1

        # 四柱地支（用于判断流年冲合）
        four_zhis = [year_gz[1], month_gz[1],
                     day_gz[1] if len(day_gz) >= 2 else '',
                     time_gz[1] if len(time_gz) >= 2 else '']

        # 出生年的天干地支索引（用于计算流年）
        year_gan_idx = TIANGAN.index(year_gz[0])
        year_zhi_idx = DIZHI.index(year_gz[1])
        birth_year = birth_dt.year if birth_dt else 1990

        dayun = []
        for i in range(1, 9):
            gan_idx = (month_gan_idx + i * direction) % 10
            zhi_idx = (month_zhi_idx + i * direction) % 12
            gz = TIANGAN[gan_idx] + DIZHI[zhi_idx]
            age = start_age + (i - 1) * 10

            # 十神（用日干）
            ss_map = SHISHEN.get(ri_gan, {}) if ri_gan else SHISHEN.get(year_gz[0], {})

            # 大运地支藏干
            dy_canggan = []
            for cg in ZHI_CANGGAN.get(DIZHI[zhi_idx], []):
                dy_canggan.append({'gan': cg, 'shishen': ss_map.get(cg, '')})

            # 大运与四柱的关系
            dy_relations = []
            dy_zhi = DIZHI[zhi_idx]
            chong_target = ZHI_CHONG.get(dy_zhi, '')
            if chong_target and chong_target in four_zhis:
                dy_relations.append(f'冲{chong_target}')
            for fz in four_zhis:
                if fz and (dy_zhi, fz) in ZHI_LIUHE:
                    dy_relations.append(f'合{fz}')
                    break

            # 长生状态
            cs_map = CHANGSHENG.get(ri_gan, {}) if ri_gan else {}
            dy_changsheng = cs_map.get(DIZHI[zhi_idx], '')

            # 10年流年详情
            liunian = []
            for y in range(10):
                ln_age = age + y
                ln_year = birth_year + ln_age - 1
                ln_gan_idx = (year_gan_idx + ln_age - 1) % 10
                ln_zhi_idx = (year_zhi_idx + ln_age - 1) % 12
                ln_gan = TIANGAN[ln_gan_idx]
                ln_zhi = DIZHI[ln_zhi_idx]
                ln_gz = ln_gan + ln_zhi
                ln_ss = ss_map.get(ln_gan, '')
                ln_zhi_ss = ss_map.get(ZHI_CANGGAN.get(ln_zhi, [''])[0], '')
                ln_nayin = NAYIN.get(ln_gz, '')
                ln_cs = cs_map.get(ln_zhi, '')

                # 流年与四柱的冲合
                ln_relations = []
                chong_target = ZHI_CHONG.get(ln_zhi, '')
                if chong_target and chong_target in four_zhis:
                    ln_relations.append(f'冲{chong_target}')
                for fz in four_zhis:
                    if fz and (ln_zhi, fz) in ZHI_LIUHE:
                        ln_relations.append(f'合{fz}')
                        break

                liunian.append({
                    'age': ln_age,
                    'year': ln_year,
                    'ganzhi': ln_gz,
                    'gan_shishen': ln_ss,
                    'zhi_shishen': ln_zhi_ss,
                    'nayin': ln_nayin,
                    'changsheng': ln_cs,
                    'relations': ln_relations,
                })

            dayun.append({
                'ganzhi': gz,
                'start_age': age,
                'nayin': NAYIN.get(gz, ''),
                'shishen': ss_map.get(TIANGAN[gan_idx], ''),
                'changsheng': dy_changsheng,
                'canggan': dy_canggan,
                'relations': dy_relations,
                'liunian': liunian,
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
