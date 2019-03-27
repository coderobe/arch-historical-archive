import sqlite3

class DB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file)
        self.init_db()

    def init_db(self):
        c = self.db.cursor()
        c.execute('create table if not exists files (filename text, uploaded int)')
        self.db.commit()

    def add_file(self, filename):
        c = self.db.cursor()
        c.execute('insert into files (filename, uploaded) values (?, 1)',
                (filename,))
        self.db.commit()

    def exists(self, filename):
        c = self.db.cursor()
        c.execute('select uploaded from files where filename = ?', (filename,))
        return c.fetchone() is not None
