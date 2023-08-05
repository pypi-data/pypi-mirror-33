import unittest
import d4
import sys
import os
import io

class TestMainVersion(unittest.TestCase):
    def test_main_version(self):
        stdout, sys.stdout = sys.stdout, io.StringIO()
        try:
            sys.argv = ["d4", "-v"]
            d4.d4.main()
        except: 
            version_str = sys.stdout.getvalue()
            sys.stdout = stdout
            self.assertRegex(version_str,'^d4 [1-9]?[0-9]+\.[1-9]?[0-9]+\.[1-9]?[0-9]+$')

class TestMainVersionLong(unittest.TestCase):
    def test_main_version_long(self):
        stdout, sys.stdout = sys.stdout, io.StringIO()
        try:
            sys.argv = ["d4", "--version"]
            d4.d4.main()
        except: 
            version_str = sys.stdout.getvalue()
            sys.stdout = stdout
            self.assertRegex(version_str,'^d4 [1-9]?[0-9]+\.[1-9]?[0-9]+\.[1-9]?[0-9]+$')

if __name__ == "__main__":
    unittest.main()
