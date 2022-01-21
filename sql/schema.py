from util import load_yaml

SCHEMA_NAME = 'public'

# historial price data table
MARKETPLACE_TABLE = 'marketplace'
SEARCH_TABLE = 'search'
# node tables
RELEASE_TABLE = 'releases'
ARTIST_TABLE = 'artists'
LABEL_TABLE = 'labels'

# edge tables
E_ARTIST_RELEASE = 'artist_release'
E_LABEL_RELEASE = 'label_release'

# views
PRICES_VIEW = 'prices'


DB_KEYS_POSTGRES = load_yaml('keys/database_postgres.yaml')
DB_KEYS_MYSQL = load_yaml('keys/database_mysql.yaml')
