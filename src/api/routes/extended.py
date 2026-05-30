"""
扩展 API 路由：卦辞解读、声音唱和、AI 解读、音频合成
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import Response
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

# === 音频合成 ===

@router.get("/audio/lv/{lv_name}")
def get_lv_audio(lv_name: str, duration: float = Query(default=1.5, ge=0.3, le=5.0)):
    """播放单个律吕的音频（WAV格式）"""
    from ...core.audio import generate_lv_tone, ToneConfig, TWELVE_LVLV

    lv = None
    for l in TWELVE_LVLV:
        if l.name == lv_name:
            lv = l
            break
    if not lv:
        return Response(content=b'', status_code=404)

    config = ToneConfig(duration=duration)
    wav_data = generate_lv_tone(lv, config)
    return Response(content=wav_data, media_type='audio/wav')


@router.get("/audio/daily")
def get_daily_audio(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    day: int = Query(..., ge=1, le=31),
):
    """生成指定日期的四柱律吕序列音频（年→月→日→时）"""
    from ...core.audio import generate_four_pillars_audio
    from ...core.tiangan_dizhi import day_ganzhi_index, index_to_ganzhi, year_ganzhi, hour_to_shichen
    from datetime import datetime

    # 年干
    ygz = year_ganzhi(year)
    # 日干支
    day_idx = day_ganzhi_index(year, month, day)
    dgz = index_to_ganzhi(day_idx)
    # 月支（简化：月份-1对应地支）
    month_zhi = (month + 1) % 12  # 正月=寅(2)
    # 时支（用当前小时）
    hour_zhi = hour_to_shichen(datetime.now().hour)

    wav_data = generate_four_pillars_audio(ygz.gan_index, month_zhi, dgz.gan_index, hour_zhi)
    return Response(content=wav_data, media_type='audio/wav')


@router.get("/audio/sequence")
def get_sequence_audio(
    lvs: str = Query(..., description="律吕名称序列，逗号分隔，如：黄钟,太簇,姑洗"),
    duration: float = Query(default=0.8, ge=0.3, le=3.0),
):
    """生成自定义律吕序列音频"""
    from ...core.audio import generate_sequence, ToneConfig, TWELVE_LVLV

    lv_names = [n.strip() for n in lvs.split(',')]
    lv_list = []
    for name in lv_names:
        for l in TWELVE_LVLV:
            if l.name == name:
                lv_list.append(l)
                break

    if not lv_list:
        return Response(content=b'', status_code=400)

    config = ToneConfig(duration=duration)
    wav_data = generate_sequence(lv_list, gap=0.1, config=config)
    return Response(content=wav_data, media_type='audio/wav')


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
