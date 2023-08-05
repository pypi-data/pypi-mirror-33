import unittest
import d4

class TestVersion(unittest.TestCase):
    def test_version(self):
        version = d4.d4.get_version()
        self.assertRegex(version,'^[1-9]?[0-9]+\.[1-9]?[0-9]+\.[1-9]?[0-9]+$')

if __name__ == "__main__":
    unittest.main()
