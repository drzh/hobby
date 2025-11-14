'''
Provide sqlite3 database functions for alert system.
'''

import sqlite3
import os
import re

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
        self.conn.commit()

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

        c = self.conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        return rows

    def insert(self, table, columns, values):
        '''
        Insert a single record or multiple records into a table.
        :param table: Table name (identifier characters only)
        :param columns: Iterable of column names
        :param values: Tuple/list for single row or list of tuples/lists for multiple rows
        :return: lastrowid for single insert, rowcount for multiple inserts
        '''

        if not columns:
            raise ValueError("columns must be a non-empty iterable")

        # Basic identifier validation to avoid SQL injection via table/column names
        ident_re = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
        if not ident_re.match(table):
            raise ValueError("invalid table name")

        cols = list(columns)
        for col in cols:
            if not ident_re.match(col):
                raise ValueError(f"invalid column name: {col}")

        cols_sql = ', '.join([f'"{c}"' for c in cols])
        placeholders = ', '.join(['?'] * len(cols))
        sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})'

        c = self.conn.cursor()

        # Treat a list-of-rows (list of tuples/lists) as many; otherwise single row
        if isinstance(values, list) and values and isinstance(values[0], (list, tuple)):
            # Ensure each row has correct length
            for row in values:
                if len(row) != len(cols):
                    raise ValueError("each row must have the same number of elements as columns")
            c.executemany(sql, values)
            self.conn.commit()
            return c.rowcount
        else:
            row = tuple(values)
            if len(row) != len(cols):
                raise ValueError("values must have the same number of elements as columns")
            c.execute(sql, row)
            self.conn.commit()
            return c.lastrowid

    def keep_records(self, table, column_group='URL', column_order='TIME', number=1000):
        '''
        Keep only the latest 'number' of records for each unique value in column_group.
        :param table: Table name
        :param column_group: Column to group by
        :param column_order: Column to order by
        :param number: Number of records to keep (non-negative int)
        :return: number of rows deleted
        '''
        # Validate identifiers to avoid SQL injection
        ident_re = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
        if not ident_re.match(table):
            raise ValueError("invalid table name")
        if not ident_re.match(column_group):
            raise ValueError("invalid column_group name")
        if not ident_re.match(column_order):
            raise ValueError("invalid column_order name")
        if not isinstance(number, int) or number < 0:
            raise ValueError("number must be a non-negative integer")

        q_table = f'"{table}"'
        q_group = f'"{column_group}"'
        q_order = f'"{column_order}"'

        c = self.conn.cursor()

        # Get distinct group values (may include NULL)
        c.execute(f'SELECT DISTINCT {q_group} FROM {q_table}')
        groups = [row[0] for row in c.fetchall()]

        total_deleted = 0
        for val in groups:
            # Count rows for this group (handle NULL specially)
            if val is None:
                c.execute(f'SELECT COUNT(*) FROM {q_table} WHERE {q_group} IS NULL')
            else:
                c.execute(f'SELECT COUNT(*) FROM {q_table} WHERE {q_group}=?', (val,))
            count = c.fetchone()[0]

            if count > number:
                # Delete rows not in the latest `number` ordered by column_order desc.
                # Handle NULL group value separately because "col = NULL" does not match.
                if val is None:
                    sub = f'SELECT {q_order} FROM {q_table} WHERE {q_group} IS NULL ORDER BY {q_order} DESC LIMIT ?'
                    delete_sql = f'DELETE FROM {q_table} WHERE {q_group} IS NULL AND {q_order} NOT IN ({sub})'
                    c.execute(delete_sql, (number,))
                else:
                    sub = f'SELECT {q_order} FROM {q_table} WHERE {q_group}=? ORDER BY {q_order} DESC LIMIT ?'
                    delete_sql = f'DELETE FROM {q_table} WHERE {q_group}=? AND {q_order} NOT IN ({sub})'
                    c.execute(delete_sql, (val, val, number))

                total_deleted += c.rowcount

        self.conn.commit()
        return total_deleted

    def close(self):
        '''
        Close the database connection.
        '''
        self.conn.close()