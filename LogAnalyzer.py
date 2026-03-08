# ============================================================
#  log_analyzer.py
#  Server Log Analyzer — Counter + defaultdict
# ============================================================

"""
Self-Study Note — Python logging module
─────────────────────────────────────────
The standard format string for the logging module looks like:

    fmt = '%(asctime)s %(levelname)-8s %(name)s — %(message)s'

Key format fields:
  %(asctime)s    — human-readable timestamp (default: YYYY-MM-DD HH:MM:SS,mmm)
  %(levelname)s  — level name: DEBUG/INFO/WARNING/ERROR/CRITICAL
  %(name)s       — logger name (usually __name__ of the module)
  %(message)s    — the log message string

To add this to a real application:

    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(name)s — %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(),
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Server started")
    logger.error("Database connection failed")

The FileHandler writes to disk; StreamHandler echoes to stdout.
RotatingFileHandler is preferred in production to cap file size.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime


# ─────────────────────────────────────────────────────────────
#  SIMULATED SERVER LOG
# ─────────────────────────────────────────────────────────────

RAW_LOGS: list[str] = [
    "2024-03-01 08:00:01 INFO     auth      — User login successful: user_42",
    "2024-03-01 08:00:03 INFO     api       — GET /products 200 OK",
    "2024-03-01 08:00:05 ERROR    database  — Connection timeout after 30s",
    "2024-03-01 08:00:06 INFO     api       — GET /cart 200 OK",
    "2024-03-01 08:00:10 WARNING  api       — Rate limit approaching for IP 10.0.0.5",
    "2024-03-01 08:00:12 ERROR    database  — Connection timeout after 30s",
    "2024-03-01 08:00:15 INFO     auth      — User login successful: user_17",
    "2024-03-01 08:00:18 ERROR    payments  — Payment gateway unreachable",
    "2024-03-01 08:00:20 INFO     api       — POST /checkout 201 Created",
    "2024-03-01 08:00:22 CRITICAL database  — Max connection pool exhausted",
    "2024-03-01 08:00:25 ERROR    payments  — Payment gateway unreachable",
    "2024-03-01 08:00:27 WARNING  auth      — Failed login attempt: user_99 (3rd attempt)",
    "2024-03-01 08:00:30 INFO     api       — GET /orders 200 OK",
    "2024-03-01 08:00:33 ERROR    database  — Query execution failed: SELECT * FROM orders",
    "2024-03-01 08:00:35 INFO     cache     — Cache miss for key: product_catalog",
    "2024-03-01 08:00:37 WARNING  api       — Deprecated endpoint /v1/products called",
    "2024-03-01 08:00:40 ERROR    payments  — Payment gateway unreachable",
    "2024-03-01 08:00:42 INFO     api       — GET /search?q=laptop 200 OK",
    "2024-03-01 08:00:45 ERROR    auth      — JWT token validation failed: expired token",
    "2024-03-01 08:00:47 CRITICAL payments  — All payment processors offline",
    "2024-03-01 08:00:50 INFO     cache     — Cache refreshed: product_catalog",
    "2024-03-01 08:00:52 WARNING  database  — Slow query detected (2.3s): SELECT * FROM users",
    "2024-03-01 08:00:55 ERROR    database  — Connection timeout after 30s",
    "2024-03-01 08:00:57 INFO     api       — DELETE /session 200 OK",
    "2024-03-01 08:01:00 ERROR    auth      — JWT token validation failed: expired token",
]

# Log line pattern: YYYY-MM-DD HH:MM:SS LEVEL    module  — message
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>\w+)\s+"
    r"(?P<module>\w+)\s+—\s+"
    r"(?P<message>.+)$"
)


# ─────────────────────────────────────────────────────────────
#  PARSE
# ─────────────────────────────────────────────────────────────

def parse_log_line(line: str) -> dict | None:
    """
    Parse a single log line into a structured dict.

    Returns:
        {'timestamp': str, 'level': str, 'module': str, 'message': str}
        or None if the line does not match the expected format.
    """
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return match.groupdict()


def parse_all_logs(raw_lines: list[str]) -> list[dict]:
    """Parse all raw log lines; silently skip malformed lines."""
    parsed = [parse_log_line(line) for line in raw_lines]
    return [entry for entry in parsed if entry is not None]


# ─────────────────────────────────────────────────────────────
#  ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyze_logs(entries: list[dict]) -> dict:
    """
    Run full analysis on parsed log entries.

    Uses:
      - Counter  for level distribution, top errors, module activity
      - defaultdict(list) to group error messages by module

    Args:
        entries: List of parsed log dicts.

    Returns:
        Summary dict with analysis results.
    """
    if not entries:
        return {"total_entries": 0, "error_rate": 0.0,
                "top_errors": [], "busiest_module": None}

    total = len(entries)

    # Counter: level distribution
    level_counts: Counter = Counter(e.get("level") for e in entries)

    # Counter: most active modules
    module_counts: Counter = Counter(e.get("module") for e in entries)

    # Counter: most common error messages (ERROR + CRITICAL only)
    error_messages: Counter = Counter(
        e.get("message")
        for e in entries
        if e.get("level") in ("ERROR", "CRITICAL")
    )

    # defaultdict(list): group error messages by module
    errors_by_module: defaultdict = defaultdict(list)
    for e in entries:
        if e.get("level") in ("ERROR", "CRITICAL"):
            errors_by_module[e.get("module", "unknown")].append(e.get("message"))

    error_count = level_counts.get("ERROR", 0) + level_counts.get("CRITICAL", 0)
    error_rate  = round(error_count / total * 100, 1)

    busiest_module = module_counts.most_common(1)[0][0] if module_counts else None
    top_errors     = [(msg, count) for msg, count in error_messages.most_common(3)]

    return {
        "total_entries":    total,
        "error_rate":       f"{error_rate}%",
        "level_distribution": dict(level_counts),
        "top_errors":       top_errors,
        "busiest_module":   busiest_module,
        "module_activity":  dict(module_counts.most_common()),
        "errors_by_module": dict(errors_by_module),
    }


# ─────────────────────────────────────────────────────────────
#  DEMO / MAIN
# ─────────────────────────────────────────────────────────────

def divider(title: str) -> None:
    print(f"\n{'─' * 60}\n  {title}\n{'─' * 60}")


def main() -> None:
    entries = parse_all_logs(RAW_LOGS)

    divider("📋 PARSED LOG SAMPLE (first 5 entries)")
    for e in entries[:5]:
        print(f"  [{e['level']:<8}] {e['module']:<10} {e['timestamp']}  {e['message']}")

    summary = analyze_logs(entries)

    divider("📊 SUMMARY")
    print(f"  Total log entries : {summary['total_entries']}")
    print(f"  Error rate        : {summary['error_rate']}")
    print(f"  Busiest module    : {summary['busiest_module']}")

    divider("📈 LEVEL DISTRIBUTION")
    for level, count in sorted(summary["level_distribution"].items()):
        bar = "█" * count
        print(f"  {level:<8} {count:>3}  {bar}")

    divider("🔥 TOP 3 ERROR MESSAGES")
    for i, (msg, count) in enumerate(summary["top_errors"], 1):
        print(f"  {i}. [{count}x] {msg}")

    divider("🗂️  ERRORS BY MODULE")
    for module, errors in summary["errors_by_module"].items():
        uniq = list(dict.fromkeys(errors))   # preserve order, deduplicate
        print(f"  {module:<12}  {len(errors)} error(s): {uniq}")

    divider("📡 MODULE ACTIVITY")
    for module, count in summary["module_activity"].items():
        bar = "▪" * count
        print(f"  {module:<12} {count:>2}  {bar}")

    print()


if __name__ == "__main__":
    main()
