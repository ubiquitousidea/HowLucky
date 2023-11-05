from util import load_yaml


DB_CHOICE = "postgres"
SCHEMA_NAME = "public"  # postgresql

# historial price data table
MARKETPLACE_TABLE = "marketplace"
SEARCH_TABLE = "search"
# node tables
RELEASE_TABLE = "releases"
ARTIST_TABLE = "artists"
LABEL_TABLE = "labels"

# edge tables
E_ARTIST_RELEASE = "artist_release"
E_LABEL_RELEASE = "label_release"

ALL_TABLES = [
    MARKETPLACE_TABLE,
    RELEASE_TABLE,
    ARTIST_TABLE,
    LABEL_TABLE,
    E_ARTIST_RELEASE,
    E_LABEL_RELEASE
]

ALL_ENT = [
    'artist',
    'label',
    'release'
]

# views
PRICES_VIEW = "prices"


DB_KEYS_POSTGRES = load_yaml("keys/database_postgres.yaml")
# DB_KEYS_MYSQL = load_yaml('keys/database_mysql_root.yaml')
