import json

with open('../config.json', 'r') as config_file:
    config = json.load(config_file)

# Reddit app credentials saved in hidden config file
CLIENT_ID = config.get('client_id')
CLIENT_SECRET = config.get('client_secret')
REDIRECT_URI = config.get('redirect_uri')
USER_AGENT = config.get('client_id')
REFRESH = config.get('refresh_token')

# Hugging face credentials saved in hidden config file
HF_API_TOKEN = config.get('hugging_face_token')
