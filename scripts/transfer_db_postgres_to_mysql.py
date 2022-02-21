import numpy as np
from database.database_util import get_db_object


migration_control = dict(
    releases=True,
    marketplace=True,
    artists=True,
    labels=True,
    artist_release=True,
    label_release=True
)

db_from = get_db_object('mysql')
db_to = get_db_object('postgres')

for table, migrate in migration_control.items():

    if migrate:
        print(f'migrating table {table}')
        df = db_from.read_rows(table)
        df = df.replace({np.nan: None})
        if table == 'marketplace':
            df = df.drop('qid', axis=1)
        try:
            df = df.drop('profile', axis=1)
        except:
            pass
        db_to.insert_rows(df, table)
