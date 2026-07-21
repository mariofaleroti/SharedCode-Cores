from __future__ import annotations

import re
import unittest
from datetime import datetime, timezone

from date_time_core import (
    datetime_to_run_id_timestamp,
    datetime_to_utc_iso,
    format_iso_for_log,
    parse_iso_datetime,
    timestamp_seconds_to_utc_iso,
)


class DateTimeCoreBehaviorTests(unittest.TestCase):
    def test_datetime_to_utc_iso_uses_z_without_microseconds(self) -> None:
        value = datetime(2026, 6, 30, 15, 4, 5, 123456, tzinfo=timezone.utc)

        self.assertEqual(datetime_to_utc_iso(value), "2026-06-30T15:04:05Z")

    def test_naive_datetime_is_treated_as_utc(self) -> None:
        value = datetime(2026, 6, 30, 15, 4, 5)

        self.assertEqual(datetime_to_utc_iso(value), "2026-06-30T15:04:05Z")

    def test_parse_accepts_z_and_plus_zero_utc(self) -> None:
        z_value = parse_iso_datetime("2026-06-30T15:04:05Z")
        offset_value = parse_iso_datetime("2026-06-30T15:04:05+00:00")

        self.assertEqual(z_value, offset_value)

    def test_timestamp_seconds_to_utc_iso_is_explicit(self) -> None:
        value = datetime(2026, 6, 30, 15, 4, 5, tzinfo=timezone.utc).timestamp()

        self.assertEqual(timestamp_seconds_to_utc_iso(value), "2026-06-30T15:04:05Z")

    def test_datetime_to_run_id_timestamp_is_stable(self) -> None:
        value = datetime(2026, 6, 30, 15, 4, 5, tzinfo=timezone.utc)

        self.assertEqual(datetime_to_run_id_timestamp(value), "20260630_150405")

    def test_format_iso_for_log_keeps_readable_order(self) -> None:
        self.assertEqual(
            format_iso_for_log("2026-06-30T12:04:05-03:00"),
            "2026-06-30 12:04:05 -03:00",
        )

    def test_utc_now_shape_is_consistent(self) -> None:
        self.assertRegex(datetime_to_utc_iso(datetime.now(timezone.utc)), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


if __name__ == "__main__":
    unittest.main()
