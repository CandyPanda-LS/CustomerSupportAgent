import os
import shutil
import sqlite3

import pandas as pd
import psycopg2
import requests

# Configuration
db_url = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
local_file = "travel2.sqlite"
backup_file = "travel2.backup.sqlite"

# PostgreSQL connection details
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'port': '5432'
}


def download_database():
    """Download the SQLite database if needed"""
    overwrite = False
    if overwrite or not os.path.exists(local_file):
        print("Downloading database...")
        response = requests.get(db_url)
        response.raise_for_status()
        with open(local_file, "wb") as f:
            f.write(response.content)
        shutil.copy(local_file, backup_file)
    return local_file


def update_dates(file):
    """Update dates in SQLite database to current time"""
    print("Updating dates to current time...")
    shutil.copy(backup_file, file)
    conn = sqlite3.connect(file)

    # Get all tables
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()

    # Load all data into memory
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    # Calculate time difference to bring dates to present
    example_time = pd.to_datetime(
        tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    # Update bookings table dates
    if 'bookings' in tdf:
        tdf["bookings"]["book_date"] = (
                pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True)
                + time_diff
        )

    # Update flights table dates
    if 'flights' in tdf:
        datetime_columns = [
            "scheduled_departure",
            "scheduled_arrival",
            "actual_departure",
            "actual_arrival",
        ]
        for column in datetime_columns:
            tdf["flights"][column] = (
                    pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
            )

    # Write updated data back to SQLite
    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    return file


def _map_data_type(sqlite_type):
    """Map SQLite data types to PostgreSQL"""
    if sqlite_type is None:
        return 'TEXT'

    sqlite_type = str(sqlite_type).upper()
    if 'INT' in sqlite_type:
        return 'INTEGER'
    elif 'REAL' in sqlite_type or 'FLOAT' in sqlite_type or 'DOUBLE' in sqlite_type:
        return 'FLOAT8'
    elif 'CHAR' in sqlite_type or 'TEXT' in sqlite_type or 'CLOB' in sqlite_type:
        return 'TEXT'
    elif 'BLOB' in sqlite_type or sqlite_type == '':
        return 'BYTEA'
    elif 'DATE' in sqlite_type or 'TIME' in sqlite_type:
        return 'TIMESTAMP WITH TIME ZONE'
    elif 'BOOLEAN' in sqlite_type:
        return 'BOOLEAN'
    else:
        return 'TEXT'  # Default fallback


def migrate_to_postgresql(sqlite_db):
    """Migrate data from SQLite to PostgreSQL"""
    print("Starting migration to PostgreSQL...")

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cur = sqlite_conn.cursor()

    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cur = pg_conn.cursor()

        # Get list of tables
        sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in sqlite_cur.fetchall()]

        for table in tables:
            print(f"Processing table: {table}")

            # Get table structure
            sqlite_cur.execute(f"PRAGMA table_info({table});")
            columns = sqlite_cur.fetchall()
            col_names = [col[1] for col in columns]

            # Create table in PostgreSQL
            create_columns = []
            for col in columns:
                col_name = col[1]
                col_type = _map_data_type(col[2])
                create_columns.append(f"{col_name} {col_type}")

            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(create_columns)});"
            pg_cur.execute(create_table_sql)

            # Get all data from SQLite table
            sqlite_cur.execute(f"SELECT * FROM {table};")
            rows = sqlite_cur.fetchall()

            # Insert data into PostgreSQL
            if rows:
                placeholders = ', '.join(['%s'] * len(col_names))
                insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"
                pg_cur.executemany(insert_sql, rows)

        pg_conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
    finally:
        if 'pg_cur' in locals():
            pg_cur.close()
        if 'pg_conn' in locals():
            pg_conn.close()
        sqlite_cur.close()
        sqlite_conn.close()


if __name__ == "__main__":
    # db_file = download_database()
    updated_db = update_dates(local_file)
    migrate_to_postgresql(updated_db)