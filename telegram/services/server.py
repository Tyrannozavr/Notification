import hashlib
import hmac

import requests
from aiogram.fsm.context import FSMContext
from requests import Response
from typing_extensions import Any

from data import BASE_URL, BOT_TOKEN
from services.Authentication import set_access_token, get_access_token


def link_account(data: dict, bot_token: str) -> str:
    print('link data is', data)
    url = BASE_URL + 'auth/telegram/link'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    print('telegram linked', response.json(), response.status_code)
    if response.status_code == 200 and response.json() == 'OK':
        return 'success'
    else:
        return response.text


def register_account_request(username: str, password: str) -> Response:
    register_data = {
        "username": username,
        "password": password
    }
    response = requests.post(BASE_URL + 'auth/register/', json=register_data)
    return response


async def complete_registration(state: FSMContext, user_data: dict):
    response = await auth_request(url='auth/telegram/link/', state=state,
                                  user_data=user_data, method='get')
    if not isinstance(response, Response):
        return response
    else:
        telegram_link_token = response.json().split('=')[1]
        data = {**user_data, "link_token": telegram_link_token}
        response = link_account(data=data, bot_token=BOT_TOKEN)
        return response


async def fetch_access_token(data: dict, bot_token: str, state: FSMContext) -> str:
    url = BASE_URL + 'auth/telegram/login/'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200:
        token = response.json().get('access')
        await set_access_token(token, state=state)
        return token


async def login_account(data: dict, state: FSMContext) -> str:
    bot_token = BOT_TOKEN
    access_token = await fetch_access_token(data, bot_token, state=state)
    if not access_token:
        return 'error'
    else:
        await set_access_token(access_token, state=state)
        return 'success'


def encode_data(data: dict, bot_token: str):
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    data['hash'] = hash_signature
    return data


async def auth_request(url: str, state: FSMContext, user_data: dict, method: str, data=None) -> Response | str:
    if data is None:
        data = {}
    token = await get_access_token(state)
    request_url = BASE_URL + url
    if method == 'get':
        response = requests.get(request_url, headers={'Authorization': f'Bearer {token}'})
    elif method == 'delete':
        response = requests.delete(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif method == 'post':
        response = requests.post(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif method == 'put':
        response = requests.put(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif method == 'patch':
        response = requests.patch(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    else:
        return 'Invalid type'
    if response.status_code == 401:
        login_status = await login_account(data=user_data, state=state)
        if login_status == 'success':
            return await auth_request(url=url, data=data, state=state, user_data=user_data, method=method)
        else:
            return 'Authentication error, link your account'
    else:
        return response
