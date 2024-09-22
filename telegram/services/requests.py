import hashlib
import hmac

import requests
from aiogram.fsm.context import FSMContext
from requests import Response

from data import BASE_URL, BOT_TOKEN


async def fetch_access_token(data: dict, bot_token: str, state: FSMContext) -> str:
    url = BASE_URL + 'auth/telegram/login/'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200:
        token = response.json().get('access')
        await set_access_token(token, state=state)
        return token


def encode_data(data: dict, bot_token: str):
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    data['hash'] = hash_signature
    return data


async def set_access_token(token, state: FSMContext):
    await state.update_data({'token': token})
    return state


async def get_access_token(state: FSMContext):
    data = await state.get_data()
    return data.get('token', None)


async def login_account(data: dict, state: FSMContext) -> str:
    bot_token = BOT_TOKEN
    access_token = await fetch_access_token(data, bot_token, state=state)
    if not access_token:
        return 'error'
    else:
        await set_access_token(access_token, state=state)
        return 'success'


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
