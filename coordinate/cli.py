"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    KINDS,
    SHAPES,
    SHAPE_NAMES,
    MAX_COORD,
    MIN_COORD,
    CoordinateError,
    Point,
    generate_problems,
)
from .render import render_grid, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="coordinate",
        description="四象限坐标网格：读点坐标、按坐标连点成图与答案页",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--min", dest="min_coord", type=int, default=-8, help="最小坐标，默认 -8")
    sheet.add_argument("--max", dest="max_coord", type=int, default=8, help="最大坐标，默认 8")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--kinds",
        default=",".join(KINDS),
        help="题型，用逗号分隔：reading（读点）、plotting（连点）",
    )
    sheet.add_argument("--size", type=int, default=320, help="坐标系边长，默认 320")
    sheet.add_argument("--title", default="坐标练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    blank = subparsers.add_parser("grid", help="输出空白四象限坐标系 SVG")
    blank.add_argument("--size", type=int, default=320, help="边长，默认 320")
    blank.add_argument("-o", "--output", default=None, help="输出文件")

    shape = subparsers.add_parser("shape", help="输出已连线的图形 SVG")
    shape.add_argument("name", choices=sorted(SHAPES), help="图形名称")
    shape.add_argument("--size", type=int, default=320, help="边长，默认 320")
    shape.add_argument("-o", "--output", default=None, help="输出文件")

    where = subparsers.add_parser("where", help="判断点所在象限")
    where.add_argument("x", type=int, help="横坐标")
    where.add_argument("y", type=int, help="纵坐标")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_kinds(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise CoordinateError("至少需要一种题型")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "where":
            point = Point(args.x, args.y)
            print("%s 在%s" % (point.label, point.quadrant_name))
            return 0
        if args.command == "grid":
            _write_output(render_grid(size=args.size), args.output)
            return 0
        if args.command == "shape":
            points = SHAPES[args.name]
            _write_output(
                render_grid(points, connect=True, labels=True, size=args.size), args.output
            )
            print("图形：%s（%d 个顶点）" % (SHAPE_NAMES[args.name], len(points)))
            return 0
        problems = generate_problems(
            args.count,
            _parse_kinds(args.kinds),
            args.min_coord,
            args.max_coord,
            args.seed,
        )
        _write_output(
            render_worksheet(problems, args.title, args.answers, args.size), args.output
        )
        return 0
    except CoordinateError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
