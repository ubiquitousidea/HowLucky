class BaseDB(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def _enquote_values(values, backtick=False, double_quote=False):
        if backtick is True:
            output = [f'`{v}`' for v in values]
        elif double_quote is True:
            output = [f'\"{v}\"' for v in values]
        else:
            output = [f'\'{v}\'' for v in values]
        return output

    def _comma_separate(self, values, quote=False, backtick=False, double_quote=False):
        if quote is True or double_quote is True or backtick is True:
            output = ','.join(self._enquote_values(values, backtick, double_quote))
        else:
            output = ','.join(values)
        return output

    @staticmethod
    def _validate(query):
        return query if query.endswith(';') else f'{query};'
    
    @staticmethod
    def _valid_schema(data):
        """
        check that all rows have the same schema
        :param data:
        :return:
        """
        colnames = [list(row.keys()) for row in data]
        return all([len(set(names)) == 1 for names in zip(*colnames)])

    def _value_grid(self, m, n, fmt='%s'):
        """
        create a blank grid of values for an insert statement
        :param m: number of rows
        :param n: number of columns
        :param fmt: format string
        :return: query string for the VALUES clause of an insert statement
        """
        row = self._row_str(n, fmt)
        x = [f"({row})" for _ in range(m)]
        return ','.join(x)

    @staticmethod
    def _row_str(n, fmt='%s'):
        return ','.join([fmt] * n)

    @staticmethod
    def data_to_dict(data):
        try:
            data = data.to_dict('records')
        except:
            pass
        return data

    def _prepare_col_names(self, df):
        labels = df.columns.tolist()
        return self._comma_separate(labels, double_quote=True)
