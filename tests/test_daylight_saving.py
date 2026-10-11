"""Tests for daylight saving time handling."""

import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class TestDaylightSaving(unittest.TestCase):

    def test_winter_and_summer_time(self):
        cases = [
            ("America/New_York", "EST", -5, "EDT", -4),
            ("Europe/London", "GMT", 0, "BST", 1),
            ("Europe/Berlin", "CET", 1, "CEST", 2),
        ]

        for zone, winter_name, winter_offset, summer_name, summer_offset in cases:
            with self.subTest(zone=zone):
                tz = ZoneInfo(zone)

                winter = datetime(2026, 1, 15, 12, 0, tzinfo=tz)
                summer = datetime(2026, 7, 15, 12, 0, tzinfo=tz)

                self.assertEqual(winter.tzname(), winter_name)
                self.assertEqual(summer.tzname(), summer_name)

                self.assertEqual(
                    winter.utcoffset(),
                    timedelta(hours=winter_offset),
                )
                self.assertEqual(
                    summer.utcoffset(),
                    timedelta(hours=summer_offset),
                )


if __name__ == "__main__":
    unittest.main()
