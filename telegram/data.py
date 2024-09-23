import os
from os import getenv

from dotenv import load_dotenv

REDIS = os.environ.get('REDIS', "localhost")

load_dotenv('../.env')
BOT_TOKEN = getenv("BOT_TOKEN")
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000/api/')
REDIS_URL = f'redis://{REDIS}:6379/1'
