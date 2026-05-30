"""
扩展 API 路由：卦辞解读、声音唱和、AI 解读
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import Optional

from ...core.hexagram import get_hexagram_by_name
from ...core.huangji_algorithm import HuangjiEngine
from ...core.changhe import ChangheSystem, TWELVE_LVLV
from ...core.tiangan_dizhi import day_ganzhi_index, index_to_ganzhi
from ...data.interpretations import InterpretationEngine, INTERPRETATIONS
from ...data.wuxing import get_hexagram_wuxing_analysis
from ...analysis.ai_interpreter import AIInterpreter

router = APIRouter()
engine = HuangjiEngine()
changhe = ChangheSystem()
interp_engine = InterpretationEngine()
ai_interpreter = AIInterpreter()


# === 卦辞解读 ===

@router.get("/interpret/{hexagram_name}")
def get_interpretation(hexagram_name: str):
    """获取卦象的卦辞、象辞、爻辞解读"""
    hex_ = get_hexagram_by_name(hexagram_name)
    if not hex_:
        return {'error': f'未找到卦象: {hexagram_name}'}

    interp = INTERPRETATIONS.get(hexagram_name)
    wuxing = get_hexagram_wuxing_analysis(hex_)

    result = {
        'hexagram': {
            'name': hex_.name,
            'unicode': hex_.unicode,
            'binary': hex_.binary,
            'upper': hex_.upper,
            'lower': hex_.lower,
            'yang_count': hex_.yang_count,
        },
        'wuxing': wuxing,
    }

    if interp:
        result['interpretation'] = {
            'gua_ci': interp.gua_ci,
            'tuan_ci': interp.tuan_ci,
            'xiang_ci': interp.xiang_ci,
            'nature': interp.nature,
            'keywords': interp.keywords,
            'yao_ci': interp.yao_ci,
        }
    else:
        result['interpretation'] = {'note': '该卦详细卦辞数据待补充'}

    return result


@router.get("/interpret/chain/{year}")
def interpret_chain(year: int):
    """获取指定年份卦象链的综合解读"""
    chain = engine.compute_chain(year)
    result = interp_engine.interpret_chain(chain)
    return result


# === 声音唱和 ===

@router.get("/changhe/daily")
def get_daily_changhe(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    day: int = Query(..., ge=1, le=31),
):
    """获取指定日期的声音唱和信息"""
    day_idx = day_ganzhi_index(year, month, day)
    gz = index_to_ganzhi(day_idx)
    result = changhe.get_daily_changhe(gz.gan_index, gz.zhi_index)
    result['date'] = f"{year}-{month:02d}-{day:02d}"
    result['ganzhi'] = gz.name
    return result


@router.get("/changhe/matrix")
def get_changhe_matrix():
    """获取完整的10×12唱和千字发音矩阵"""
    return changhe.get_full_matrix()


@router.get("/changhe/lvlv")
def get_lvlv_system():
    """获取十二律吕完整信息"""
    return {
        'twelve_lvlv': [
            {'name': lv.name, 'type': lv.type, 'index': lv.index,
             'frequency_ratio': lv.frequency_ratio}
            for lv in TWELVE_LVLV
        ]
    }


# === AI 解读 ===

@router.get("/ai/interpret/{year}")
def ai_interpret(
    year: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    day: Optional[int] = Query(None, ge=1, le=31),
):
    """
    AI 辅助解读（本地规则引擎）

    返回结构化的卦象解读和可用于 LLM 的 prompt
    """
    result = ai_interpreter.interpret_locally(year, month, day)
    return result


@router.get("/ai/prompt/{year}")
def get_ai_prompt(
    year: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    day: Optional[int] = Query(None, ge=1, le=31),
):
    """
    获取用于 LLM 的推演 prompt

    可将此 prompt 直接发送给 Claude/GPT 等模型进行深度解读
    """
    prompt = ai_interpreter.build_chain_prompt(year, month, day)
    return {'year': year, 'prompt': prompt}
