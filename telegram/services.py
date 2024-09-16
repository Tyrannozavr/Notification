import hashlib
import hmac
import os

import requests
from dotenv import load_dotenv

from data import BASE_URL


def link_account(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/link'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200 and response.json() == 'OK':
        return 'success'
    else:
        return response.text

def encode_data(data: dict, bot_token: str):
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    data['hash'] = hash_signature
    return data
