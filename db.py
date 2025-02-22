import sqlite3

create_table = """
    CREATE TABLE IF NOT EXISTS Properties (
    id TEXT PRIMARY KEY, 
    title TEXT NOT NULL, 
    Price INTEGER NOT NULL,
    Currency TEXT NOT NULL
);
"""


class Db:
    def __init__(self, db_name="idealista.db"):
        self.db_name = db_name
        self._create_properties_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_properties_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)
            conn.commit()

    def close(self):
        self._connect().close()
