"""
This file contains the steps for completing the
OAuth2 process for the discogs API through python
Steps:
1: Create the app on your discogs account and copy the app key into discogs_howlucky.yaml
2: Create the Client object using the name of the app and the consumer key/secret
3: Generate the authentication URL and visit that URL in a browser
4: Log in to your discogs account if prompted and give permission for the app to access account info
5: After accepting, copy the authorization code into the command line and hit enter
6: The get_access_token method returns access token/secrete which are written to file discogs_dsnyder427_token.yaml
"""


from util import load_yaml, write_yaml
import webbrowser
import discogs_client

app_keys = load_yaml('keys/discogs_howlucky.yaml')

d = discogs_client.Client(
    'HowLucky',
    consumer_key=app_keys['Consumer Key'],
    consumer_secret=app_keys['Consumer Secret']
)

auth_url = d.get_authorize_url()
webbrowser.open(auth_url[2])
auth_token = input('authorization token? ')
tokens = d.get_access_token(auth_token)
token_info = {'token': tokens[0], 'secret': tokens[1]}
write_yaml(token_info, 'discogs_dsnyder427_token.yaml')
