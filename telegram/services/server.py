import hashlib
import hmac

import requests
from aiogram.fsm.context import FSMContext
from requests import Response
from typing_extensions import Any

from data import BASE_URL, BOT_TOKEN


def link_account(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/link'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200 and response.json() == 'OK':
        return 'success'
    else:
        return response.text


async def get_access_token(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/login/'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200:
        return response.json().get('access')


async def login_account(data: dict, state: FSMContext) -> str:
    bot_token = BOT_TOKEN
    access_token = await get_access_token(data, bot_token)
    if not access_token:
        return 'error'
    else:
        await state.update_data(access_token=access_token)
        return 'success'

def encode_data(data: dict, bot_token: str):
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    data['hash'] = hash_signature
    return data



async def get_auth_request(url: str, state: FSMContext, user_data: dict) -> Any:
    data = await state.get_data()
    token = data.get('access_token')
    request_url = BASE_URL + url
    response = requests.get(request_url, headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 401:
        login_status = await login_account(data=user_data, state=state)
        if login_status == 'success':
            return await get_auth_request(url=url, state=state, user_data=user_data)
        else:
            return 'Authentication error, link your account'
    else:
        return response.json()

async def post_auth_request(url: str, data: dict, state: FSMContext, user_data: dict) -> Response | str:
    state_data = await state.get_data()
    token = state_data.get('access_token')
    request_url = BASE_URL + url
    response = requests.post(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 401:
        login_status = await login_account(data=user_data, state=state)
        if login_status == 'success':
            return await post_auth_request(url=url, data=data, state=state, user_data=user_data)
        else:
            return 'Authentication error, link your account'
    else:
        return response

async def auth_request(url: str, data: dict, state: FSMContext, user_data: dict, type: str) -> Response | str:
    state_data = await state.get_data()
    token = state_data.get('access_token')
    request_url = BASE_URL + url
    if type == 'get':
        response = requests.get(request_url, headers={'Authorization': f'Bearer {token}'})
    elif type == 'delete':
        response = requests.delete(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif type == 'post':
        response = requests.post(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif type == 'put':
        response = requests.put(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    elif type == 'patch':
        response = requests.patch(request_url, json=data, headers={'Authorization': f'Bearer {token}'})
    else:
        return 'Invalid type'
    if response.status_code == 401:
        login_status = await login_account(data=user_data, state=state)
        if login_status == 'success':
            return await auth_request(url=url, data=data, state=state, user_data=user_data, type=type)
        else:
            return 'Authentication error, link your account'
    else:
        return response

