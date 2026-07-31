import sqlite3

def db_dir_exists(db_directory: Path) -> bool:
    return db_directory.exists() and db_directory.is_dir()

def ensure_db_dir_exists(db_directory: Path):
    if not db_dir_exists(db_directory):
        db_directory.mkdir(parents=True, exist_ok=True)
    return db_dir_exists(db_directory)

def db_file_exists(db_path: Path) -> bool:
    return db_path.exists() and db_path.is_file()

def ensure_db_file_exists(db_path: Path):
    if not db_file_exists(db_path):
        # Create an empty database file
        conn = sqlite3.connect(db_path)
        conn.close()
    return db_file_exists(db_path)