#!/usr/bin/env python3
"""
Database Migration Tool - Smart Banking Assistant

Usage:
  python migrate.py up              Apply all pending migrations
  python migrate.py status          Show which migrations are applied / pending
  python migrate.py create <name>   Create a new migration file

See MIGRATIONS.md for full documentation and examples.
"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
MIGRATION_TABLE = "_migrations"
MIGRATION_PATTERN = re.compile(r"^V(\d+)__(.+)\.sql$")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "mysql"),
    "database": os.getenv("DB_NAME", "banking_chatbot"),
    "port": int(os.getenv("DB_PORT", "3306")),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _connect(with_db: bool = True):
    config = dict(DB_CONFIG)
    if not with_db:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def _ensure_database():
    """Create the database if it does not already exist."""
    conn = _connect(with_db=False)
    cursor = conn.cursor()
    db = DB_CONFIG["database"]
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()


def _ensure_migrations_table(conn):
    """Create the internal _migrations tracking table if needed."""
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{MIGRATION_TABLE}` (
            id          INT PRIMARY KEY AUTO_INCREMENT,
            version     INT NOT NULL UNIQUE,
            name        VARCHAR(255) NOT NULL,
            filename    VARCHAR(255) NOT NULL UNIQUE,
            applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    cursor.close()


def _get_applied(conn) -> dict:
    """Return {version: filename} for every already-applied migration."""
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT version, filename FROM `{MIGRATION_TABLE}` ORDER BY version"
    )
    rows = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    return rows


def _get_migration_files() -> list:
    """Return sorted [(version, name, Path)] for every V*.sql file."""
    MIGRATIONS_DIR.mkdir(exist_ok=True)
    files = []
    for path in sorted(MIGRATIONS_DIR.glob("V*.sql")):
        m = MIGRATION_PATTERN.match(path.name)
        if m:
            files.append((int(m.group(1)), m.group(2).replace("_", " "), path))
    return files


def _apply_migration(conn, version: int, name: str, path: Path):
    """Execute a single migration file and record it."""
    sql = path.read_text(encoding="utf-8")

    # Split on semicolons — skip empty statements and comments-only blocks
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    cursor = conn.cursor()
    try:
        for stmt in statements:
            cursor.execute(stmt)

        cursor.execute(
            f"INSERT INTO `{MIGRATION_TABLE}` (version, name, filename) "
            f"VALUES (%s, %s, %s)",
            (version, name, path.name),
        )
        conn.commit()
        logger.info(f"  [OK] {path.name}")
    except Error as exc:
        conn.rollback()
        logger.error(f"  [FAIL] {path.name} — {exc}")
        raise
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_up():
    """Apply every pending migration in version order."""
    _ensure_database()
    conn = _connect()
    try:
        _ensure_migrations_table(conn)
        applied = _get_applied(conn)
        all_files = _get_migration_files()
        pending = [(v, n, p) for v, n, p in all_files if v not in applied]

        if not pending:
            logger.info("Already up to date. No pending migrations.")
            return

        logger.info(f"Running {len(pending)} pending migration(s)...\n")
        for version, name, path in pending:
            _apply_migration(conn, version, name, path)

        logger.info(f"\nDone — {len(pending)} migration(s) applied.")
    finally:
        conn.close()


def cmd_status():
    """Print a table showing applied vs pending migrations."""
    _ensure_database()
    conn = _connect()
    try:
        _ensure_migrations_table(conn)
        applied = _get_applied(conn)
        all_files = _get_migration_files()

        if not all_files:
            logger.info("No migration files found in migrations/")
            return

        logger.info(f"\n{'Ver':<6} {'Status':<10} File")
        logger.info("-" * 60)
        for version, _name, path in all_files:
            status = "Applied" if version in applied else "Pending"
            logger.info(f"  V{version:03d}  {status:<10} {path.name}")

        pending_count = sum(1 for v, _, _ in all_files if v not in applied)
        logger.info(
            f"\n{len(all_files)} migration(s) total — "
            f"{len(applied)} applied, {pending_count} pending\n"
        )
    finally:
        conn.close()


def cmd_create(name: str):
    """Scaffold the next migration file."""
    MIGRATIONS_DIR.mkdir(exist_ok=True)
    all_files = _get_migration_files()
    next_version = (max(v for v, _, _ in all_files) + 1) if all_files else 1

    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    filename = f"V{next_version:03d}__{safe_name}.sql"
    filepath = MIGRATIONS_DIR / filename

    if filepath.exists():
        logger.error(f"File already exists: migrations/{filename}")
        sys.exit(1)

    filepath.write_text(
        f"-- Migration: {name}\n"
        f"-- Created:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"-- Write your SQL changes below\n\n",
        encoding="utf-8",
    )
    logger.info(f"Created: migrations/{filename}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "up":
        cmd_up()
    elif command == "status":
        cmd_status()
    elif command == "create":
        if len(sys.argv) < 3:
            logger.error("Usage: python migrate.py create <migration_name>")
            sys.exit(1)
        cmd_create(" ".join(sys.argv[2:]))
    else:
        logger.error(f"Unknown command: '{command}'")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
