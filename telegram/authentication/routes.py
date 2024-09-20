from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import BOT_TOKEN
from services.Authentication import Registration, set_access_token
from services.notifications import create_notification_keyboard
from services.server import register_account


def register_authentication_handlers(dp):
    @dp.message(Registration.username)
    async def set_username(message: Message, state: FSMContext):
        username = message.text
        Registration.username = username
        await message.answer(f'Здравствуйте {username} введите пароль:')
        await state.set_state(Registration.password)

    @dp.message(Registration.password)
    async def set_password(message: Message, state: FSMContext):
        password = message.text
        Registration.password = password
        response = register_account(username=Registration.username, password=password)
        await state.clear()
        if response.status_code == 201:
            access_token = response.json().get('access_token')
            await set_access_token(token=access_token, state=state)
            return message.answer("Аккаунт создан успешно, удалите пожалуйста сообщение с паролем",
                                  reply_markup=create_notification_keyboard())
        else:
            return message.answer(response.text)
