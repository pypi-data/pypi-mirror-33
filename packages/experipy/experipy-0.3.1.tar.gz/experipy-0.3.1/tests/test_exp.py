import os
import shutil
import unittest

from experipy.exp       import Exp, Experiment
from experipy.grammar   import Executable

class TestExperimentInternals(unittest.TestCase):
    def test_make_runscript(self):
        exp = Experiment(Executable("hostname"))
        script = exp.make_runscript()
        self.assertIn(Exp.shebang, script)
        self.assertIn("mkdir", script)
        self.assertIn("hostname", script)
        self.assertIn("rm", script)

class TestExperimentRun(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree("results")

    def test_simple_run(self):
        exp = Experiment(
            Executable("echo", ["Hello", "> test.out"], outputs=["test.out"]),
            destdir="results"
        ).run()
        self.assertTrue(os.path.exists("results"))
        self.assertTrue(os.path.exists("results/run.sh"))
        self.assertTrue(os.path.exists("results/test.out"))
        self.assertTrue(os.path.exists(os.path.join("results", Exp.timing)))
