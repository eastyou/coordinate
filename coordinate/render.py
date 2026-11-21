"""四象限网格、连线图形与 A4 练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Optional, Sequence

from .model import (
    MAX_COORD,
    MIN_COORD,
    CoordinateError,
    CoordinateProblem,
    Point,
)

_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.prompt { font-size: 13px; margin: 0 0 2mm; color: #323f4b; }
.answer-line { margin-top: 2mm; border-bottom: 1px dashed #9aa5b1; height: 22px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2b6cb0; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
.answer-figures { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 4mm; }
@media print { .sheet { padding: 0; } }
""".strip()


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def _mapper(size: int, low: int, high: int) -> tuple:
    margin = size * 0.08
    span = float(size - 2 * margin)
    scale = span / (high - low)

    def to_px(x: int, y: int) -> tuple:
        px = margin + (x - low) * scale
        py = margin + (high - y) * scale
        return px, py

    return to_px, margin, scale


def render_grid(
    points: Sequence[Point] = (),
    connect: bool = False,
    labels: bool = True,
    size: int = 320,
    low: int = MIN_COORD,
    high: int = MAX_COORD,
) -> str:
    """绘制带网格与坐标轴的四象限坐标系。"""
    if isinstance(size, bool) or not isinstance(size, int) or size < 200:
        raise CoordinateError("坐标系尺寸必须是至少 200 的整数")
    if low < MIN_COORD or high > MAX_COORD or low >= high:
        raise CoordinateError("坐标范围必须在 -10–10 且 low < high")
    for point in points:
        if not isinstance(point, Point):
            raise CoordinateError("点必须是 Point")
        if point.x < low or point.x > high or point.y < low or point.y > high:
            raise CoordinateError("点 %s 超出坐标范围" % point.label)

    to_px, margin, scale = _mapper(size, low, high)
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="坐标系">' % (size, size, size, size),
        "<title>四象限坐标系</title>",
    ]

    # 网格
    grid_lines: List[str] = ['<g stroke="#dde3ea" stroke-width="0.6">']
    for value in range(low, high + 1):
        x1, y1 = to_px(value, low)
        x2, y2 = to_px(value, high)
        grid_lines.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (_fmt(x1), _fmt(y1), _fmt(x2), _fmt(y2))
        )
        x1, y1 = to_px(low, value)
        x2, y2 = to_px(high, value)
        grid_lines.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (_fmt(x1), _fmt(y1), _fmt(x2), _fmt(y2))
        )
    grid_lines.append("</g>")
    parts.extend(grid_lines)

    # 坐标轴
    x0, y0 = to_px(0, 0)
    x_left, _ = to_px(low, 0)
    x_right, _ = to_px(high, 0)
    _, y_top = to_px(0, high)
    _, y_bottom = to_px(0, low)
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#323f4b" stroke-width="1.6"/>'
        % (_fmt(x_left), _fmt(y0), _fmt(x_right), _fmt(y0))
    )
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#323f4b" stroke-width="1.6"/>'
        % (_fmt(x0), _fmt(y_bottom), _fmt(x0), _fmt(y_top))
    )

    # 轴刻度数字
    ticks: List[str] = ['<g font-size="%s" fill="#52606d">' % _fmt(max(7.0, size * 0.028))]
    for value in range(low, high + 1, 2 if high - low > 12 else 1):
        if value == 0:
            continue
        px, _ = to_px(value, 0)
        ticks.append(
            '<text x="%s" y="%s" text-anchor="middle">%d</text>'
            % (_fmt(px), _fmt(y0 + size * 0.045), value)
        )
        _, py = to_px(0, value)
        ticks.append(
            '<text x="%s" y="%s" text-anchor="end">%d</text>'
            % (_fmt(x0 - size * 0.02), _fmt(py + size * 0.012), value)
        )
    ticks.append(
        '<text x="%s" y="%s" text-anchor="end">O</text>'
        % (_fmt(x0 - size * 0.02), _fmt(y0 + size * 0.045))
    )
    ticks.append("</g>")
    parts.extend(ticks)

    # 连线
    if connect and len(points) >= 2:
        coords = " ".join(
            "%s,%s" % tuple(_fmt(value) for value in to_px(point.x, point.y))
            for point in points
        )
        parts.append(
            '<polygon points="%s" fill="#2b6cb0" fill-opacity="0.12" '
            'stroke="#2b6cb0" stroke-width="2"/>' % coords
        )

    # 点与字母
    for index, point in enumerate(points):
        px, py = to_px(point.x, point.y)
        parts.append(
            '<circle cx="%s" cy="%s" r="%s" fill="#b02a37"/>'
            % (_fmt(px), _fmt(py), _fmt(max(2.4, size * 0.009)))
        )
        if labels:
            parts.append(
                '<text x="%s" y="%s" font-size="%s" fill="#b02a37" font-weight="bold">%s</text>'
                % (
                    _fmt(px + size * 0.014),
                    _fmt(py - size * 0.014),
                    _fmt(max(9.0, size * 0.038)),
                    chr(ord("A") + index),
                )
            )

    parts.append("</svg>")
    return "\n".join(parts)


def render_worksheet(
    problems: Sequence[CoordinateProblem],
    title: str = "坐标练习",
    answers: bool = False,
    size: int = 320,
) -> str:
    """生成可打印的坐标练习纸。"""
    items = list(problems)
    if not items:
        raise CoordinateError("至少需要一道题")
    for item in items:
        if not isinstance(item, CoordinateProblem):
            raise CoordinateError("题目必须是 CoordinateProblem")

    cards: List[str] = []
    for index, item in enumerate(items, 1):
        if item.kind == "reading":
            figure = render_grid(item.points, connect=False, labels=True, size=size)
        else:
            figure = render_grid((), connect=False, labels=False, size=size)
        cards.append(
            '<div class="card">\n<p class="prompt">%d. %s</p>\n%s\n'
            '<div class="answer-line"></div>\n</div>'
            % (index, html.escape(item.prompt), figure)
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="grid">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        figures = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), html.escape(item.answer))
            )
            if item.kind == "plotting":
                figures.append(
                    '<div class="card">%s%s</div>'
                    % (
                        '<p class="prompt">%d. %s</p>' % (index, html.escape(item.answer)),
                        render_grid(item.points, connect=True, labels=True, size=size),
                    )
                )
        extra = ""
        if figures:
            extra = '<div class="answer-figures">%s</div>' % "\n".join(figures)
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table>%s</section>" % ("\n".join(rows), extra)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)
