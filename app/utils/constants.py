from database.db_utils import DatabaseManager
import os
Database_path: str = os.getenv("DATABASE_PATH", "fitness_studio.db")

DATABASE= DatabaseManager(db_path=Database_path)