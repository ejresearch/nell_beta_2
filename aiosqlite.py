import sqlite3

Row = sqlite3.Row

class Cursor:
    def __init__(self, cur):
        self._cur = cur

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def fetchone(self):
        return self._cur.fetchone()

    async def fetchall(self):
        return self._cur.fetchall()

class Connection:
    def __init__(self, path):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._conn.close()

    async def execute(self, sql, params=()):
        cur = self._conn.execute(sql, params)
        return Cursor(cur)

    async def commit(self):
        self._conn.commit()

async def connect(path):
    return Connection(path)

