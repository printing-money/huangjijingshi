"""
世界历史事件数据库

覆盖中国史 + 世界史重大事件，用于卦象关联验证和模式匹配。
按时间线组织，标注事件类型、影响范围和重要性。
"""

from __future__ import annotations

from ..analysis.history_validator import HistoryEvent, EventType


# 世界史重大事件（补充中国史之外的全球事件）
WORLD_HISTORY_EVENTS: list = [
    # === 古代文明 ===
    HistoryEvent(-3100, "古埃及统一", EventType.FOUNDING, "美尼斯统一上下埃及", 8),
    HistoryEvent(-2600, "金字塔建造", EventType.CULTURAL, "吉萨大金字塔", 7),
    HistoryEvent(-1792, "汉谟拉比法典", EventType.REFORM, "巴比伦法典", 8),
    HistoryEvent(-1200, "特洛伊战争", EventType.WAR, "希腊联军攻特洛伊", 6),
    HistoryEvent(-776, "首届奥运会", EventType.CULTURAL, "古希腊奥林匹亚", 6),
    HistoryEvent(-509, "罗马共和国", EventType.FOUNDING, "推翻王政建立共和", 8),
    HistoryEvent(-490, "马拉松战役", EventType.WAR, "希波战争转折", 7),
    HistoryEvent(-336, "亚历山大即位", EventType.FOUNDING, "马其顿帝国扩张", 8),
    HistoryEvent(-264, "布匿战争", EventType.WAR, "罗马与迦太基", 7),
    HistoryEvent(-27, "罗马帝国建立", EventType.FOUNDING, "屋大维称帝", 9),

    # === 中世纪 ===
    HistoryEvent(476, "西罗马灭亡", EventType.COLLAPSE, "日耳曼人攻陷罗马", 9),
    HistoryEvent(622, "伊斯兰教创立", EventType.CULTURAL, "穆罕默德迁徙", 9),
    HistoryEvent(800, "查理曼加冕", EventType.FOUNDING, "神圣罗马帝国前身", 7),
    HistoryEvent(1066, "诺曼征服", EventType.WAR, "威廉征服英格兰", 7),
    HistoryEvent(1096, "第一次十字军", EventType.WAR, "东征耶路撒冷", 7),
    HistoryEvent(1215, "大宪章", EventType.REFORM, "英国限制王权", 8),
    HistoryEvent(1347, "黑死病", EventType.DISASTER, "欧洲大瘟疫", 9),
    HistoryEvent(1453, "君士坦丁堡陷落", EventType.COLLAPSE, "东罗马帝国灭亡", 8),

    # === 近代 ===
    HistoryEvent(1492, "哥伦布发现新大陆", EventType.CULTURAL, "大航海时代", 10),
    HistoryEvent(1517, "宗教改革", EventType.REFORM, "马丁路德九十五条", 8),
    HistoryEvent(1588, "无敌舰队覆灭", EventType.WAR, "英国崛起", 7),
    HistoryEvent(1642, "英国内战", EventType.WAR, "议会与王权之争", 7),
    HistoryEvent(1687, "牛顿力学", EventType.TECHNOLOGY, "自然哲学的数学原理", 9),
    HistoryEvent(1776, "美国独立", EventType.FOUNDING, "独立宣言", 10),
    HistoryEvent(1789, "法国大革命", EventType.DYNASTY_CHANGE, "攻占巴士底狱", 10),
    HistoryEvent(1804, "拿破仑称帝", EventType.FOUNDING, "法兰西第一帝国", 8),
    HistoryEvent(1815, "滑铁卢战役", EventType.WAR, "拿破仑最终失败", 8),
    HistoryEvent(1848, "共产党宣言", EventType.CULTURAL, "马克思恩格斯", 8),
    HistoryEvent(1861, "美国内战", EventType.WAR, "南北战争", 8),
    HistoryEvent(1868, "明治维新", EventType.REFORM, "日本近代化", 8),
    HistoryEvent(1869, "苏伊士运河", EventType.TECHNOLOGY, "连通地中海与红海", 6),

    # === 现代 ===
    HistoryEvent(1903, "莱特兄弟飞行", EventType.TECHNOLOGY, "人类首次动力飞行", 7),
    HistoryEvent(1914, "一战爆发", EventType.WAR, "萨拉热窝事件", 10),
    HistoryEvent(1917, "俄国革命", EventType.DYNASTY_CHANGE, "十月革命", 10),
    HistoryEvent(1918, "一战结束", EventType.WAR, "德国投降", 9),
    HistoryEvent(1929, "大萧条", EventType.DISASTER, "华尔街崩盘", 9),
    HistoryEvent(1939, "二战爆发", EventType.WAR, "德国入侵波兰", 10),
    HistoryEvent(1945, "二战结束", EventType.WAR, "原子弹与日本投降", 10),
    HistoryEvent(1947, "印度独立", EventType.FOUNDING, "印巴分治", 8),
    HistoryEvent(1948, "以色列建国", EventType.FOUNDING, "中东格局改变", 8),
    HistoryEvent(1957, "人造卫星", EventType.TECHNOLOGY, "苏联发射Sputnik", 8),
    HistoryEvent(1961, "柏林墙", EventType.WAR, "冷战象征", 7),
    HistoryEvent(1969, "登月", EventType.TECHNOLOGY, "阿波罗11号", 9),
    HistoryEvent(1979, "伊朗革命", EventType.DYNASTY_CHANGE, "伊斯兰共和国", 7),
    HistoryEvent(1989, "柏林墙倒塌", EventType.REFORM, "冷战结束标志", 9),
    HistoryEvent(1991, "苏联解体", EventType.COLLAPSE, "冷战结束", 10),
    HistoryEvent(2001, "911事件", EventType.DISASTER, "恐怖袭击", 9),
    HistoryEvent(2008, "金融危机", EventType.DISASTER, "全球经济衰退", 8),
    HistoryEvent(2020, "新冠大流行", EventType.DISASTER, "COVID-19全球蔓延", 9),
    HistoryEvent(2022, "俄乌冲突", EventType.WAR, "地缘政治剧变", 8),
]

# 中国史补充事件（填充更多细节）
CHINA_HISTORY_SUPPLEMENT: list = [
    # 先秦补充
    HistoryEvent(-841, "共和行政", EventType.REFORM, "中国有确切纪年之始", 7),
    HistoryEvent(-356, "商鞅变法", EventType.REFORM, "秦国崛起之基", 8),
    HistoryEvent(-260, "长平之战", EventType.WAR, "秦赵决战", 7),
    HistoryEvent(-209, "陈胜吴广起义", EventType.WAR, "秦末农民起义", 7),

    # 汉代补充
    HistoryEvent(-138, "张骞出使西域", EventType.CULTURAL, "丝绸之路开辟", 8),
    HistoryEvent(-104, "太初历", EventType.TECHNOLOGY, "司马迁修史记", 7),
    HistoryEvent(105, "蔡伦造纸", EventType.TECHNOLOGY, "四大发明之一", 8),
    HistoryEvent(184, "黄巾起义", EventType.WAR, "东汉末年动乱", 7),

    # 唐宋补充
    HistoryEvent(605, "大运河", EventType.TECHNOLOGY, "隋炀帝开凿", 7),
    HistoryEvent(690, "武则天称帝", EventType.DYNASTY_CHANGE, "中国唯一女皇帝", 8),
    HistoryEvent(868, "金刚经印刷", EventType.TECHNOLOGY, "现存最早印刷品", 6),
    HistoryEvent(1004, "澶渊之盟", EventType.WAR, "宋辽和议", 6),
    HistoryEvent(1044, "火药配方", EventType.TECHNOLOGY, "武经总要记载", 7),

    # 明清补充
    HistoryEvent(1449, "土木堡之变", EventType.WAR, "明英宗被俘", 7),
    HistoryEvent(1557, "葡据澳门", EventType.CULTURAL, "西方势力进入", 6),
    HistoryEvent(1662, "郑成功收复台湾", EventType.WAR, "驱逐荷兰殖民者", 7),
    HistoryEvent(1689, "尼布楚条约", EventType.REFORM, "中俄首个边界条约", 6),
    HistoryEvent(1793, "马戛尔尼使团", EventType.CULTURAL, "中英首次官方接触", 6),
    HistoryEvent(1860, "火烧圆明园", EventType.WAR, "英法联军", 8),
    HistoryEvent(1894, "甲午战争", EventType.WAR, "中日海战", 9),
    HistoryEvent(1900, "庚子国变", EventType.WAR, "八国联军侵华", 8),

    # 现代补充
    HistoryEvent(1919, "五四运动", EventType.REFORM, "新文化运动高潮", 8),
    HistoryEvent(1921, "中共成立", EventType.FOUNDING, "中国共产党建立", 9),
    HistoryEvent(1927, "南昌起义", EventType.WAR, "武装斗争开始", 7),
    HistoryEvent(1934, "长征", EventType.WAR, "红军战略转移", 8),
    HistoryEvent(1950, "抗美援朝", EventType.WAR, "朝鲜战争", 8),
    HistoryEvent(1964, "原子弹试爆", EventType.TECHNOLOGY, "中国核武器", 8),
    HistoryEvent(1971, "恢复联合国席位", EventType.REFORM, "重返国际舞台", 7),
    HistoryEvent(1997, "香港回归", EventType.REFORM, "一国两制实践", 7),
    HistoryEvent(2003, "载人航天", EventType.TECHNOLOGY, "神舟五号", 7),
    HistoryEvent(2010, "GDP世界第二", EventType.PROSPERITY, "经济总量超日本", 7),
    HistoryEvent(2015, "亚投行成立", EventType.REFORM, "国际金融新秩序", 6),
]


def get_all_events() -> list:
    """获取完整的历史事件数据库"""
    from ..analysis.history_validator import HISTORY_EVENTS
    all_events = list(HISTORY_EVENTS) + WORLD_HISTORY_EVENTS + CHINA_HISTORY_SUPPLEMENT
    all_events.sort(key=lambda e: e.year)
    return all_events
