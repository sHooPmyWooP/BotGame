import sqlite3
from sqlite3 import Error


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


def main():
    database = r'..\Resources\db\SPY_MESSAGES.db'
    # create a database connection
    conn = create_connection(database)
    with conn:
        select_all(conn, "spy_messages")


if __name__ == '__main__':
    main()
