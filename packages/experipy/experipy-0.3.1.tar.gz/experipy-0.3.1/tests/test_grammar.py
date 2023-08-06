import unittest

from experipy.grammar import Executable, Wrapper, Pipeline, Group

class TestExecutable(unittest.TestCase):
    def test_render(self):
        exe = Executable("cat", ["1.txt", "2.txt"])
        self.assertEqual(str(exe), "cat 1.txt 2.txt")

    def test_output(self):
        exe = Executable("echo", 
            ['"Hello World"', "> test.txt"], 
            outputs=["test.txt"]
        )
        self.assertEqual(list(exe.outputs()),["test.txt"])

    def test_wait(self):
        exe = Executable("ping", wait=False)
        self.assertEqual(str(exe), "ping &")


class TestWrapper(unittest.TestCase):
    def test_render(self):
        exe = Executable("ls", ["-l"])
        wrap = Wrapper("valgrind", ["-v", "[[wrapped]]"], exe)
        self.assertEqual(str(wrap), "valgrind -v ls -l")

    def test_bad_opts_params(self):
        with self.assertRaises(ValueError):
            wrap = Wrapper("valgrind", ["-v"], Executable("ls"))

    def test_bad_wrapped(self):
        with self.assertRaises(TypeError):
            wrap = Wrapper("valgrind", ["-v", "[[wrapped]]"], dict())

    def test_inputs(self):
        exe = Executable("test", inputs=["1.txt", "3.txt"])
        wrap = Wrapper("wrap", ["--","[[wrapped]]"], exe, inputs=["2.txt","3.txt"])
        self.assertEqual(sorted(list(wrap.inputs())), ["1.txt", "2.txt", "3.txt"])
