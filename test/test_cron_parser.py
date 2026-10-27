import unittest

from app.parser import parse_cron


class ParseCronTests(unittest.TestCase):
    def test_expands_sample_expression(self):
        self.assertEqual(
            parse_cron("*/15 0 1,15 * 1-5 /usr/bin/find"),
            [
                ("minute", "0 15 30 45"),
                ("hour", "0"),
                ("day of month", "1 15"),
                ("month", "1 2 3 4 5 6 7 8 9 10 11 12"),
                ("day of week", "1 2 3 4 5"),
                ("command", "/usr/bin/find"),
            ],
        )

    def test_expands_full_wildcards(self):
        rows = parse_cron("* * * * * /bin/echo hello")

        self.assertEqual(rows[0], ("minute", " ".join(map(str, range(60)))))
        self.assertEqual(rows[1], ("hour", " ".join(map(str, range(24)))))
        self.assertEqual(rows[2], ("day of month", " ".join(map(str, range(1, 32)))))
        self.assertEqual(rows[3], ("month", " ".join(map(str, range(1, 13)))))
        self.assertEqual(rows[4], ("day of week", "0 1 2 3 4 5 6"))

    def test_expands_comma_separated_values(self):
        rows = parse_cron("1,5,10 0 1,15 * 1,3 /bin/true")

        self.assertEqual(rows[0], ("minute", "1 5 10"))
        self.assertEqual(rows[2], ("day of month", "1 15"))
        self.assertEqual(rows[4], ("day of week", "1 3"))

    def test_expands_range(self):
        rows = parse_cron("0 9-12 * * 1-5 /bin/true")

        self.assertEqual(rows[1], ("hour", "9 10 11 12"))
        self.assertEqual(rows[4], ("day of week", "1 2 3 4 5"))

    def test_expands_steps(self):
        rows = parse_cron("5/20 0-10/5 * * * /bin/true")

        self.assertEqual(rows[0], ("minute", "5 25 45"))
        self.assertEqual(rows[1], ("hour", "0 5 10"))

    def test_expands_month_and_weekday_names(self):
        rows = parse_cron("0 0 * JAN,MAR MON-FRI /bin/true")

        self.assertEqual(rows[3], ("month", "1 3"))
        self.assertEqual(rows[4], ("day of week", "1 2 3 4 5"))

    def test_weekday_seven_is_sunday(self):
        rows = parse_cron("0 0 * * 7 /bin/true")

        self.assertEqual(rows[4], ("day of week", "0"))

    def test_keeps_command_with_spaces(self):
        rows = parse_cron("0 0 * * * /bin/echo hello world")

        self.assertEqual(rows[-1], ("command", "/bin/echo hello world"))

    def test_rejects_out_of_range_value(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 59"):
            parse_cron("60 * * * * /bin/true")

    def test_rejects_zero_step(self):
        with self.assertRaisesRegex(ValueError, "step must be greater than zero"):
            parse_cron("*/0 * * * * /bin/true")

    def test_rejects_expression_without_command(self):
        with self.assertRaisesRegex(ValueError, "five cron fields"):
            parse_cron("* * * * *")


if __name__ == "__main__":
    unittest.main()
