class Datasette:
    def __init__(self, files, metadata):
        self.files = files

    @property
    def databases(self):
        for key, info in sorted(self.inspect().items()):
            yield Database(self, info)


class Database:
    def __init__(self, datasette, info):
        self.datasette = datasette
        self.info = info

    @property
    def tables(self):
        for table in self.info["tables"]:
            yield Table(self, table)


class Table:
    def __init__(self, database, info):
        self.database = database
        self.info = info
