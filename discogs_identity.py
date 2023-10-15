from util import load_yaml
import discogs_client


app_keys = load_yaml("keys/discogs_howlucky.yaml")
token_info = load_yaml("keys/discogs_dsnyder427_token.yaml")

dclient = discogs_client.Client(
    user_agent="HowLucky",
    consumer_key=app_keys["Consumer Key"],
    consumer_secret=app_keys["Consumer Secret"],
    token=token_info["token"],
    secret=token_info["secret"],
)

me = dclient.identity()
