import mysql.connector
from sql.schema import DB_KEYS_MYSQL


class DBMySQL(object):
    def __init__(self, cred, *args, **kwargs):
        self.user = cred.get('user')
        self.host = cred.get('host')
        self.port = cred.get('port')
        self.database = cred.get('database')
        self.password = cred.get('password')
        self.schema_name = cred.get('schema_name')

    def write_rows(self, data, table, returning=None):
        """
        write rows of the dataframe to the table specified
        :param data: list of dict, format like pd.DataFrame.to_dict('records')
        :param table: str, name of the table to write to
        :param returning: str or list of strings, columns to return
        :return: dictionary of returned values if returning is not None
        """

        validate = self.validate

        for row in data:
            col_names = ','.join(list(row.keys()))
            values = ','.join([f'\'{validate(v)}\'' for v in list(row.values())])
            query = f'insert into {self.schema_name}.{table}({col_names}) values '
            query += f'({values})'
            if returning:
                query +=
            with mysql.connector.connect(**self.credentials) as con:


    @property
    def credentials(self):
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'database': self.database
        }

    @staticmethod
    def validate(value):
        return value.replace('%', '')