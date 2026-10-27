MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

DAYS_OF_WEEK = {
    "SUN": 0,
    "MON": 1,
    "TUE": 2,
    "WED": 3,
    "THU": 4,
    "FRI": 5,
    "SAT": 6,
}

FIELDS = [
    ("minute", 0, 59, {}),
    ("hour", 0, 23, {}),
    ("day of month", 1, 31, {}),
    ("month", 1, 12, MONTHS),
    ("day of week", 0, 7, DAYS_OF_WEEK),
]


def parse_number(value, minimum, maximum, names):
    if value.upper() in names:
        number = names[value.upper()]
    else:
        if not value.isascii() or not value.isdigit():
            raise ValueError(f"invalid value {value!r}")
        number = int(value)

    if number < minimum or number > maximum:
        raise ValueError(f"value {value!r} must be between {minimum} and {maximum}")
    return number


def expand_field(expression, minimum, maximum, names, is_day_of_week=False):
    values = []

    for item in expression.split(","):
        parts = item.split("/")
        if len(parts) > 2:
            raise ValueError(f"invalid step expression {item!r}")

        base = parts[0]
        step = 1
        if len(parts) == 2:
            if not parts[1].isascii() or not parts[1].isdigit():
                raise ValueError(f"invalid step in {item!r}")
            step = int(parts[1])
            if step == 0:
                raise ValueError("step must be greater than zero")

        if base == "*":
            start = minimum
            end = maximum
        elif "-" in base:
            range_ends = base.split("-")
            if len(range_ends) != 2 or not range_ends[0] or not range_ends[1]:
                raise ValueError(f"invalid range {base!r}")

            start = parse_number(range_ends[0], minimum, maximum, names)
            end = parse_number(range_ends[1], minimum, maximum, names)
            if start > end:
                raise ValueError(f"range start must not exceed its end in {base!r}")
        else:
            start = parse_number(base, minimum, maximum, names)
            end = maximum if len(parts) == 2 else start

        for value in range(start, end + 1, step):
            if is_day_of_week and value == 7:
                value = 0
            values.append(value)

    return sorted(set(values))


def parse_cron(expression):
    parts = expression.split(maxsplit=5)
    if len(parts) != 6 or not parts[5].strip():
        raise ValueError("expected five cron fields followed by a command")

    rows = []
    for index in range(5):
        name, minimum, maximum, names = FIELDS[index]
        values = expand_field(
            parts[index],
            minimum,
            maximum,
            names,
            is_day_of_week=(name == "day of week"),
        )
        rows.append((name, " ".join(str(value) for value in values)))

    rows.append(("command", parts[5].strip()))
    return rows
