from rich import box
from rich.console import Console
from rich.table import Table


def render_table(rows):
    table = Table(
        title="CRON EXPANSION",
        title_style="bold bright_cyan",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold bright_magenta",
        row_styles=("", "dim"),
        padding=(0, 1),
        show_lines=True,
    )
    table.add_column("FIELD", width=14, no_wrap=True, style="bold bright_cyan")
    table.add_column("EXPANDED VALUES", style="bright_white")

    for name, value in rows:
        table.add_row(name, value)

    Console().print(table)
