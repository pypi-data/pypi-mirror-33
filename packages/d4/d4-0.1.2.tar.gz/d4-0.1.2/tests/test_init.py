import unittest
import d4
import shutil
import os

class TestInitProject(unittest.TestCase):
    def test_init_project01(self):
        project_name = "test_project"

        try:
            d4.d4.init_project(project_name)

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
