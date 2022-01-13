from util import load_yaml

SCHEMA_NAME = 'public'

# historial price data table
MARKETPLACE_TABLE = 'marketplace'

# node tables
RELEASE_TABLE = 'releases'
ARTIST_TABLE = 'artists'
LABEL_TABLE = 'labels'

# edge tables
E_ARTIST_RELEASE = 'artist_release'
E_LABEL_RELEASE = 'label_release'

# views
PRICES_VIEW = 'prices'


DATABASE_KEYS = load_yaml('keys/database.yaml')
