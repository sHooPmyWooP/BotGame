import sqlite3
from sqlite3 import Error
import os
import os.path


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def query_database(conn):
    c = conn.cursor()
    c.execute("""
            CREATE TABLE IF NOT EXISTS EXPO_MESSAGES(
                id integer primary key,
                expo_timestamp text,
                msg_from text,
                content text,
                result_type text, 
                universe text);
            """)


def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    database = os.path.join(os.path.abspath(os.path.join(dir_path, os.pardir)), 'Resources', 'db', '')
    # create a database connection
    conn = create_connection(database + 'messages.db')
    query_database(conn)
    # with conn:
    #     #     select_all(conn, "spy_messages")


if __name__ == '__main__':
    main()
