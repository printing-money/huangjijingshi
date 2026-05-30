# 皇极经世推演系统

基于北宋邵雍《皇极经世书》及黄畿《皇极经世书传》注解，构建的世界发展规律推演算法平台。

## 核心理念

邵雍以"元会运世"四级时间体系统摄宇宙万物的运行规律：

```
1 元 = 12 会 = 360 运 = 4,320 世 = 129,600 年
```

本系统实现完整的九层卦象分形同构推演链：

```
元(乾) → 会(辟卦) → 运(主卦爻变) → 世(运卦爻变) → 十年律卦
                                      ↘ 经卦(60年) → 岁(挨60卦次)
→ 月经(60天) → 旬纬(10天) → 日(挨60卦次) → 时经(2时辰)
```

## 功能模块

- **九层卦象推演**：输入任意时间点，输出完整卦象链
- **周期分析**：阴阳消长、五行生克、卦气升降的周期性规律
- **历史验证**：将历史事件与卦象对应，验证推演规律
- **趋势推演**：基于卦象属性推演未来关键节点
- **模式匹配**：查找历史上相似卦象组合进行对照分析

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 启动 API 服务
python -m src.api.app
```

## API 示例

```bash
# 获取 2024 年完整卦象链
curl http://localhost:8000/api/hexagram/chain/2024

# 获取精确时间的卦象
curl -X POST http://localhost:8000/api/hexagram/datetime \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 6, "day": 15, "hour": 10}'

# 周期分析
curl http://localhost:8000/api/analysis/trend/2024
```

## 参考文献

- 《皇极经世书》- 北宋 邵雍
- 《皇极经世书传》- 元末明初 黄畿
- [皇极经世·卷一上](https://zh.wikisource.org/wiki/皇極經世/卷一上)
- [Chinese Text Project - 皇极经世](https://ctext.org/datawiki.pl?if=en&remap=gb&res=36437)

## 许可证

MIT License
