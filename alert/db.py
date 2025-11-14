'''
Provide sqlite3 database functions for alert system.
'''

import sqlite3
import os

class DB:
    def __init__(self, db_file):
        # Ensure parent directory exists (if any)
        dirpath = os.path.dirname(db_file)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        # If the database file does not exist, create it by opening a connection
        self.conn = sqlite3.connect(db_file)

    def create_table(self, table, columns):
        '''
        Create a table if it does not exist.
        :param table: Table name
        :param columns: Dictionary of column names and types
        '''
        cols = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        self.conn.cursor().execute(f'''CREATE TABLE IF NOT EXISTS {table} ({cols})''')

    def select(self, table, columns='*', where=None):
        '''
        Select records from a table.
        :param table: Table name
        :param columns: Columns to select
        :param where: WHERE clause
        :return: List of records
        '''
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        self.conn.cursor().execute(query)
        return self.conn.cursor().fetchall()

    def insert(self, table, columns, values):
        '''
        Insert a record into a table.
        :param table: Table name
        :param columns: List of column names
        :param values: List of values
        '''
        cols = ', '.join(columns)
        vals = ', '.join(['?' for _ in values])
        self.conn.cursor().execute(f'''INSERT INTO {table} ({cols}) VALUES ({vals})''', values)
        self.conn.commit()

    def keep_records(self, table, column_group = 'URL', column_order = 'TIME', number=1000):
        '''
        Keep only the latest 'number' of records for each unique value in column_group.
        :param table: Table name
        :param column_group: Column to group by
        :param column_order: Column to order by
        :param number: Number of records to keep
        '''
        c = self.conn.cursor()
        c.execute(f'''SELECT DISTINCT {column_group} FROM {table}''')
        groups = c.fetchall()
        for group in groups:
            c.execute(f'''SELECT COUNT(*) FROM {table} WHERE {column_group}=?''', (group[0],))
            count = c.fetchone()[0]
            if count > number:
                c.execute(f'''DELETE FROM {table} WHERE {column_group}=? AND {column_order} NOT IN 
                              (SELECT {column_order} FROM {table} WHERE {column_group}=? ORDER BY {column_order} DESC LIMIT ?)''',
                          (group[0], group[0], number))
        self.conn.commit()

    def close(self):
        '''
        Close the database connection.
        '''
        self.conn.close()