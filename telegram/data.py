import os
from os import getenv

from dotenv import load_dotenv

load_dotenv('../.env')
BOT_TOKEN = getenv("BOT_TOKEN")
BASE_URL = os.environ.get('BASE_URL')