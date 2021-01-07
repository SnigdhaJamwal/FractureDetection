import mysql.connector

def connection():
    conn = mysql.connector.connect(user='<username>', password='<password>',
                              host='localhost',
                              database='<database name>')
    c = conn.cursor()

    return c, conn
