from util import load_yaml
import discogs_client


app_keys = load_yaml('keys/appdata.yaml')
token_info = load_yaml('keys/my_token.yaml')

d = discogs_client.Client(
    user_agent='HowLucky',
    consumer_key=app_keys['Consumer Key'],
    consumer_secret=app_keys['Consumer Secret'],
    token=token_info['token'],
    secret=token_info['secret']
)

me = d.identity()

collection = me.collection_folders[0].releases
wantlist = me.wantlist
