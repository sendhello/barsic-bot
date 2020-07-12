from utils import bbunchify
import yaml


with open('config.yaml') as f:
    config = bbunchify(yaml.safe_load(f))

TELEGRAM_TOKEN = config.general.telegram_token