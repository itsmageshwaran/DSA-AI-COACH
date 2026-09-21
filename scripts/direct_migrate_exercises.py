"""
Direct migration script — adds 4 new columns to exercises table in both DBs.
Idempotent: checks if columns exist before adding them.
"""
import sqlite3
import os

DBS = ["app.db", "dsa_coach.db"]
NEW_COLUMNS = [
    ("hints_json", "TEXT"),
    ("company_tags", "VARCHAR(255)"),
    ("required_concept", "VARCHAR(255)"),
    ("difficulty_tier", "VARCHAR(50)"),
]


def migrate_db(path: str) -> None:
    if not os.path.exists(path):
        print(f"  SKIP: {path} not found, skipping.")
        return

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(exercises)")
    existing = {row[1] for row in cursor.fetchall()}

    added = []
    for col_name, col_type in NEW_COLUMNS:
        if col_name not in existing:
            cursor.execute(f"ALTER TABLE exercises ADD COLUMN {col_name} {col_type}")
            added.append(col_name)

    # Also stamp alembic_version so alembic knows we're up to date
    cursor.execute("SELECT version_num FROM alembic_version")
    rows = cursor.fetchall()
    if rows:
        cursor.execute("UPDATE alembic_version SET version_num = 'a1b2c3d4e5f6'")
    else:
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('a1b2c3d4e5f6')")

    conn.commit()
    conn.close()

    if added:
        print(f"  OK {path}: Added columns: {', '.join(added)}")
    else:
        print(f"  SKIP {path}: All columns already exist (idempotent).")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for db in DBS:
        full_path = os.path.join(base, db)
        print(f"Migrating {db}...")
        migrate_db(full_path)
    print("Done.")
