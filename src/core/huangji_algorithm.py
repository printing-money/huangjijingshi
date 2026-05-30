from __future__ import annotations
"""
黄畿算法 - 分形同构九层卦象推演

基于黄畿《皇极经世书传》的完整推演体系：
- 元(乾) → 会(辟卦) → 运(主卦爻变) → 世(运卦爻变) → 十年律卦(世卦爻变)
-                                       ↘ 经卦(60年) → 岁(挨60卦次)
- → 月经(岁卦爻变·60天) → 旬纬(月经爻变·10天) → 日(挨60卦次) → 时经(日卦爻变·2时辰)

核心原则：
- "一六为经，六六为纬"
- "以一日当一年，一时当一月"
- 分形同构：微观层与宏观层推演法则完全一致
"""

from dataclasses import dataclass
from typing import Optional

from .hexagram import (
    Hexagram, get_hexagram, change_yao, find_pos_in_60,
    XIANTIAN_60_SEQUENCE, TWELVE_SOVEREIGN, FOUR_PRINCIPAL,
)
from .tiangan_dizhi import (
    HuangjiCoordinate, year_to_coordinate, gregorian_to_huangji,
)


@dataclass
class HexagramChain:
    """完整九层卦象链"""
    # 宏观层
    yuan: Hexagram           # 元卦（乾）
    hui: Hexagram            # 会卦（辟卦）
    yun: Hexagram            # 运卦
    shi: Hexagram            # 世卦
    ten_year: Hexagram       # 十年律卦
    sui: Hexagram            # 岁卦（年卦）

    # 微观层（可选，需要具体日期）
    yue_jing: Optional[Hexagram] = None   # 月经卦（60天）
    xun_wei: Optional[Hexagram] = None    # 旬纬卦（10天）
    ri: Optional[Hexagram] = None         # 日卦
    shi_jing: Optional[Hexagram] = None   # 时经卦（2时辰）

    # 坐标信息
    coordinate: Optional[HuangjiCoordinate] = None


class HuangjiEngine:
    """黄畿推演引擎"""

    def get_hui_hexagram(self, hui_index: int) -> Hexagram:
        """
        获取会卦（辟卦/十二消息卦）

        Args:
            hui_index: 会索引（0-11，子到亥）
        """
        binary = TWELVE_SOVEREIGN[hui_index % 12]
        return get_hexagram(binary)

    def get_yun_hexagram(self, hui_index: int, yun_in_hui: int) -> Hexagram:
        """
        计算运卦（星卦）

        每会30运，由5个主卦各管辖6运。
        主卦变动对应爻（初爻至上爻）产生值运卦。

        方位对应：子会从复卦开始（索引30），午会从姤卦开始（索引0）

        Args:
            hui_index: 会索引（0-11）
            yun_in_hui: 运在会内序号（0-29）
        """
        # 计算该会在60卦序中的起始位置
        hui_start = ((hui_index % 12) * 5 + 30) % 60

        # 每主卦管辖6运，计算主卦在会内的位置（0-4）
        master_index_in_hui = (yun_in_hui % 30) // 6

        # 全局索引
        global_index = (hui_start + master_index_in_hui) % 60

        # 主卦
        master_binary = XIANTIAN_60_SEQUENCE[global_index]

        # 变爻得运卦
        yao_to_change = (yun_in_hui % 6) + 1
        yun_binary = change_yao(master_binary, yao_to_change)

        return get_hexagram(yun_binary)

    def get_shi_hexagram(self, hui_index: int, yun_in_hui: int, shi_in_yun: int) -> Hexagram:
        """
        计算世卦（辰卦）

        每运12世，每2世共用一个世卦。
        世卦 = 运卦变对应爻位。

        Args:
            hui_index: 会索引（0-11）
            yun_in_hui: 运在会内序号（0-29）
            shi_in_yun: 世在运内序号（0-11）
        """
        yun_hex = self.get_yun_hexagram(hui_index, yun_in_hui)
        jiazi_shi_index = shi_in_yun // 2  # 每2世一个甲子世
        yao_to_change = jiazi_shi_index + 1
        shi_binary = change_yao(yun_hex.binary, yao_to_change)
        return get_hexagram(shi_binary)

    def get_ten_year_hexagram(self, hui_index: int, yun_in_hui: int,
                              shi_in_yun: int, year_in_shi: int) -> Hexagram:
        """
        计算十年律卦

        原文："一卦管十年，三十年为一世"
        前世（偶数世）：世卦变内三爻（初、二、三）
        后世（奇数世）：世卦变外三爻（四、五、上）

        Args:
            year_in_shi: 年在世内位置（0-29）
        """
        shi_hex = self.get_shi_hexagram(hui_index, yun_in_hui, shi_in_yun)
        shi_parity = shi_in_yun % 2
        decade_in_shi = year_in_shi // 10  # 0, 1, 2
        yao_index = shi_parity * 3 + decade_in_shi + 1  # 1-6
        ten_year_binary = change_yao(shi_hex.binary, yao_index)
        return get_hexagram(ten_year_binary)

    def get_sui_hexagram(self, gregorian_year: int) -> Hexagram:
        """
        计算岁卦（年卦）—— 黄畿"挨六十卦次"

        算法：运卦→变爻→经卦(管60年) → 经卦位置起，挨60卦次→年卦(1年1卦)

        原文（L1154-1156）：
        "从小畜分乾之四，挨六十卦次，求之即得其直年为何卦。"
        """
        huangji_sui = gregorian_year + 67017

        # 定位到运
        global_shi = max(1, (huangji_sui + 29) // 30)  # ceil
        hui_index = ((global_shi - 1) // 360) % 12
        shi_in_hui = (global_shi - 1) % 360
        yun_in_hui = shi_in_hui // 12

        # 获取运卦
        yun_hex = self.get_yun_hexagram(hui_index, yun_in_hui)

        # 计算年在运内的位置（0-359）
        yun_start_sui = ((huangji_sui - 1) // 360) * 360 + 1
        year_in_yun = huangji_sui - yun_start_sui

        # 经卦：运卦变爻，每卦管60年
        jing_index = year_in_yun // 60
        jing_binary = change_yao(yun_hex.binary, jing_index + 1)

        # 年卦：从经卦位置起，挨六十卦次
        jing_pos = find_pos_in_60(jing_binary)
        year_in_jing = year_in_yun % 60
        sui_idx = (jing_pos + year_in_jing) % 60

        return get_hexagram(XIANTIAN_60_SEQUENCE[sui_idx])

    def get_yue_jing_hexagram(self, gregorian_year: int, day_of_year: int) -> Hexagram:
        """
        月经卦 —— 岁卦变爻，每卦管60天

        原文 L1144："大要一六为经，六六为纬"
        """
        sui_hex = self.get_sui_hexagram(gregorian_year)
        day_index = max(0, min(day_of_year - 1, 359))
        jing_index = day_index // 60  # 0-5
        jing_binary = change_yao(sui_hex.binary, jing_index + 1)
        return get_hexagram(jing_binary)

    def get_xun_wei_hexagram(self, gregorian_year: int, day_of_year: int) -> Hexagram:
        """
        旬纬卦 —— 月经卦变爻，每卦管10天

        与宏观层"经卦→纬卦(管10年)"完全同构
        """
        sui_hex = self.get_sui_hexagram(gregorian_year)
        day_index = max(0, min(day_of_year - 1, 359))

        # 月经卦
        jing_index = day_index // 60
        jing_binary = change_yao(sui_hex.binary, jing_index + 1)

        # 旬纬卦
        day_in_jing = day_index % 60
        wei_index = day_in_jing // 10  # 0-5
        wei_binary = change_yao(jing_binary, wei_index + 1)
        return get_hexagram(wei_binary)

    def get_ri_hexagram(self, gregorian_year: int, day_of_year: int) -> Hexagram:
        """
        日卦 —— 从月经卦位置起，挨六十卦次

        与宏观层"经卦位置起，挨60卦次→年卦"完全同构
        """
        sui_hex = self.get_sui_hexagram(gregorian_year)
        day_index = max(0, min(day_of_year - 1, 359))

        # 月经卦
        jing_index = day_index // 60
        jing_binary = change_yao(sui_hex.binary, jing_index + 1)

        # 日卦：从月经卦位置起，挨六十卦次
        jing_pos = find_pos_in_60(jing_binary)
        day_in_jing = day_index % 60
        ri_idx = (jing_pos + day_in_jing) % 60
        return get_hexagram(XIANTIAN_60_SEQUENCE[ri_idx])

    def get_shi_jing_hexagram(self, gregorian_year: int, day_of_year: int,
                              shichen_index: int) -> Hexagram:
        """
        时经卦 —— 日卦变爻，每2时辰一变

        1日=12时辰，日卦变6爻 → 6个时经卦，每卦管2时辰

        Args:
            shichen_index: 时辰索引 0-11（子=0, ..., 亥=11）
        """
        ri_hex = self.get_ri_hexagram(gregorian_year, day_of_year)
        jing_index = shichen_index // 2  # 0-5
        jing_binary = change_yao(ri_hex.binary, jing_index + 1)
        return get_hexagram(jing_binary)

    def compute_chain(self, gregorian_year: int,
                      day_of_year: Optional[int] = None,
                      shichen_index: Optional[int] = None) -> HexagramChain:
        """
        计算完整的九层卦象链

        Args:
            gregorian_year: 公历年份
            day_of_year: 皇极年内天数（1-360，可选）
            shichen_index: 时辰索引（0-11，可选）
        """
        coord = year_to_coordinate(gregorian_year)

        # 宏观层
        yuan_hex = get_hexagram(63)  # 元卦固定为乾
        hui_hex = self.get_hui_hexagram(coord.hui - 1)
        yun_hex = self.get_yun_hexagram(coord.hui - 1, coord.yun - 1)
        shi_hex = self.get_shi_hexagram(coord.hui - 1, coord.yun - 1, coord.shi - 1)

        # 十年律卦
        year_in_shi = coord.sui - 1  # 0-29
        ten_year_hex = self.get_ten_year_hexagram(
            coord.hui - 1, coord.yun - 1, coord.shi - 1, year_in_shi
        )

        # 岁卦
        sui_hex = self.get_sui_hexagram(gregorian_year)

        chain = HexagramChain(
            yuan=yuan_hex,
            hui=hui_hex,
            yun=yun_hex,
            shi=shi_hex,
            ten_year=ten_year_hex,
            sui=sui_hex,
            coordinate=coord,
        )

        # 微观层（需要日期）
        if day_of_year is not None:
            chain.yue_jing = self.get_yue_jing_hexagram(gregorian_year, day_of_year)
            chain.xun_wei = self.get_xun_wei_hexagram(gregorian_year, day_of_year)
            chain.ri = self.get_ri_hexagram(gregorian_year, day_of_year)

            if shichen_index is not None:
                chain.shi_jing = self.get_shi_jing_hexagram(
                    gregorian_year, day_of_year, shichen_index
                )

        return chain


# 全局引擎实例
engine = HuangjiEngine()
