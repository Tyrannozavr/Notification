import requests
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from requests import Response

from data import BASE_URL, BOT_TOKEN
from logger import logger
from services.requests import encode_data, auth_request


class Registration(StatesGroup):
    username = State()
    password = State()


def link_account(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/link'
    raw_data = data
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200 and response.json() == 'OK':
        logger.info(f'linked account {raw_data}')
        return 'success'
    else:
        return response.text


def register_account_request(username: str, password: str) -> Response:
    register_data = {
        "username": username,
        "password": password
    }
    logger.info(f'Registering account {username}')
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
