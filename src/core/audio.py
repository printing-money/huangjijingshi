"""
律吕音频合成引擎

两种模式：
1. 采样模式（优先）：使用预录制的真实乐器 WAV 采样
2. 合成模式（兜底）：Karplus-Strong 弦乐物理建模

Karplus-Strong 算法模拟真实弦振动：
- 用噪声填充延迟线（模拟拨弦瞬间）
- 反复对延迟线做低通滤波（模拟弦的能量耗散）
- 自然产生谐波结构，听起来像真实拨弦乐器

无需第三方依赖，仅使用 Python 标准库。
"""

from __future__ import annotations

import io
import math
import random
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .changhe import TWELVE_LVLV, LvLv, get_year_lv, get_month_lv, get_day_lv, get_hour_lv


# 黄钟基准频率（Hz）— 取 C4 = 261.63Hz
HUANGZHONG_FREQ = 261.63

# 采样率
SAMPLE_RATE = 44100

# 采样文件目录
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


@dataclass
class ToneConfig:
    """音色配置"""
    duration: float = 2.0       # 时长（秒）
    amplitude: float = 0.7      # 音量 (0-1)
    timbre: str = 'guqin'       # 音色: guqin(古琴) / bianqing(编磬) / xiao(箫)
    brightness: float = 0.5     # 明亮度 (0-1)，影响高频衰减速度


def lv_to_frequency(lv: LvLv) -> float:
    """律吕转频率（Hz）"""
    return HUANGZHONG_FREQ * lv.frequency_ratio


def _karplus_strong(frequency: float, duration: float, amplitude: float = 0.7,
                    brightness: float = 0.5, pluck_position: float = 0.4) -> list:
    """
    Karplus-Strong 弦乐物理建模

    原理：用短噪声脉冲激励一个带低通滤波的延迟线，
    延迟线长度决定音高，滤波系数决定音色衰减。

    Args:
        frequency: 目标频率
        duration: 时长
        amplitude: 音量
        brightness: 明亮度（0=暗沉 1=明亮）
        pluck_position: 拨弦位置（0=琴桥 1=中央），影响泛音结构
    """
    n_samples = int(SAMPLE_RATE * duration)
    delay_length = int(SAMPLE_RATE / frequency)

    if delay_length < 2:
        delay_length = 2

    # 初始化延迟线（模拟拨弦瞬间的弦形状）
    # 用带通滤波的噪声，pluck_position 决定哪些泛音被抑制
    buffer = [0.0] * delay_length
    for i in range(delay_length):
        # 基础噪声
        noise = random.uniform(-1, 1)
        # 拨弦位置滤波：在 pluck_position 处拨弦会抑制该位置为节点的泛音
        pos = i / delay_length
        shape = math.sin(math.pi * pos / pluck_position) if pos < pluck_position else \
                math.sin(math.pi * (1 - pos) / (1 - pluck_position))
        buffer[i] = noise * abs(shape) * amplitude

    # 生成音频
    samples = []
    idx = 0

    # 低通滤波系数（brightness 越高，高频保留越多）
    decay = 0.994 + brightness * 0.005  # 0.994 ~ 0.999
    # 一阶低通混合系数
    blend = 0.3 + brightness * 0.4  # 0.3 ~ 0.7

    for i in range(n_samples):
        # 从延迟线读取当前样本
        current = buffer[idx]
        samples.append(current)

        # Karplus-Strong 核心：对相邻样本做加权平均（低通滤波）
        next_idx = (idx + 1) % delay_length
        # 扩展 KS：加入 blend 系数控制音色
        filtered = decay * (blend * buffer[idx] + (1 - blend) * buffer[next_idx])

        # 写回延迟线
        buffer[idx] = filtered

        idx = next_idx

    return samples


def _apply_envelope(samples: list, duration: float, attack: float = 0.005) -> list:
    """应用包络：极短 attack + 自然衰减（KS 自带衰减，这里只处理起音和尾部）"""
    n = len(samples)
    attack_samples = int(SAMPLE_RATE * attack)
    release_samples = int(SAMPLE_RATE * 0.05)

    for i in range(min(attack_samples, n)):
        samples[i] *= i / attack_samples

    # 尾部淡出（避免截断噪声）
    for i in range(min(release_samples, n)):
        idx = n - 1 - i
        samples[idx] *= i / release_samples

    return samples


def generate_tone(frequency: float, config: Optional[ToneConfig] = None) -> bytes:
    """
    生成单个音调的 PCM 数据

    使用 Karplus-Strong 物理建模，不同 timbre 通过参数调整实现：
    - guqin: 低 brightness，长 duration，拨弦位置偏中央
    - bianqing: 高 brightness，短 decay，拨弦位置偏边缘
    - xiao: 中等 brightness，加入气息噪声
    """
    if config is None:
        config = ToneConfig()

    # 根据音色调整参数
    if config.timbre == 'guqin':
        brightness = 0.3
        pluck_pos = 0.35
    elif config.timbre == 'bianqing':
        brightness = 0.8
        pluck_pos = 0.15
    else:  # xiao
        brightness = 0.5
        pluck_pos = 0.5

    samples = _karplus_strong(
        frequency, config.duration, config.amplitude,
        brightness=brightness, pluck_position=pluck_pos,
    )
    samples = _apply_envelope(samples, config.duration)

    # 箫加入气息感
    if config.timbre == 'xiao':
        for i in range(len(samples)):
            t = i / SAMPLE_RATE
            breath = random.uniform(-0.02, 0.02) * math.exp(-t * 2)
            samples[i] = samples[i] * 0.85 + breath

    # 转 16-bit PCM
    pcm_samples = []
    for s in samples:
        val = int(s * 32767)
        val = max(-32768, min(32767, val))
        pcm_samples.append(val)

    return struct.pack(f'<{len(pcm_samples)}h', *pcm_samples)


def generate_wav(pcm_data: bytes) -> bytes:
    """将 PCM 数据封装为 WAV 格式"""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)          # 单声道
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def generate_lv_tone(lv: LvLv, config: Optional[ToneConfig] = None) -> bytes:
    """生成单个律吕的 WAV 音频"""
    freq = lv_to_frequency(lv)
    pcm = generate_tone(freq, config)
    return generate_wav(pcm)


def generate_sequence(lvs: list, gap: float = 0.1,
                      config: Optional[ToneConfig] = None) -> bytes:
    """
    生成律吕序列的 WAV 音频（多个音依次播放）

    Args:
        lvs: 律吕列表
        gap: 音符间隔（秒）
        config: 音色配置
    """
    if config is None:
        config = ToneConfig(duration=0.8)

    all_pcm = b''
    gap_samples = int(SAMPLE_RATE * gap)
    gap_pcm = struct.pack(f'<{gap_samples}h', *([0] * gap_samples))

    for i, lv in enumerate(lvs):
        freq = lv_to_frequency(lv)
        pcm = generate_tone(freq, config)
        all_pcm += pcm
        if i < len(lvs) - 1:
            all_pcm += gap_pcm

    return generate_wav(all_pcm)


def generate_chord(lvs: list, config: Optional[ToneConfig] = None) -> bytes:
    """
    生成和弦（多个律吕同时发声）
    """
    if config is None:
        config = ToneConfig(duration=2.5)

    n_samples = int(SAMPLE_RATE * config.duration)
    mixed = [0.0] * n_samples

    for lv in lvs:
        freq = lv_to_frequency(lv)
        tone_pcm = generate_tone(freq, config)
        tone_samples = struct.unpack(f'<{n_samples}h', tone_pcm[:n_samples * 2])
        for i in range(min(n_samples, len(tone_samples))):
            mixed[i] += tone_samples[i] / 32767.0

    # 归一化
    peak = max(abs(v) for v in mixed) if mixed else 1.0
    if peak > 0:
        scale = config.amplitude / peak
    else:
        scale = 0

    pcm_data = struct.pack(
        f'<{n_samples}h',
        *[max(-32768, min(32767, int(v * scale * 32767))) for v in mixed]
    )
    return generate_wav(pcm_data)


def generate_four_pillars_audio(year_gan: int, month_zhi: int,
                                day_gan: int, hour_zhi: int,
                                timbre: str = 'bianqing') -> bytes:
    """
    生成四柱律吕序列音频（年→月→日→时）

    依次播放年律、月律、日律、时律
    """
    lvs = [
        get_year_lv(year_gan),
        get_month_lv(month_zhi),
        get_day_lv(day_gan),
        get_hour_lv(hour_zhi),
    ]
    config = ToneConfig(duration=1.0, amplitude=0.5, timbre=timbre)
    return generate_sequence(lvs, gap=0.15, config=config)
