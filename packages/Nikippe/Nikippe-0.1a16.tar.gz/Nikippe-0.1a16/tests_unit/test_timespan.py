import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nikippe.renderer.circularchart import TimeSpan
from datetime import datetime, timedelta


class TestTimeSpan(unittest.TestCase):
    def test_week(self):
        now = datetime(2018, 7, 1, 11, 15, 37, 20)
        first, last = TimeSpan.WEEK(now)
        self.assertLess(now, last)
        self.assertGreaterEqual(now, first)
        self.assertEqual(last-first, timedelta(weeks=1))

    def test_day(self):
        now = datetime(2018, 7, 1, 11, 15, 37, 20)
        first, last = TimeSpan.DAY(now)
        self.assertLess(now, last)
        self.assertGreaterEqual(now, first)
        self.assertEqual(last-first, timedelta(days=1))

    def test_hour(self):
        now = datetime(2018, 7, 1, 11, 15, 37, 20)
        first, last = TimeSpan.HOUR(now)
        self.assertLess(now, last)
        self.assertGreaterEqual(now, first)
        self.assertEqual(last-first, timedelta(hours=1))

    def test_minute(self):
        now = datetime(2018, 7, 1, 11, 15, 37, 20)
        first, last = TimeSpan.MINUTE(now)
        self.assertLess(now, last)
        self.assertGreaterEqual(now, first)
        self.assertEqual(last-first, timedelta(minutes=1))

    def test_get_enum(self):
        self.assertEqual(TimeSpan.WEEK, TimeSpan.get_enum("week"))
        self.assertEqual(TimeSpan.DAY, TimeSpan.get_enum("Day"))
        self.assertEqual(TimeSpan.HOUR, TimeSpan.get_enum("HOUR"))
        self.assertEqual(TimeSpan.MINUTE, TimeSpan.get_enum("MINUTE"))
        with self.assertRaises(ValueError):
            TimeSpan.get_enum("blabla")

if __name__ == '__main__':
    unittest.main()

