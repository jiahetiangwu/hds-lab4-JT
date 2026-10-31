"""Inspect SQLite schema, relationships, row counts, and missing values in read-only mode."""
import argparse
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(__file__).resolve().parent / "data/raw/cohort.db")
    args = parser.parse_args()
    path = args.db.resolve()
    if not path.is_file():
        parser.error(f"Database not found: {path}")
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        print("Integrity:", connection.execute("PRAGMA integrity_check").fetchone()[0])
        print("Foreign key violations:", len(connection.execute("PRAGMA foreign_key_check").fetchall()))
        tables = connection.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        for name, definition in tables:
            quoted_name = '"' + name.replace('"', '""') + '"'
            print(f"\n{name}: {connection.execute('SELECT COUNT(*) FROM ' + quoted_name).fetchone()[0]} rows")
            print(definition)
        checks = {
            "Patients without samples": "SELECT COUNT(*) FROM patients p WHERE NOT EXISTS (SELECT 1 FROM samples s WHERE s.patient_id=p.patient_id)",
            "Patients with multiple samples": "SELECT COUNT(*) FROM (SELECT patient_id FROM samples GROUP BY patient_id HAVING COUNT(*)>1)",
            "Samples without mutation records": "SELECT COUNT(*) FROM samples s WHERE NOT EXISTS (SELECT 1 FROM mutations m WHERE m.sample_id=s.sample_id)",
            "Missing sex, age, stage (NULL counts)": "SELECT SUM(sex IS NULL), SUM(age_at_diagnosis IS NULL), SUM(stage IS NULL) FROM patients",
        }
        for label, query in checks.items():
            print(f"{label}: {connection.execute(query).fetchone()}")


if __name__ == "__main__":
    main()
