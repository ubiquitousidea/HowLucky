from database_classes import BaseDB
import mysql.connector


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
        return self._execute(query, values)

    def _execute(self, query, values):
        query = self._validate(query)
        with mysql.connector.connect(**self.credentials) as con:
            cur = con.cursor()
            cur.execute(query, values)
            con.commit()
