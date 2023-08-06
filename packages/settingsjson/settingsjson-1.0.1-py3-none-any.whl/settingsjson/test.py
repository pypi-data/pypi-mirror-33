import unittest
import sys
import os
import settingsjson


class TestSettingsJSON(unittest.TestCase):
    def test_get(self):
        s = settingsjson.get()
        self.assertIn("password", s)
        self.assertEqual("secret", s["password"])

    def test_search_with_basepath(self):
        s = settingsjson.get(basepath="./dir/dir2")
        self.assertIn("password", s)

    def test_search_deep_path(self):
        p = os.getcwd()
        try:
            os.chdir("./dir/dir2")
            s = settingsjson.get()
            self.assertIn("password", s)
        finally:
            os.chdir(p)

    def test_notfound(self):
        filename = "GetSettings.json.json.json"
        try:
            settingsjson.get(filename=filename)
            self.fail()
        except Exception as e:
            self.assertEqual(e.args[0], "not found " + filename)
            pass

    def test_notfound_with_basepath(self):
        filename = "GetSettings.json.json.json"
        basepath = "./dir/dir2"
        try:
            settingsjson.get(basepath=basepath, filename=filename)
            self.fail()
        except Exception as e:
            self.assertEqual(e.args[0], "not found " + filename + " in " + basepath)
            pass


if __name__ == "__main__":
    unittest.main()
