"""
中英术语对照表

用于铁板神数断词和卦辞的英文翻译辅助。
高频命理术语的固定翻译，确保一致性。
"""

from __future__ import annotations


# 命理核心术语
TERMS = {
    # 吉凶
    '吉': 'auspicious', '凶': 'inauspicious', '大吉': 'greatly auspicious',
    '平安': 'peace and safety', '无咎': 'no blame', '有悔': 'cause for regret',
    '亨通': 'smooth progress', '顺遂': 'all goes well',

    # 人物关系
    '父': 'father', '母': 'mother', '妻': 'wife', '夫': 'husband',
    '子': 'son', '女': 'daughter', '兄弟': 'brothers', '姐妹': 'sisters',
    '贵人': 'benefactor', '小人': 'petty person',

    # 事业
    '科甲': 'imperial examination success', '登科': 'passing the exam',
    '功名': 'fame and rank', '仕途': 'official career',
    '财运': 'fortune in wealth', '破财': 'loss of wealth',
    '发财': 'gaining wealth', '贫': 'poverty',

    # 健康
    '寿': 'longevity', '疾': 'illness', '灾': 'calamity',
    '丧': 'bereavement', '归西': 'passing away', '夭': 'premature death',

    # 时运
    '流年': 'annual fortune', '大运': 'major cycle',
    '运通': 'fortune flows', '运滞': 'fortune stagnates',
    '转机': 'turning point', '否极泰来': 'after darkness comes light',

    # 自然意象
    '春': 'spring', '夏': 'summer', '秋': 'autumn', '冬': 'winter',
    '花': 'flower', '月': 'moon', '风': 'wind', '雨': 'rain',
    '云': 'cloud', '雪': 'snow', '山': 'mountain', '水': 'water',
    '龙': 'dragon', '虎': 'tiger', '凤': 'phoenix',

    # 卦象
    '乾': 'Heaven/Creative', '坤': 'Earth/Receptive',
    '震': 'Thunder/Arousing', '巽': 'Wind/Gentle',
    '坎': 'Water/Abysmal', '离': 'Fire/Clinging',
    '艮': 'Mountain/Stillness', '兑': 'Lake/Joyous',

    # 干支
    '甲': 'Jia', '乙': 'Yi', '丙': 'Bing', '丁': 'Ding',
    '戊': 'Wu', '己': 'Ji', '庚': 'Geng', '辛': 'Xin',
    '壬': 'Ren', '癸': 'Gui',
    '子': 'Zi', '丑': 'Chou', '寅': 'Yin', '卯': 'Mao',
    '辰': 'Chen', '巳': 'Si', '午': 'Wu', '未': 'Wei',
    '申': 'Shen', '酉': 'You', '戌': 'Xu', '亥': 'Hai',
}

# 铁板断词常见句式翻译模板
VERSE_PATTERNS = {
    '一树残花，有枝复茂': 'A tree of fading blossoms — yet new branches shall flourish again.',
    '童年三四岁，皎皎碧玉枝': 'At three or four years old, bright as a jade branch in moonlight.',
    '时行平稳，微恙不志': 'The times move steadily; minor ailments, nothing to worry about.',
    '安于淡薄，识父母心': 'Content in simplicity, understanding a parent\'s heart.',
    '童未成人，一旦归西': 'The child has not yet grown — alas, departed too soon.',
    '流年交一旬，灾晦未相侵': 'A decade passes in the flow of years; misfortune has not yet come calling.',
    '却空篱落，探春回还': 'The empty fence stands bare — spring ventures forth and returns.',
}


def build_translation_prompt(chinese_text: str, context: str = '') -> str:
    """
    构建用于 LLM 翻译断词的 prompt

    要求：信达雅，保留诗意，不过度解释
    """
    return f"""Translate the following Chinese divination verse into English.

Requirements:
- Preserve the poetic imagery and rhythm
- Be faithful to the meaning (信)
- Be clear and readable (达)
- Be elegant and literary (雅)
- Do NOT add explanations or interpretations
- Keep it concise — one verse, one translation
- Use present tense for timeless truths, future tense for predictions

{f'Context: {context}' if context else ''}

Chinese: {chinese_text}

English translation:"""
