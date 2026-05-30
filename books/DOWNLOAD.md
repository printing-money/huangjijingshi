# 典籍下载说明

当前服务器外网访问受限，无法直接下载大文件。

## 手动获取方式

### 皇极经世书（原文）
1. **Wikisource**：https://zh.wikisource.org/wiki/皇極經世
   - 卷一上至卷十四，全文可复制
2. **Chinese Text Project**：https://ctext.org （搜索"皇极经世"）
   - 含多个版本和注解
3. **Archive.org**：https://archive.org/details/02092259.cn
   - PDF 扫描版

### 铁板神数
1. **Scribd**：https://www.scribd.com/document/766661253/正統鐵板神數
2. 民间流传版本需自行搜集

### 命理典籍（参考 ref/bazi/README.md 中的链接）
- 三命通会、穷通宝鉴、滴天髓等均有下载链接（访问密码: 2274）

## 获取后放置位置

```
books/
├── raw/                    # 原始文件（PDF/图片，不入git）
│   ├── 皇极经世书.pdf
│   ├── 铁板神数.pdf
│   └── 三命通会.pdf
├── texts/                  # 结构化文本（入git）
│   ├── huangji_guanwu.py  # 观物篇结构化
│   ├── tieban_tiaowen.py  # 铁板条文库
│   └── sanming_rishi.py   # 三命通会日时断
└── README.md              # 本文件
```

将 `books/raw/` 加入 .gitignore（PDF 太大不入库）。
结构化后的 Python 数据文件放 `books/texts/` 或直接放 `src/data/`。
