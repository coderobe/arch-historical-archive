import sqlite3

class DB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file)
        self.init_db()

    def init_db(self):
        c = self.db.cursor()
        version = self._get_version()

        if version is None:
            c.execute('create table if not exists files (filename text, uploaded int)')
            self._set_version(1)
            version = 1

        if version < 2:
            c.execute('alter table files rename to files_old;')
            c.execute('create table files (filename text, uploaded int, primary key (`filename`)) without rowid;')
            c.execute('insert into files select * from files_old;')
            c.execute('drop table files_old;')
            self._set_version(2)

        self.db.commit()

    def _get_version(self):
        self.db.cursor().execute('pragma user_version').fetchone()[0]

    def _set_version(self, version):
        self.db.cursor().execute('pragma user_version='+str(version))

    def add_file(self, filename):
        c = self.db.cursor()
        c.execute('insert into files (filename, uploaded) values (?, 1)',
                (filename,))
        self.db.commit()

    def exists(self, filename):
        c = self.db.cursor()
        c.execute('select uploaded from files where filename = ?', (filename,))
        return c.fetchone() is not None
