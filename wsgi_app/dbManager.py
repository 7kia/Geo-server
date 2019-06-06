# from StringIO import StringIO
# from sqlite3 import dbapi2 as db
import sqlite3
#from pyspatialite import dbapi2 as db

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')

def myMIN(arg):
    console.log(arg)

def myX(arg):
    console.log(arg)

def myY(arg):
    console.log(arg)

class DatabaseManager:
    loadDb = {}

    def loadDbToMemory(self, path):
        if self.loadDb.get(path) is None:
            # connection = sqlite3.connect(path)
            # preloadDb = sqlite3.connect(":memory:")
            # with preloadDb:
            #     connection.backup(preloadDb, pages=1, progress=progress)

            # TODO: delete later
            preloadDb = sqlite3.connect(path)

            preloadDb.create_function("Pow", 2, pow)
            preloadDb.create_function("MIN", 1, myMIN)
            preloadDb.create_function("X", 1, myX)
            preloadDb.create_function("Y", 1, myY)

            self.loadDb[path] = preloadDb

    def getDb(self, path):
        if self.loadDb.get(path) is None:
            self.loadDbToMemory(path)
        return self.loadDb[path]


dbManager = DatabaseManager()