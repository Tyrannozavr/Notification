import hashlib
import hmac

import requests
from aiogram.fsm.context import FSMContext

from data import BASE_URL


def link_account(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/link'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200 and response.json() == 'OK':
        return 'success'
    else:
        return response.text


async def get_access_token(data: dict, bot_token: str) -> str:
    url = BASE_URL + 'auth/telegram/login'
    data = encode_data(data, bot_token=bot_token)
    response = requests.post(url, json={'data': data})
    if response.status_code == 200:
        return response.json().get('access')


async def login_account(data: dict, bot_token: str, state: FSMContext) -> str:
    access_token = get_access_token(data, bot_token)
    await state.update_data(access_token=access_token)


def encode_data(data: dict, bot_token: str):
    data_check_arr = [f"{key}={value}" for key, value in data.items()]
    data_check_arr.sort()
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash_signature = hmac.new(secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()
    data['hash'] = hash_signature
    return data


async def store_user_access_token(user_id: int, token: str):
    try:
        # Check if the user already exists in the database
        user_token = session.query(UserToken).filter_by(user_id=user_id).first()

        if user_token:
            # Update existing token
            user_token.access_token = token
        else:
            # Create a new entry for the user
            user_token = UserToken(user_id=user_id, access_token=token)
            session.add(user_token)

        # Commit the changes to the database
        session.commit()
    except IntegrityError:
        # Handle unique constraint violation (if necessary)
        session.rollback()
        print(f"User ID {user_id} already exists.")
    finally:
        session.close()
