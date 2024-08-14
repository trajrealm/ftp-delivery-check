import psycopg2


class DBConnection(object):
    _db_connection = None
    _db_cur = None
    _db_engine = None

    def __init__(self, ahost, auser, apass, adbname):
        self.__connect(ahost, auser, apass, adbname)

    def query(self, query):
        return self._db_cur.execute(query, ())

    def fetchall(self):
        return self._db_cur.fetchall()

    def fetchone(self):
        return self._db_cur.fetchone()

    def colnames(self):
        return [desc[0] for desc in self._db_cur.description]

    def __connect(self, ahost, auser, apass, adbname):
        conn_string = "host='%s' dbname=%s user='%s' password='%s'" \
                      % (ahost, adbname, auser, apass)
        self._db_connection = psycopg2.connect(conn_string)
        self._db_connection.autocommit = True
        self._db_cur = self._db_connection.cursor()
