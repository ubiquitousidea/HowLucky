from database.database_classes import BaseDB
import mysql.connector
import pandas as pd


class DBMySQL(BaseDB):
    def __init__(self, cred, *args, **kwargs):
        """
        Create a MySQL database interface object
        :param cred: dict, credentials for database
        """
        BaseDB.__init__(self, *args, **kwargs)
        self.user = cred.get('user')
        self.host = cred.get('host')
        self.port = cred.get('port')
        self.database = cred.get('database')
        self.password = cred.get('password')

    @property
    def credentials(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'passwd': self.password,
            'database': self.database
        }

    def insert_rows(self, data, table, returning=None):
        """
        write rows of the dataframe to the table specified
        :param data: list of dict, format like pd.DataFrame.to_dict('records')
        :param table: str, name of the table to write to
        :param returning: str or list of strings, columns to return
        :return: dictionary of returned values if returning is not None
        """
        data = self.data_to_dict(data)
        assert self._valid_schema(data), 'schema error in data'
        col_names = self._comma_separate(data[0].keys(), backtick=True)
        n_col = len(data[0])
        m_row = len(data)
        query = f'insert into {self.database}.{table}({col_names}) values '
        query += self._value_grid(m=m_row, n=n_col)
        if returning is not None:
            query += f' returning {self._comma_separate(returning)}'
        values = []
        for row in data:
            values.extend(list(row.values()))
        values = tuple(values)
        return self._execute(query, values, commit=True)

    def read_rows(self, table, **conditions):
        query = f'select * from {self.database}.{table} '
        cond_values = None  # this name needs to be defined for cur.execute to run
        if len(conditions) > 0:
            cond_values = []
            format_st = []
            for colname, values in conditions.items():
                n = len(values)
                _ = ','.join(['%s'] * n)
                fmt = f'{colname} in ({_})'
                format_st.append(fmt)
                cond_values.extend(values)
            condition_string = ' AND '.join(format_st)
            query += f'WHERE {condition_string}'
        output = self._execute(query, cond_values)
        return output

    def _execute(self, query, values, commit=False):
        query = self._validate(query)
        with mysql.connector.connect(**self.credentials) as con:
            cur = con.cursor()
            cur.execute(query, values)
            if commit is True:
                con.commit()
            try:
                output = pd.DataFrame(
                    cur.fetchall(),
                    columns=[_[0] for _ in cur.description]
                )
            except:
                output = None
        return output

