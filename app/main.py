import argparse

from app.parser import parse_cron
from app.presentation import render_table


def main():
    parser = argparse.ArgumentParser(
        description="Expand a five-field cron expression."
    )
    parser.add_argument(
        "expression",
        help='cron expression and command, e.g. "*/15 0 1,15 * 1-5 /usr/bin/find"',
    )
    args = parser.parse_args()

    try:
        rows = parse_cron(args.expression)
    except ValueError as error:
        parser.error(str(error))

    render_table(rows)
