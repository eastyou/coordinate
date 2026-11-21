"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from coordinate.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_where_first(self):
        code, out, _ = run(["where", "3", "4"])
        self.assertEqual(code, 0)
        self.assertIn("第一象限", out)

    def test_where_axis(self):
        code, out, _ = run(["where", "0", "4"])
        self.assertEqual(code, 0)
        self.assertIn("坐标轴上", out)

    def test_where_invalid(self):
        code, _, err = run(["where", "20", "4"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_grid_stdout(self):
        code, out, _ = run(["grid"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)

    def test_grid_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "grid.svg"
            code, out, _ = run(["grid", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_shape_stdout(self):
        code, out, _ = run(["shape", "house"])
        self.assertEqual(code, 0)
        self.assertIn("<polygon", out)
        self.assertIn("房子", out)

    def test_shape_invalid(self):
        with self.assertRaises(SystemExit):
            main(["shape", "dragon"])

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_bad_kind(self):
        code, _, err = run(["sheet", "--kinds", "reading,drawing"])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_sheet_empty_kind(self):
        code, _, err = run(["sheet", "--kinds", " , "])
        self.assertEqual(code, 2)
        self.assertIn("题型", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
