# Cron Expression Parser

A small command-line application that parses a standard five-field cron
expression, expands each time field into its values, and prints the result in
a colorful terminal table alongside the command.

The project is designed to be easy to run, review, and extend. The parser,
command-line entry point, and table presentation are kept in separate modules.

## Features

- Parses the five standard cron fields: minute, hour, day of month, month, and
  day of week.
- Expands wildcards, comma-separated values, inclusive ranges, and step values.
- Accepts three-letter month and weekday names.
- Preserves a command containing spaces when the entire cron expression is
  quoted as one shell argument.
- Displays expanded fields and the command in a colored Rich table.
- Reports malformed expressions and out-of-range values as command-line errors.

## Requirements

- Python 3.12 or newer
- Either [uv](https://docs.astral.sh/uv/) or `pip`

The terminal UI uses [Rich](https://github.com/Textualize/rich).

## Setup with uv

From the project directory, synchronize the environment and dependencies:

```bash
uv sync
```

`uv sync` creates or updates the project virtual environment using
`pyproject.toml` and `uv.lock`.

## Setup with pip

Create and activate a virtual environment, then install Rich:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install rich
```

On Windows Command Prompt, activate the environment with:

```bat
.venv\Scripts\activate
```

On Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the application

Pass the full cron expression and command as one quoted argument:

```bash
uv run python cli.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

If you set up the project with `pip` and activated the virtual environment,
run:

```bash
python cli.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

The output is a table with one row per cron field and one row for the command.
For example, the expanded values are:

```text
minute        0 15 30 45
hour          0
day of month  1 15
month         1 2 3 4 5 6 7 8 9 10 11 12
day of week   1 2 3 4 5
command       /usr/bin/find
```

The actual application presents these rows in a colored, bordered table.

The shell quotes matter: they make the entire expression a single argument to
the program. The command portion may contain spaces:

```bash
uv run python cli.py "0 0 * * * /usr/bin/echo hello world"
```

With the `pip` setup, the equivalent command is:

```bash
python cli.py "0 0 * * * /usr/bin/echo hello world"
```

For help:

```bash
uv run python cli.py --help
```

Or, with the `pip` setup:

```bash
python cli.py --help
```

## Supported cron syntax

The expression has exactly five schedule fields followed by a command:

```text
minute hour day-of-month month day-of-week command
```

| Field        | Allowed numeric values |
| ------------ | ---------------------: |
| Minute       |                   0–59 |
| Hour         |                   0–23 |
| Day of month |                   1–31 |
| Month        |                   1–12 |
| Day of week  |                    0–7 |

Supported field forms:

| Form                 | Example  | Meaning                                                     |
| -------------------- | -------- | ----------------------------------------------------------- |
| A single value       | `5`      | Only value 5                                                |
| Wildcard             | `*`      | Every value in the field's range                            |
| Comma-separated list | `1,5,10` | Values 1, 5, and 10                                         |
| Inclusive range      | `9-12`   | Values 9 through 12                                         |
| Wildcard with a step | `*/15`   | Every 15th value, starting at the field's minimum           |
| Range with a step    | `9-17/4` | Every 4th value from 9 through 17                           |
| Value with a step    | `5/20`   | Starting at 5, every 20th value through the field's maximum |

Lists, ranges, and steps can be combined in one field, for example:

```text
1,10-20/5,45
```

Month names are `JAN` through `DEC`. Weekday names are `SUN` through `SAT`.
Names are case-insensitive. For weekdays, both `0` and `7` represent Sunday;
the output normalizes `7` to `0`.

## Validation and errors

Each field is validated against its own allowed range. Invalid field values,
malformed ranges, invalid steps, or an expression without all five fields and a
command are reported as errors. A failed command-line invocation exits with a
non-zero status.

Examples of invalid input:

```bash
python cli.py "60 * * * * /bin/true"
python cli.py "*/0 * * * * /bin/true"
python cli.py "* * * * *"
```

## Run the tests

The test suite uses Python's built-in `unittest` module, so no additional test
dependency is needed. With `uv`, run:

```bash
uv run python -m unittest discover -s test -v
```

With the `pip` setup and activated virtual environment, run:

```bash
python -m unittest discover -s test -v
```

The tests cover the sample expression, full wildcards, lists, ranges, steps,
month and weekday names, Sunday normalization, commands containing spaces, and
invalid inputs.

## Project layout

```text
.
├── app/
│   ├── main.py                  # CLI argument handling and application flow
│   ├── parser/
│   │   ├── __init__.py          # Public parser import
│   │   └── cron_parser.py       # Cron field parsing and expansion
│   └── presentation/
│       ├── __init__.py          # Public table-rendering import
│       └── table.py             # Rich terminal table
├── test/
│   └── test_cron_parser.py      # Parser unit tests
├── cli.py                       # Root-level executable entry point
├── pyproject.toml               # Project metadata and dependencies
└── uv.lock                      # Locked dependency versions
```

The parser can also be imported directly by Python code:

```python
from app.parser import parse_cron

rows = parse_cron("*/15 0 1,15 * 1-5 /usr/bin/find")
```

## Scope and limitations

This program expands each field independently. It does not calculate actual
calendar dates or future execution timestamps, and it does not run the command.
It supports numeric values, the field forms listed above, and the documented
month and weekday names.

Special schedules such as `@yearly`, seconds or year fields, and extensions
such as `L`, `W`, `?`, or `#` are not supported. The day-of-month and day-of-week
fields are displayed independently; cron's date-matching behavior is not
evaluated.

## Extending the application

- Add parsing behavior in `app/parser/cron_parser.py` and cover it in
  `test/test_cron_parser.py`.
- Keep command-line input and error reporting in `app/main.py`.
- Change table appearance or output formatting in `app/presentation/table.py`.
- After making changes, run the test suite using the `uv` or `pip` command in
  the [Run the tests](#run-the-tests) section.

`parse_cron` returns a list of `(field_name, expanded_values)` pairs, including
the command as the last row. It raises `ValueError` for invalid expressions.
