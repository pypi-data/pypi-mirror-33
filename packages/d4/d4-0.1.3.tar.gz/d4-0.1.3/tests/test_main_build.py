import unittest
import d4
import docker
import os
import shutil
import sys

class TestMainBuild(unittest.TestCase):
    def test_main_build(self):
        client = docker.from_env()
        project_name = "test_project"
        image_name = "test_image:latest"
        registry_server = "index.docker.io"
        try:
            d4.d4.init_project(project_name)
            os.chdir("./" + project_name)
            f = open("common.yaml", "w")
            f.write("image_name: " + image_name + "\n")
            f.write("registry_server: " + registry_server + "\n")
            f.close()
            sys.argv = ["d4", "build"]
            d4.d4.main()
            test_image = client.images.get(image_name)
            self.assertIsNotNone(test_image)
        finally:
            os.chdir("..")
            shutil.rmtree(project_name)
            client.images.remove(image_name)
            client.close()

if __name__ == "__main__":
    unittest.main()
