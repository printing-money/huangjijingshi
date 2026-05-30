"""
AI 辅助解读模块

提供基于 LLM 的卦象语义分析能力：
- 构建结构化的卦象 prompt
- 支持多种 LLM 后端（OpenAI/Anthropic/本地模型）
- 卦象链综合解读
- 历史对照分析
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import json

from ..core.hexagram import Hexagram
from ..core.huangji_algorithm import HuangjiEngine, HexagramChain
from ..core.tiangan_dizhi import year_ganzhi, year_to_coordinate
from ..data.interpretations import InterpretationEngine, INTERPRETATIONS
from ..data.wuxing import get_hexagram_wuxing_analysis


@dataclass
class AIInterpretation:
    """AI 解读结果"""
    prompt: str              # 发送给 LLM 的 prompt
    response: str            # LLM 返回的解读
    model: str               # 使用的模型
    context: dict            # 上下文数据


class AIInterpreter:
    """AI 辅助解读器"""

    def __init__(self, api_key: Optional[str] = None, model: str = 'claude-sonnet-4-6'):
        self.api_key = api_key
        self.model = model
        self.engine = HuangjiEngine()
        self.interp_engine = InterpretationEngine()

    def build_chain_prompt(self, year: int, month: Optional[int] = None,
                           day: Optional[int] = None) -> str:
        """
        构建卦象链解读 prompt

        生成结构化的上下文信息供 LLM 分析
        """
        day_of_year = None
        if month and day:
            day_of_year = (month - 1) * 30 + day

        chain = self.engine.compute_chain(year, day_of_year)
        coord = chain.coordinate
        gz = year_ganzhi(year)

        # 构建卦象信息
        layers_info = []
        layer_data = [
            ('元', chain.yuan, '统摄129600年，代表整个宇宙大周期'),
            ('会', chain.hui, f'统摄10800年，当前第{coord.hui}会'),
            ('运', chain.yun, f'统摄360年，当前第{coord.global_yun}运'),
            ('世', chain.shi, f'统摄30年，当前第{coord.shi}世'),
            ('十年律卦', chain.ten_year, '统摄10年'),
            ('岁', chain.sui, '统摄1年，流年主卦'),
        ]

        for level, hex_, desc in layer_data:
            interp = INTERPRETATIONS.get(hex_.name)
            wuxing = get_hexagram_wuxing_analysis(hex_)
            info = f"  {level}卦：{hex_.unicode}{hex_.name}（{desc}）"
            info += f"\n    上卦{hex_.upper}({wuxing['upper_wuxing']}) 下卦{hex_.lower}({wuxing['lower_wuxing']}) {wuxing['relation']}"
            info += f"\n    阳爻{hex_.yang_count}/6"
            if interp:
                info += f"\n    卦辞：{interp.gua_ci}"
                info += f"\n    象曰：{interp.xiang_ci}"
            layers_info.append(info)

        prompt = f"""你是一位精通邵雍《皇极经世书》的易学研究者。请基于以下卦象信息，对{year}年（{gz.name}年）的世运进行综合分析和解读。

## 皇极坐标
- 公历{year}年，干支{gz.name}年
- 皇极第{coord.huangji_year}年
- 第{coord.hui}会 第{coord.yun}运（全元第{coord.global_yun}运）第{coord.shi}世 第{coord.sui}年

## 九层卦象链
{chr(10).join(layers_info)}

## 分析要求
请从以下维度进行解读：
1. **大势研判**：基于运卦和世卦，分析当前所处的历史大周期特征
2. **流年主题**：基于岁卦的卦辞、象辞，解读本年的核心主题
3. **五行生克**：分析各层卦象的五行关系，判断能量流向
4. **阴阳消长**：基于阳爻数的变化趋势，判断当前处于阴阳消长的哪个阶段
5. **历史对照**：联想历史上类似卦象组合出现时的情况
6. **趋势展望**：基于卦象变化规律，对未来走势做出推演

请用通俗易懂的语言解读，既要有学术依据，也要有现实参考价值。"""

        return prompt

    def build_comparison_prompt(self, year: int, similar_events: list) -> str:
        """构建历史对照分析 prompt"""
        chain = self.engine.compute_chain(year)
        gz = year_ganzhi(year)

        events_info = []
        for event_data in similar_events[:5]:
            event = event_data['event']
            event_chain = self.engine.compute_chain(event.year)
            events_info.append(
                f"  - {event.year}年 {event.name}（{event.event_type.value}）"
                f"岁卦:{event_chain.sui.name} 运卦:{event_chain.yun.name}"
            )

        prompt = f"""作为皇极经世研究者，请分析{year}年（{gz.name}年）与以下历史时期的卦象相似性，并推演可能的发展趋势。

## 当前年份卦象
- {year}年 岁卦:{chain.sui.unicode}{chain.sui.name} 运卦:{chain.yun.unicode}{chain.yun.name} 世卦:{chain.shi.unicode}{chain.shi.name}

## 历史上卦象相似的时期
{chr(10).join(events_info)}

请分析：
1. 这些历史时期与当前的共同卦象特征是什么？
2. 历史上这些卦象组合出现时，通常伴随什么类型的事件？
3. 基于"历史不会重复，但会押韵"的原则，当前可能面临什么样的机遇或挑战？
4. 从卦象变化的角度，给出应对建议。"""

        return prompt

    def interpret_locally(self, year: int, month: Optional[int] = None,
                          day: Optional[int] = None) -> dict:
        """
        本地解读（不依赖外部 API）

        基于内置的卦辞数据和规则引擎生成解读
        """
        day_of_year = None
        if month and day:
            day_of_year = (month - 1) * 30 + day

        chain = self.engine.compute_chain(year, day_of_year)
        coord = chain.coordinate
        gz = year_ganzhi(year)

        # 使用解读引擎
        chain_interp = self.interp_engine.interpret_chain(chain)

        # 五行分析
        sui_wuxing = get_hexagram_wuxing_analysis(chain.sui)
        yun_wuxing = get_hexagram_wuxing_analysis(chain.yun)

        # 阴阳状态
        sui_yang = chain.sui.yang_count
        if sui_yang >= 5:
            yin_yang_state = "阳气极盛，物极必反之象"
        elif sui_yang >= 4:
            yin_yang_state = "阳气旺盛，进取有为之时"
        elif sui_yang == 3:
            yin_yang_state = "阴阳平衡，中正和谐之象"
        elif sui_yang >= 2:
            yin_yang_state = "阴气渐长，宜守不宜攻"
        elif sui_yang >= 1:
            yin_yang_state = "阴气盛而一阳来复，转机将至"
        else:
            yin_yang_state = "纯阴之象，静极思动，蓄势待发"

        return {
            'year': year,
            'ganzhi': gz.name,
            'coordinate': {
                'hui': coord.hui,
                'yun': coord.yun,
                'global_yun': coord.global_yun,
                'shi': coord.shi,
            },
            'hexagram_chain': {
                'yun': f"{chain.yun.unicode}{chain.yun.name}",
                'shi': f"{chain.shi.unicode}{chain.shi.name}",
                'sui': f"{chain.sui.unicode}{chain.sui.name}",
            },
            'interpretation': chain_interp,
            'wuxing_analysis': {
                'sui': sui_wuxing,
                'yun': yun_wuxing,
            },
            'yin_yang_state': yin_yang_state,
            'prompt_for_llm': self.build_chain_prompt(year, month, day),
        }

    async def interpret_with_llm(self, year: int, month: Optional[int] = None,
                                  day: Optional[int] = None) -> AIInterpretation:
        """
        使用 LLM 进行深度解读

        需要配置 API key。支持 Anthropic Claude API。
        """
        prompt = self.build_chain_prompt(year, month, day)

        if not self.api_key:
            return AIInterpretation(
                prompt=prompt,
                response="未配置 API Key。请设置 ANTHROPIC_API_KEY 环境变量，或使用 interpret_locally() 进行本地解读。",
                model=self.model,
                context={'year': year},
            )

        # Anthropic API 调用
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': self.model,
                        'max_tokens': 2000,
                        'messages': [{'role': 'user', 'content': prompt}],
                    },
                    timeout=60.0,
                )
                data = resp.json()
                response_text = data.get('content', [{}])[0].get('text', '解读失败')

        except Exception as e:
            response_text = f"API 调用失败: {str(e)}"

        return AIInterpretation(
            prompt=prompt,
            response=response_text,
            model=self.model,
            context={'year': year, 'month': month, 'day': day},
        )
