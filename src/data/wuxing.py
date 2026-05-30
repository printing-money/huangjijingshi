"""
五行分析模块

提供卦象的五行属性分析、生克关系判断。
"""

from __future__ import annotations

from ..core.hexagram import Hexagram


# 八卦五行对应
TRIGRAM_WUXING = {
    '乾': '金', '兑': '金',
    '离': '火',
    '震': '木', '巽': '木',
    '坎': '水',
    '艮': '土', '坤': '土',
}

# 五行生克
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
WUXING_NAMES = ['木', '火', '土', '金', '水']


def get_hexagram_wuxing_analysis(hexagram: Hexagram) -> dict:
    """分析卦象的五行属性"""
    upper_wx = TRIGRAM_WUXING.get(hexagram.upper, '土')
    lower_wx = TRIGRAM_WUXING.get(hexagram.lower, '土')

    # 判断关系
    if upper_wx == lower_wx:
        relation = '比和'
        harmony = '和谐'
    elif WUXING_SHENG.get(lower_wx) == upper_wx:
        relation = '下生上'
        harmony = '顺畅'
    elif WUXING_SHENG.get(upper_wx) == lower_wx:
        relation = '上生下'
        harmony = '泄气'
    elif WUXING_KE.get(upper_wx) == lower_wx:
        relation = '上克下'
        harmony = '压制'
    elif WUXING_KE.get(lower_wx) == upper_wx:
        relation = '下克上'
        harmony = '反抗'
    else:
        relation = '无直接关系'
        harmony = '中性'

    return {
        'upper_wuxing': upper_wx,
        'lower_wuxing': lower_wx,
        'relation': relation,
        'harmony': harmony,
        'description': f"上卦{hexagram.upper}属{upper_wx}，下卦{hexagram.lower}属{lower_wx}，{relation}",
    }
