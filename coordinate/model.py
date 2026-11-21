"""四象限坐标：点、象限、连点图形与出题。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

MIN_COORD = -10
MAX_COORD = 10
KINDS: Tuple[str, ...] = ("reading", "plotting")


class CoordinateError(ValueError):
    """坐标相关的输入错误。"""


def check_coord(value: Any, name: str = "坐标") -> int:
    """校验坐标是 -10–10 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise CoordinateError("%s必须是整数" % name)
    if value < MIN_COORD or value > MAX_COORD:
        raise CoordinateError(
            "%s必须在 %d–%d 之间：%d" % (name, MIN_COORD, MAX_COORD, value)
        )
    return value


def letter(index: int) -> str:
    """把 0、1、2… 映射为 A、B、C…"""
    if isinstance(index, bool) or not isinstance(index, int):
        raise CoordinateError("点序号必须是整数")
    if index < 0 or index > 25:
        raise CoordinateError("点序号必须在 0–25 之间：%d" % index)
    return chr(ord("A") + index)


@dataclass(frozen=True)
class Point:
    """平面直角坐标系中的一个点。"""

    x: int
    y: int

    def __post_init__(self) -> None:
        check_coord(self.x, "横坐标")
        check_coord(self.y, "纵坐标")

    @property
    def quadrant(self) -> int:
        """返回 1–4，坐标轴上返回 0。"""
        if self.x == 0 or self.y == 0:
            return 0
        if self.x > 0 and self.y > 0:
            return 1
        if self.x < 0 and self.y > 0:
            return 2
        if self.x < 0 and self.y < 0:
            return 3
        return 4

    @property
    def quadrant_name(self) -> str:
        if self.quadrant == 0:
            return "坐标轴上"
        return "第%s象限" % ("一二三四"[self.quadrant - 1])

    @property
    def label(self) -> str:
        return "(%d, %d)" % (self.x, self.y)

    def __str__(self) -> str:
        return self.label


SHAPE_NAMES: Dict[str, str] = {
    "house": "房子",
    "fish": "小鱼",
    "star": "五角星",
}


def _shape(coords: Sequence[Tuple[int, int]]) -> Tuple[Point, ...]:
    return tuple(Point(x, y) for x, y in coords)


SHAPES: Dict[str, Tuple[Point, ...]] = {
    "house": _shape(((-4, -5), (4, -5), (4, 2), (0, 6), (-4, 2))),
    "fish": _shape(((-6, 0), (-3, 3), (3, 3), (6, 0), (3, -3), (-3, -3))),
    "star": _shape(
        (
            (0, 8),
            (2, 3),
            (7, 3),
            (3, -1),
            (5, -6),
            (0, -3),
            (-5, -6),
            (-3, -1),
            (-7, 3),
            (-2, 3),
        )
    ),
}


@dataclass(frozen=True)
class CoordinateProblem:
    """一道读点坐标题或连点成图题。"""

    points: Tuple[Point, ...]
    kind: str
    shape: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.points, tuple) or not self.points:
            raise CoordinateError("题目至少需要一个点")
        for point in self.points:
            if not isinstance(point, Point):
                raise CoordinateError("点必须是 Point")
        if self.kind not in KINDS:
            raise CoordinateError("未知题型：%s" % self.kind)
        if self.kind == "plotting":
            if len(self.points) < 3:
                raise CoordinateError("连点成图至少需要 3 个点")
            if self.shape not in SHAPE_NAMES:
                raise CoordinateError("未知图形：%s" % self.shape)

    @property
    def letters(self) -> Tuple[str, ...]:
        return tuple(letter(index) for index in range(len(self.points)))

    @property
    def prompt(self) -> str:
        if self.kind == "reading":
            if len(self.points) == 1:
                return "写出点 A 的坐标"
            return "写出 %s 各点的坐标" % "、".join(self.letters)
        pairs = "，".join(
            "%s%s" % (name, point.label) for name, point in zip(self.letters, self.points)
        )
        return "在坐标系中描出 %s，并依次连线，看看是什么图形" % pairs

    @property
    def answer(self) -> str:
        if self.kind == "reading":
            return "；".join(
                "%s%s" % (name, point.label)
                for name, point in zip(self.letters, self.points)
            )
        return "连线后是%s" % SHAPE_NAMES[self.shape]


def generate_points(
    count: int = 4,
    min_coord: int = -8,
    max_coord: int = 8,
    seed: Optional[int] = None,
) -> List[Point]:
    """生成不重复的点。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise CoordinateError("点的数量必须是正整数")
    if count > 40:
        raise CoordinateError("点的数量不能超过 40")
    check_coord(min_coord, "最小坐标")
    check_coord(max_coord, "最大坐标")
    if min_coord > max_coord:
        raise CoordinateError("最小坐标不能大于最大坐标")
    span = max_coord - min_coord + 1
    if count > span * span:
        raise CoordinateError("该范围内最多只有 %d 个点" % (span * span))
    rng = random.Random(seed)
    seen = set()
    result: List[Point] = []
    while len(result) < count:
        x = rng.randint(min_coord, max_coord)
        y = rng.randint(min_coord, max_coord)
        if (x, y) in seen:
            continue
        seen.add((x, y))
        result.append(Point(x, y))
    return result


def generate_problems(
    count: int = 8,
    kinds: Sequence[str] = KINDS,
    min_coord: int = -8,
    max_coord: int = 8,
    seed: Optional[int] = None,
) -> List[CoordinateProblem]:
    """生成读点题与连点成图题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise CoordinateError("题目数量必须是正整数")
    if count > 20:
        raise CoordinateError("题目数量不能超过 20")
    chosen = tuple(kinds)
    if not chosen:
        raise CoordinateError("至少需要一种题型")
    for kind in chosen:
        if kind not in KINDS:
            raise CoordinateError("未知题型：%s" % kind)
    if "plotting" in chosen and not SHAPES:
        raise CoordinateError("没有可用的连点图形")

    rng = random.Random(seed)
    points = generate_points(count * 3, min_coord, max_coord, seed)
    result: List[CoordinateProblem] = []
    cursor = 0
    for index in range(count):
        kind = rng.choice(chosen)
        if kind == "reading":
            how_many = rng.choice((1, 2, 3))
            selected = tuple(points[(cursor + step) % len(points)] for step in range(how_many))
            cursor += how_many
            result.append(CoordinateProblem(selected, "reading"))
        else:
            shape = rng.choice(sorted(SHAPES))
            result.append(CoordinateProblem(SHAPES[shape], "plotting", shape))
    return result
