import MySQLdb

def connection():
        conn = MySQLdb.connect(host="localhost", user = "root", passwd = "linq12345",
                               db = "linq")
        c = conn.cursor()
        return c,conn

