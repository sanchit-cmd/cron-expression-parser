# Cron Expression Parser

Expand a standard five-field cron expression and display each field's
scheduled values alongside its command.

```bash
python main.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

The fields support `*`, comma-separated values, ranges, and `/step` values.
Month names (`JAN`–`DEC`) and weekday names (`SUN`–`SAT`) are also accepted.
Weekday `7` is treated as Sunday (`0`). The command may contain spaces when the
entire expression is passed as one quoted argument.