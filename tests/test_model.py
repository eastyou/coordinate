"""坐标、象限与出题逻辑测试。"""

import unittest
from dataclasses import FrozenInstanceError

from coordinate.model import (
    KINDS,
    MAX_COORD,
    MIN_COORD,
    SHAPES,
    SHAPE_NAMES,
    CoordinateError,
    CoordinateProblem,
    Point,
    check_coord,
    generate_points,
    generate_problems,
    letter,
)


def expected_quadrant(x, y):
    if x == 0 or y == 0:
        return 0
    if x > 0 and y > 0:
        return 1
    if x < 0 and y > 0:
        return 2
    if x < 0 and y < 0:
        return 3
    return 4


class GeneratedQuadrantTest(unittest.TestCase):
    """覆盖四个象限与坐标轴上的代表性点。"""


def _make_quadrant_test(x, y):
    def test(self):
        point = Point(x, y)
        self.assertEqual(point.quadrant, expected_quadrant(x, y))

    test.__doc__ = "点 (%d, %d) 的象限" % (x, y)
    return test


for _x in [-5, -3, -1, 1, 3, 5]:
    for _y in [-5, -3, -1, 0, 1, 3, 5]:
        setattr(
            GeneratedQuadrantTest,
            "test_%d_%d" % (_x, _y),
            _make_quadrant_test(_x, _y),
        )
for _x in (-4, 0, 4):
    setattr(
        GeneratedQuadrantTest,
        "test_axis_%d" % _x,
        _make_quadrant_test(_x, 0),
    )
    setattr(
        GeneratedQuadrantTest,
        "test_vertical_%d" % _x,
        _make_quadrant_test(0, _x),
    )


class CheckCoordTest(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(check_coord(MIN_COORD), MIN_COORD)
        self.assertEqual(check_coord(MAX_COORD), MAX_COORD)

    def test_too_small(self):
        with self.assertRaises(CoordinateError):
            check_coord(-11)

    def test_too_large(self):
        with self.assertRaises(CoordinateError):
            check_coord(11)

    def test_bool(self):
        with self.assertRaises(CoordinateError):
            check_coord(True)

    def test_float(self):
        with self.assertRaises(CoordinateError):
            check_coord(1.5)

    def test_string(self):
        with self.assertRaises(CoordinateError):
            check_coord("3")

    def test_custom_name(self):
        with self.assertRaisesRegex(CoordinateError, "纵坐标"):
            check_coord(20, "纵坐标")


class LetterTest(unittest.TestCase):
    def test_first(self):
        self.assertEqual(letter(0), "A")

    def test_second(self):
        self.assertEqual(letter(1), "B")

    def test_last(self):
        self.assertEqual(letter(25), "Z")

    def test_negative(self):
        with self.assertRaises(CoordinateError):
            letter(-1)

    def test_too_large(self):
        with self.assertRaises(CoordinateError):
            letter(26)

    def test_float(self):
        with self.assertRaises(CoordinateError):
            letter(1.0)


class PointTest(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(Point(3, -2).label, "(3, -2)")
        self.assertEqual(str(Point(-1, 4)), "(-1, 4)")

    def test_quadrant_names(self):
        self.assertEqual(Point(1, 1).quadrant_name, "第一象限")
        self.assertEqual(Point(-1, 1).quadrant_name, "第二象限")
        self.assertEqual(Point(-1, -1).quadrant_name, "第三象限")
        self.assertEqual(Point(1, -1).quadrant_name, "第四象限")
        self.assertEqual(Point(0, 5).quadrant_name, "坐标轴上")

    def test_out_of_range(self):
        with self.assertRaises(CoordinateError):
            Point(11, 0)

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            Point(1, 2).x = 3


class ShapeTest(unittest.TestCase):
    def test_names(self):
        self.assertEqual(set(SHAPES), set(SHAPE_NAMES))

    def test_all_inside_range(self):
        for name, points in SHAPES.items():
            self.assertGreaterEqual(len(points), 3, name)
            for point in points:
                self.assertGreaterEqual(point.x, MIN_COORD)
                self.assertLessEqual(point.x, MAX_COORD)
                self.assertGreaterEqual(point.y, MIN_COORD)
                self.assertLessEqual(point.y, MAX_COORD)

    def test_closed_shapes(self):
        for name, points in SHAPES.items():
            self.assertNotEqual(points[0], points[-1], name)


class ProblemTest(unittest.TestCase):
    def test_single_reading(self):
        problem = CoordinateProblem((Point(3, -2),), "reading")
        self.assertEqual(problem.prompt, "写出点 A 的坐标")
        self.assertEqual(problem.answer, "A(3, -2)")

    def test_multi_reading(self):
        problem = CoordinateProblem((Point(1, 2), Point(-3, 4)), "reading")
        self.assertEqual(problem.letters, ("A", "B"))
        self.assertIn("A、B", problem.prompt)
        self.assertIn("B(-3, 4)", problem.answer)

    def test_plotting(self):
        problem = CoordinateProblem(SHAPES["house"], "plotting", "house")
        self.assertIn("房子", problem.answer)
        self.assertIn("依次连线", problem.prompt)

    def test_empty_points(self):
        with self.assertRaises(CoordinateError):
            CoordinateProblem((), "reading")

    def test_plotting_needs_three(self):
        with self.assertRaises(CoordinateError):
            CoordinateProblem((Point(1, 1), Point(2, 2)), "plotting", "house")

    def test_unknown_shape(self):
        with self.assertRaises(CoordinateError):
            CoordinateProblem(SHAPES["house"], "plotting", "dragon")

    def test_bad_kind(self):
        with self.assertRaises(CoordinateError):
            CoordinateProblem((Point(1, 1),), "guess")

    def test_bad_point_type(self):
        with self.assertRaises(CoordinateError):
            CoordinateProblem(((1, 2),), "reading")


class PointGenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_points(6, seed=1)), 6)

    def test_unique(self):
        points = generate_points(10, seed=2)
        self.assertEqual(len({(p.x, p.y) for p in points}), 10)

    def test_deterministic(self):
        self.assertEqual(generate_points(5, seed=3), generate_points(5, seed=3))

    def test_bounds(self):
        for point in generate_points(10, -2, 2, seed=4):
            self.assertGreaterEqual(point.x, -2)
            self.assertLessEqual(point.x, 2)
            self.assertGreaterEqual(point.y, -2)
            self.assertLessEqual(point.y, 2)

    def test_invalid_count(self):
        for bad in (0, -1, 2.5, True, "5"):
            with self.assertRaises(CoordinateError):
                generate_points(bad)

    def test_too_many(self):
        with self.assertRaises(CoordinateError):
            generate_points(41)

    def test_range_too_small(self):
        with self.assertRaises(CoordinateError):
            generate_points(5, 0, 1)

    def test_bad_range(self):
        with self.assertRaises(CoordinateError):
            generate_points(2, 5, 0)

    def test_out_of_bounds(self):
        with self.assertRaises(CoordinateError):
            generate_points(2, -20, 0)


class ProblemGenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(4, seed=1)), 4)

    def test_deterministic(self):
        self.assertEqual(generate_problems(4, seed=5), generate_problems(4, seed=5))

    def test_reading_only(self):
        for item in generate_problems(5, kinds=("reading",), seed=2):
            self.assertEqual(item.kind, "reading")

    def test_plotting_only(self):
        for item in generate_problems(5, kinds=("plotting",), seed=2):
            self.assertEqual(item.kind, "plotting")
            self.assertIn(item.shape, SHAPES)

    def test_invalid_count(self):
        for bad in (0, -1, True, 2.5):
            with self.assertRaises(CoordinateError):
                generate_problems(bad)

    def test_too_many(self):
        with self.assertRaises(CoordinateError):
            generate_problems(21)

    def test_empty_kinds(self):
        with self.assertRaises(CoordinateError):
            generate_problems(2, kinds=())

    def test_unknown_kind(self):
        with self.assertRaises(CoordinateError):
            generate_problems(2, kinds=("reading", "drawing"))

    def test_all_answers(self):
        for item in generate_problems(6, seed=9):
            self.assertTrue(item.answer)
            self.assertIn(item.kind, KINDS)


if __name__ == "__main__":
    unittest.main()
