import argparse
from collections.abc import Sequence


class CronExpressionParser:
    FIELDS = (
        ("minute", 0, 59, {}),
        ("hour", 0, 23, {}),
        ("day of month", 1, 31, {}),
        (
            "month",
            1,
            12,
            {
                name: value
                for value, name in enumerate(
                    (
                        "JAN",
                        "FEB",
                        "MAR",
                        "APR",
                        "MAY",
                        "JUN",
                        "JUL",
                        "AUG",
                        "SEP",
                        "OCT",
                        "NOV",
                        "DEC",
                    ),
                    start=1,
                )
            },
        ),
        (
            "day of week",
            0,
            7,
            {
                name: value
                for value, name in enumerate(
                    ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT")
                )
            },
        ),
    )

    def parse(self, expression: str) -> list[tuple[str, str]]:
        parts = expression.split(maxsplit=5)
        if len(parts) != 6 or not parts[5].strip():
            raise ValueError("expected five cron fields followed by a command")

        rows: list[tuple[str, str]] = []
        for field_expression, (name, minimum, maximum, names) in zip(
            parts[:5], self.FIELDS, strict=True
        ):
            values = self._expand_field(
                field_expression,
                minimum,
                maximum,
                names,
                name == "day of week",
            )
            rows.append((name, " ".join(str(value) for value in values)))

        rows.append(("command", parts[5].strip()))
        return rows

    @staticmethod
    def _parse_value(
        token: str,
        minimum: int,
        maximum: int,
        names: dict[str, int],
    ) -> int:
        value = names.get(token.upper())
        if value is None:
            if not token.isascii() or not token.isdigit():
                raise ValueError(f"invalid value {token!r}")
            value = int(token)

        if not minimum <= value <= maximum:
            raise ValueError(
                f"value {token!r} must be between {minimum} and {maximum}"
            )
        return value

    @classmethod
    def _expand_field(
        cls,
        expression: str,
        minimum: int,
        maximum: int,
        names: dict[str, int],
        sunday_alias: bool,
    ) -> list[int]:
        values: set[int] = set()

        for item in expression.split(","):
            if not item:
                raise ValueError("empty item in comma-separated field")

            components = item.split("/")
            if len(components) > 2:
                raise ValueError(f"invalid step expression {item!r}")
            base = components[0]
            step = 1
            if len(components) == 2:
                if not components[1].isascii() or not components[1].isdigit():
                    raise ValueError(f"invalid step in {item!r}")
                step = int(components[1])
                if step == 0:
                    raise ValueError("step must be greater than zero")

            if base == "*":
                start, end = minimum, maximum
            elif "-" in base:
                endpoints = base.split("-")
                if len(endpoints) != 2 or not all(endpoints):
                    raise ValueError(f"invalid range {base!r}")
                start = cls._parse_value(endpoints[0], minimum, maximum, names)
                end = cls._parse_value(endpoints[1], minimum, maximum, names)
                if start > end:
                    raise ValueError(
                        f"range start must not exceed its end in {base!r}"
                    )
            else:
                start = cls._parse_value(base, minimum, maximum, names)
                end = maximum if len(components) == 2 else start

            for value in range(start, end + 1, step):
                if sunday_alias and value == 7:
                    value = 0
                values.add(value)

        return sorted(values)


def render(rows: Sequence[tuple[str, str]]) -> None:
    for label, value in rows:
        print(f"{label:<14}{value}")


def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description="Expand a five-field cron expression."
    )
    argument_parser.add_argument(
        "expression",
        help='cron expression and command, e.g. "*/15 0 1,15 * 1-5 /usr/bin/find"',
    )
    args = argument_parser.parse_args()

    try:
        rows = CronExpressionParser().parse(args.expression)    
    except ValueError as error:
        argument_parser.error(str(error))

    render(rows)


if __name__ == "__main__":
    main()
