# coordinate

[![CI](https://github.com/eastyou/coordinate/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/coordinate/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

四象限坐标网格练习：读懂点的坐标，或者按坐标描点连线，画出房子、小鱼和五角星，生成可打印的 A4 练习纸与答案图。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道读点 / 连点混合练习，附答案
coordinate sheet --count 8 --answers -o sheet.html

# 只练读点坐标，坐标限定在 -5–5
coordinate sheet --kinds reading --min -5 --max 5 -o read.html

# 输出空白坐标系
coordinate grid -o grid.svg

# 输出已连线的五角星
coordinate shape star -o star.svg

# 判断点所在象限
coordinate where -3 4
# (-3, 4) 在第二象限
```

## 功能

- -10–10 四象限坐标系，1 格 1 单位，坐标轴与刻度齐全
- 读点题自动标注 A、B、C，连点题给出坐标清单
- 内置房子、小鱼、五角星三种连线图形
- 题目支持随机种子复现
- 输出 A4 打印样式，答案页附带连线后的图形

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
