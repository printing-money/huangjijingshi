"""
LLM 对话路由

支持两种模式：
1. 有 API Key → 直接调用 LLM 返回流式解读
2. 无 API Key → 返回结构化 prompt 供用户复制
"""

from __future__ import annotations

import os
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from ...core.huangji_algorithm import HuangjiEngine
from ...core.tiangan_dizhi import year_ganzhi, year_to_coordinate
from ...data.interpretations import INTERPRETATIONS
from ...data.wuxing import get_hexagram_wuxing_analysis
from ...analysis.ai_interpreter import AIInterpreter

router = APIRouter()
engine = HuangjiEngine()


class ChatRequest(BaseModel):
    """对话请求"""
    question: str
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    api_key: Optional[str] = None  # 前端传入，或从环境变量读取
    model: Optional[str] = None


def get_api_key(request_key: Optional[str]) -> Optional[str]:
    """获取 API Key：优先用请求传入的，其次环境变量"""
    if request_key:
        return request_key
    return os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY')


def build_context_prompt(year: int, month: Optional[int] = None,
                         day: Optional[int] = None) -> str:
    """构建卦象上下文"""
    interpreter = AIInterpreter()
    return interpreter.build_chain_prompt(year, month, day)


def build_chat_messages(question: str, year: int,
                        month: Optional[int] = None,
                        day: Optional[int] = None) -> list:
    """构建对话消息列表"""
    context = build_context_prompt(year, month, day)

    system_msg = """你是一位精通邵雍《皇极经世书》的易学研究者，同时也擅长用通俗易懂的语言向普通人解释卦象含义。

你的回答风格：
- 先给出简明的结论（1-2句话）
- 再展开具体分析
- 用现代人能理解的比喻和例子
- 避免堆砌术语，必要时加括号解释
- 如果用户问的是具体事情（事业、感情等），结合卦象给出实际建议"""

    return [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': f"{context}\n\n---\n\n用户提问：{question}"},
    ]


@router.post("/chat")
async def chat(req: ChatRequest):
    """
    对话接口

    有 API Key 时调用 LLM 返回解读；无 Key 时返回 prompt
    """
    from datetime import datetime

    # 默认使用当前年份
    now = datetime.now()
    year = req.year or now.year
    month = req.month or now.month
    day = req.day or now.day

    api_key = get_api_key(req.api_key)

    if not api_key:
        # 降级模式：返回 prompt 供用户复制
        messages = build_chat_messages(req.question, year, month, day)
        full_prompt = messages[0]['content'] + '\n\n' + messages[1]['content']
        return {
            'mode': 'prompt',
            'message': '未检测到 API Key，已生成推演 prompt，可复制到 ChatGPT/Claude 对话中使用。',
            'prompt': full_prompt,
            'tip': '设置环境变量 ANTHROPIC_API_KEY 或在请求中传入 api_key 即可启用直接对话。',
        }

    # 有 Key，调用 LLM
    model = req.model or 'claude-sonnet-4-6'
    messages = build_chat_messages(req.question, year, month, day)

    # 判断是 Anthropic 还是 OpenAI 格式
    if api_key.startswith('sk-ant-') or 'anthropic' in (req.model or '').lower() or not api_key.startswith('sk-'):
        return await call_anthropic(api_key, model, messages)
    else:
        return await call_openai(api_key, req.model or 'gpt-4o', messages)


async def call_anthropic(api_key: str, model: str, messages: list) -> StreamingResponse:
    """调用 Anthropic Claude API（流式）"""
    import httpx

    system_content = messages[0]['content']
    user_content = messages[1]['content']

    async def generate():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    'POST',
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': model,
                        'max_tokens': 2000,
                        'system': system_content,
                        'messages': [{'role': 'user', 'content': user_content}],
                        'stream': True,
                    },
                    timeout=60.0,
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith('data: '):
                            import json
                            try:
                                data = json.loads(line[6:])
                                if data.get('type') == 'content_block_delta':
                                    text = data.get('delta', {}).get('text', '')
                                    if text:
                                        yield f"data: {json.dumps({'text': text})}\n\n"
                                elif data.get('type') == 'message_stop':
                                    yield "data: [DONE]\n\n"
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                import json
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')


async def call_openai(api_key: str, model: str, messages: list) -> StreamingResponse:
    """调用 OpenAI API（流式）"""
    import httpx

    async def generate():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    'POST',
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                    },
                    json={
                        'model': model,
                        'messages': messages,
                        'stream': True,
                    },
                    timeout=60.0,
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith('data: '):
                            if line.strip() == 'data: [DONE]':
                                yield "data: [DONE]\n\n"
                                break
                            import json
                            try:
                                data = json.loads(line[6:])
                                text = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                if text:
                                    yield f"data: {json.dumps({'text': text})}\n\n"
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                import json
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')


@router.post("/prompt")
def get_prompt(req: ChatRequest):
    """
    仅生成 prompt（不调用 LLM）

    适合用户自行复制到其他 AI 工具中使用
    """
    from datetime import datetime
    now = datetime.now()
    year = req.year or now.year
    month = req.month or now.month
    day = req.day or now.day

    messages = build_chat_messages(req.question, year, month, day)
    full_prompt = messages[0]['content'] + '\n\n' + messages[1]['content']

    return {
        'prompt': full_prompt,
        'year': year,
        'question': req.question,
    }
