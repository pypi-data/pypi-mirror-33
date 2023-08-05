import unittest
import d4
import sys
import shutil
import os

class TestMainInit(unittest.TestCase):
    def test_main_init(self):
        project_name = "test_project"
        try:
            sys.argv = ["d4", "init", project_name]
            d4.d4.main()
            self.assertTrue(os.path.isdir(project_name))
            self.assertTrue(os.path.isfile(project_name + "/Dockerfile"))
            self.assertTrue(os.path.isfile(project_name + "/common.yaml"))
            self.assertTrue(os.path.isfile(project_name + "/build.yaml"))
            self.assertTrue(os.path.isdir(project_name + "/tests"))
            self.assertTrue(os.path.isfile(project_name + "/tests/config.yaml"))
        finally:
            shutil.rmtree(project_name)

if __name__ == "__main__":
    unittest.main()
