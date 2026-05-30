"""
律吕音频合成引擎

基于十二律吕的频率比关系，合成 WAV 音频：
- 纯正弦波（古琴音色模拟）
- 支持单音、和弦、序列播放
- 输出 WAV 格式，前端可直接 <audio> 播放

无需第三方依赖，仅使用 Python 标准库。
"""

from __future__ import annotations

import io
import math
import struct
import wave
from dataclasses import dataclass
from typing import Optional

from .changhe import TWELVE_LVLV, LvLv, get_year_lv, get_month_lv, get_day_lv, get_hour_lv


# 黄钟基准频率（Hz）
# 取中央C (C4) = 261.63Hz 作为黄钟
HUANGZHONG_FREQ = 261.63

# 采样率
SAMPLE_RATE = 44100


@dataclass
class ToneConfig:
    """音色配置"""
    duration: float = 1.5       # 时长（秒）
    amplitude: float = 0.6      # 音量 (0-1)
    attack: float = 0.05        # 起音时间（秒）
    decay: float = 0.3          # 衰减时间（秒）
    sustain: float = 0.7        # 持续音量比
    release: float = 0.4        # 释音时间（秒）
    harmonics: list = None      # 泛音系数 [(倍频, 振幅), ...]

    def __post_init__(self):
        if self.harmonics is None:
            # 默认泛音：模拟古琴/编钟音色
            self.harmonics = [
                (1.0, 1.0),     # 基频
                (2.0, 0.3),     # 二倍频
                (3.0, 0.15),    # 三倍频
                (4.0, 0.08),    # 四倍频
                (5.0, 0.04),    # 五倍频
            ]


def lv_to_frequency(lv: LvLv) -> float:
    """律吕转频率（Hz）"""
    return HUANGZHONG_FREQ * lv.frequency_ratio


def generate_tone(frequency: float, config: Optional[ToneConfig] = None) -> bytes:
    """
    生成单个音调的 PCM 数据

    使用 ADSR 包络 + 泛音叠加，模拟古乐器音色
    """
    if config is None:
        config = ToneConfig()

    num_samples = int(SAMPLE_RATE * config.duration)
    samples = []

    for i in range(num_samples):
        t = i / SAMPLE_RATE

        # ADSR 包络
        if t < config.attack:
            envelope = t / config.attack
        elif t < config.attack + config.decay:
            decay_progress = (t - config.attack) / config.decay
            envelope = 1.0 - (1.0 - config.sustain) * decay_progress
        elif t < config.duration - config.release:
            envelope = config.sustain
        else:
            release_progress = (t - (config.duration - config.release)) / config.release
            envelope = config.sustain * (1.0 - release_progress)

        # 泛音叠加
        value = 0.0
        for harmonic_mult, harmonic_amp in config.harmonics:
            value += harmonic_amp * math.sin(2 * math.pi * frequency * harmonic_mult * t)

        # 归一化泛音
        total_amp = sum(a for _, a in config.harmonics)
        value /= total_amp

        # 应用包络和音量
        value *= envelope * config.amplitude

        # 转为 16-bit PCM
        sample = int(value * 32767)
        sample = max(-32768, min(32767, sample))
        samples.append(sample)

    return struct.pack(f'<{len(samples)}h', *samples)


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

    Args:
        lvs: 律吕列表（同时发声）
        config: 音色配置
    """
    if config is None:
        config = ToneConfig(duration=2.0)

    num_samples = int(SAMPLE_RATE * config.duration)
    mixed = [0.0] * num_samples

    for lv in lvs:
        freq = lv_to_frequency(lv)
        for i in range(num_samples):
            t = i / SAMPLE_RATE

            # ADSR
            if t < config.attack:
                envelope = t / config.attack
            elif t < config.attack + config.decay:
                decay_progress = (t - config.attack) / config.decay
                envelope = 1.0 - (1.0 - config.sustain) * decay_progress
            elif t < config.duration - config.release:
                envelope = config.sustain
            else:
                release_progress = (t - (config.duration - config.release)) / config.release
                envelope = config.sustain * (1.0 - release_progress)

            value = math.sin(2 * math.pi * freq * t) * envelope
            mixed[i] += value

    # 归一化
    peak = max(abs(v) for v in mixed) if mixed else 1.0
    if peak > 0:
        scale = config.amplitude / peak
    else:
        scale = 0

    pcm_data = struct.pack(
        f'<{num_samples}h',
        *[max(-32768, min(32767, int(v * scale * 32767))) for v in mixed]
    )
    return generate_wav(pcm_data)


def generate_four_pillars_audio(year_gan: int, month_zhi: int,
                                day_gan: int, hour_zhi: int) -> bytes:
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
    config = ToneConfig(duration=1.0, amplitude=0.5)
    return generate_sequence(lvs, gap=0.15, config=config)
