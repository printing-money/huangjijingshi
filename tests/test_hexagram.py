"""
测试核心卦象运算

验证：
- 变爻运算正确性
- 先天卦序完整性
- 四正卦处理
- 与 ref/saoyong/main.py 的结果对照
"""

import pytest
from src.core.hexagram import (
    get_hexagram, change_yao, find_pos_in_60,
    XIANTIAN_60_SEQUENCE, XIANTIAN_64_SEQUENCE,
    FOUR_PRINCIPAL, TWELVE_SOVEREIGN, is_four_principal,
    get_hexagram_by_name,
)


class TestHexagramBasics:
    """基础卦象测试"""

    def test_get_hexagram_qian(self):
        """乾卦 = 63 = 111111"""
        h = get_hexagram(63)
        assert h.name == '乾'
        assert h.binary == 63
        assert h.upper == '乾'
        assert h.lower == '乾'
        assert h.yang_count == 6

    def test_get_hexagram_kun(self):
        """坤卦 = 0 = 000000"""
        h = get_hexagram(0)
        assert h.name == '坤'
        assert h.binary == 0
        assert h.yang_count == 0
        assert h.yin_count == 6

    def test_get_hexagram_fu(self):
        """复卦 = 1 = 000001"""
        h = get_hexagram(1)
        assert h.name == '复'
        assert h.yang_count == 1

    def test_get_hexagram_gou(self):
        """姤卦 = 62 = 111110"""
        h = get_hexagram(62)
        assert h.name == '姤'
        assert h.yang_count == 5


class TestChangeYao:
    """变爻运算测试"""

    def test_qian_change_first(self):
        """乾卦变初爻 → 姤卦"""
        result = change_yao(63, 1)
        assert get_hexagram(result).name == '姤'

    def test_kun_change_first(self):
        """坤卦变初爻 → 复卦"""
        result = change_yao(0, 1)
        assert get_hexagram(result).name == '复'

    def test_gou_change_all(self):
        """姤卦(111110)逐爻变动 - 对照 ref/saoyong/main.py"""
        gou = 62  # 111110
        expected = ['乾', '遁', '讼', '巽', '鼎', '大过']
        for yao in range(1, 7):
            result = change_yao(gou, yao)
            assert get_hexagram(result).name == expected[yao - 1], \
                f"姤变第{yao}爻应为{expected[yao - 1]}，实际为{get_hexagram(result).name}"

    def test_fu_change_all(self):
        """复卦(000001)逐爻变动"""
        fu = 1  # 000001
        expected_binaries = [0, 3, 5, 9, 17, 33]
        for yao in range(1, 7):
            result = change_yao(fu, yao)
            assert result == expected_binaries[yao - 1]

    def test_invalid_yao(self):
        """无效爻位返回原值"""
        assert change_yao(63, 0) == 63
        assert change_yao(63, 7) == 63


class TestXiantianSequence:
    """先天卦序测试"""

    def test_64_sequence_length(self):
        """64卦序应有64个元素"""
        assert len(XIANTIAN_64_SEQUENCE) == 64

    def test_60_sequence_length(self):
        """60卦序应有60个元素"""
        assert len(XIANTIAN_60_SEQUENCE) == 60

    def test_60_no_four_principal(self):
        """60卦序不含四正卦"""
        for b in XIANTIAN_60_SEQUENCE:
            assert b not in FOUR_PRINCIPAL

    def test_64_starts_with_qian(self):
        """64卦序从乾开始"""
        assert XIANTIAN_64_SEQUENCE[0] == 63  # 乾

    def test_64_contains_all(self):
        """64卦序包含所有64卦"""
        assert set(XIANTIAN_64_SEQUENCE) == set(range(64))

    def test_fu_position_in_60(self):
        """复卦在60卦序中的位置"""
        pos = XIANTIAN_60_SEQUENCE.index(1)  # 复卦 binary=1
        assert pos == 30  # 第31位（索引30）

    def test_gou_position_in_60(self):
        """姤卦在60卦序中的位置"""
        pos = XIANTIAN_60_SEQUENCE.index(62)  # 姤卦 binary=62
        assert pos == 0  # 第1位（索引0）


class TestFindPosIn60:
    """先天60卦序定位测试"""

    def test_normal_hexagram(self):
        """普通卦象定位"""
        # 姤卦应在索引0
        assert find_pos_in_60(62) == 0
        # 复卦应在索引30
        assert find_pos_in_60(1) == 30

    def test_four_principal_fallback(self):
        """四正卦 fallback 定位"""
        # 乾卦(63)在64序中索引0，之前无四正卦，映射到60序位置0
        pos = find_pos_in_60(63)
        assert pos >= 0  # 应该能找到有效位置


class TestTwelveSovereign:
    """十二辟卦测试"""

    def test_length(self):
        assert len(TWELVE_SOVEREIGN) == 12

    def test_zi_is_fu(self):
        """子会 = 复卦"""
        assert get_hexagram(TWELVE_SOVEREIGN[0]).name == '复'

    def test_wu_is_gou(self):
        """午会 = 姤卦"""
        assert get_hexagram(TWELVE_SOVEREIGN[6]).name == '姤'

    def test_si_is_qian(self):
        """巳会 = 乾卦"""
        assert get_hexagram(TWELVE_SOVEREIGN[5]).name == '乾'

    def test_hai_is_kun(self):
        """亥会 = 坤卦"""
        assert get_hexagram(TWELVE_SOVEREIGN[11]).name == '坤'

    def test_yang_progression(self):
        """子到巳阳爻递增"""
        for i in range(5):
            assert get_hexagram(TWELVE_SOVEREIGN[i]).yang_count < \
                   get_hexagram(TWELVE_SOVEREIGN[i + 1]).yang_count


class TestGetByName:
    """按名称查找测试"""

    def test_find_qian(self):
        h = get_hexagram_by_name('乾')
        assert h is not None
        assert h.binary == 63

    def test_find_nonexist(self):
        h = get_hexagram_by_name('不存在')
        assert h is None
