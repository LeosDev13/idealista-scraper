import sqlite3

create_table = """
    CREATE TABLE IF NOT EXISTS Properties (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    price INTEGER NOT NULL,
    currency TEXT NOT NULL,
    square_meters INTEGER NOT NULL,
    rooms int NOT NULL,
    has_garage INTEGER DEFAULT 0,
    tags TEXT NOT NULL,
    price_per_meter INTEGER NOT NULL,
    lcoation TEXT NOT NULL
);
"""
# default integer as 0 means FALSE


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
