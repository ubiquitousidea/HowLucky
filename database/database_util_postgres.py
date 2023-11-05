import numpy as np
import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd
from sql.schema import SCHEMA_NAME
from database.database_classes import BaseDB


def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(np.float64, adapt_numpy_float64)
register_adapter(np.int64, adapt_numpy_int64)


# -----------------------------------------------------------------------------
# - General database functions ------------------------------------------------
# -----------------------------------------------------------------------------

class DBPostgreSQL(BaseDB):
    def __init__(self, cred, *args, **kwargs):
        BaseDB.__init__(self, cred, *args, **kwargs)
        self.user = cred.get('user')
        self.host = cred.get('host')
        self.port = cred.get('port')
        self.dbname = cred.get('dbname')
        self.password = cred.get('password')

    @property
    def credentials(self):
        return {
            'host': self.host,
            'port': self.port,
            'dbname': self.dbname,
            'user': self.user,
            'password': self.password
        }

    def _query(self, q):
        """
        DANGER!
        execute any query, no validation is performed
        """
        with psycopg2.connect(**self.credentials) as conn:
            cur = conn.cursor()
            cur.execute(q)
            return cur.fetchall()
        

    def insert_rows(self, df, tbl, returning=None):
        """
        Write rows of dataframe 'df' to the database table 'tbl'
        :param df: pandas data frame
        :param tbl: table name
        :param returning:
        :return: None
        """
        col_names = self._prepare_col_names(df)
        n_col = df.shape[1]
        fmt = ','.join(['%s'] * n_col)
        with psycopg2.connect(**self.credentials) as conn:
            cur = conn.cursor()
            for idx, row in df.iterrows():
                query = f"INSERT INTO {SCHEMA_NAME}.{tbl}({col_names})\nVALUES ({fmt})\n"
                query += f'RETURNING {returning}' if returning is not None else ''
                query += f"ON CONFLICT DO NOTHING"
                query = self._validate(query)
                try:
                    cur.execute(query, row.values)
                except psycopg2.ProgrammingError as e:
                    print({'query': query})
                    print({'values': row})
                    raise e
        return None

    def update_rows(self, df, index_col, tbl):
        """
        update values in rows
        :param df: data frame of values to update
        :param index_col: name of the primary key column to use in the where statement
        :param tbl: table name
        :return: None
        """
        df = df.set_index(index_col)
        with psycopg2.connect(**self.credentials) as conn:
            cur = conn.cursor()
            col_names = df.columns.to_list()
            for idx, row in df.iterrows():
                values = row.values
                update_string = ','.join([f'{col_name} = %s' for col_name in col_names])
                query = f'update {tbl} set {update_string} where {index_col} = {idx}'
                cur.execute(query, values)
        return None

    def read_rows(self, tbl, **conditions):
        """
        read data from the database table tbl where conditions are true
        :param tbl: name of the database table
        :param conditions: keyword arguments of the form <column_name> = <value>
        :return: pandas data frame
        """
        query = f"SELECT * FROM {SCHEMA_NAME}.{tbl} \n"
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
        query = self._validate(query)
        with psycopg2.connect(**self.credentials) as conn:
            cur = conn.cursor()
            cur.execute(query, cond_values)
            output = pd.DataFrame(
                cur.fetchall(),
                columns=[col[0] for col in cur.description])
        return output
