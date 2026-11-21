"""坐标系与练习纸渲染测试。"""

import unittest

from coordinate.model import SHAPES, CoordinateError, CoordinateProblem, Point
from coordinate.render import render_grid, render_worksheet


class GridTest(unittest.TestCase):
    def test_root(self):
        svg = render_grid()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("四象限坐标系", svg)

    def test_grid_lines(self):
        svg = render_grid()
        self.assertEqual(svg.count("<line"), 44)

    def test_axis_labels(self):
        svg = render_grid()
        self.assertIn(">O</text>", svg)
        self.assertIn(">10</text>", svg)
        self.assertIn(">-10</text>", svg)

    def test_points(self):
        svg = render_grid((Point(3, 4), Point(-2, -5)))
        self.assertEqual(svg.count("<circle"), 2)

    def test_point_labels(self):
        svg = render_grid((Point(3, 4), Point(-2, -5)))
        self.assertIn(">A</text>", svg)
        self.assertIn(">B</text>", svg)

    def test_labels_off(self):
        svg = render_grid((Point(3, 4),), labels=False)
        self.assertNotIn(">A</text>", svg)

    def test_connect(self):
        svg = render_grid(SHAPES["house"], connect=True)
        self.assertIn("<polygon", svg)

    def test_no_connect(self):
        svg = render_grid(SHAPES["house"], connect=False)
        self.assertNotIn("<polygon", svg)

    def test_custom_range(self):
        svg = render_grid(low=-5, high=5)
        self.assertIn("<title>四象限坐标系</title>", svg)

    def test_custom_size(self):
        svg = render_grid(size=400)
        self.assertIn('width="400"', svg)

    def test_invalid_size(self):
        with self.assertRaises(CoordinateError):
            render_grid(size=100)

    def test_invalid_range(self):
        with self.assertRaises(CoordinateError):
            render_grid(low=5, high=5)

    def test_range_beyond_limit(self):
        with self.assertRaises(CoordinateError):
            render_grid(low=-20, high=5)

    def test_point_out_of_range(self):
        with self.assertRaises(CoordinateError):
            render_grid((Point(9, 9),), low=-5, high=5)

    def test_bad_point(self):
        with self.assertRaises(CoordinateError):
            render_grid((("3", "4"),))


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.problems = [
            CoordinateProblem((Point(3, -2), Point(-4, 1)), "reading"),
            CoordinateProblem(SHAPES["house"], "plotting", "house"),
            CoordinateProblem((Point(0, 5),), "reading"),
        ]

    def test_document(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("坐标练习", page)
        self.assertTrue(page.endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 3)

    def test_answers(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertIn("连线后是房子", page)

    def test_answer_figure(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("answer-figures", page)
        self.assertIn("<polygon", page)

    def test_no_answers(self):
        page = render_worksheet(self.problems)
        self.assertNotIn("参考答案", page)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="平面直角坐标系")
        self.assertIn("<title>平面直角坐标系</title>", page)

    def test_custom_size(self):
        page = render_worksheet(self.problems, size=280)
        self.assertIn('width="280"', page)

    def test_empty(self):
        with self.assertRaises(CoordinateError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(CoordinateError):
            render_worksheet([("A", "reading")])

    def test_escaping(self):
        page = render_worksheet(self.problems, title="<b>坐标</b>")
        self.assertNotIn("<b>坐标</b>", page)
        self.assertIn("&lt;b&gt;", page)


if __name__ == "__main__":
    unittest.main()
