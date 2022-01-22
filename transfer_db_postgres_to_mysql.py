import numpy as np
from database_util_mysql import DBMySQL
from database_util_postgres import read_rows as read_rows_postgres
from util import load_yaml


migration_control = dict(
    releases=True,
    marketplace=True,
    artists=True,
    labels=True,
    artist_release=True,
    label_release=True
)


KEYS = load_yaml('keys/database_mysql_root.yaml')
db = DBMySQL(KEYS)


for table, migrate in migration_control.items():
    if migrate:
        print(f'migrating table {table}')
        df = read_rows_postgres(table)
        df = df.replace({np.nan: None})
        if table == 'marketplace':
            df = df.drop('qid', axis=1)
        elif table == 'labels' or table == 'artists':
            df = df.drop('profile', axis=1)
        else:
            pass
        db.insert_rows(df.to_dict('records'), table)


# q = '''
# insert into vinyl.marketplace (release_id, lowest_price, currency, num_for_sale, `when`)
# values(%s, %s, %s, %s, %s);
# '''
