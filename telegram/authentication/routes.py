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
        await state.update_data(username=username)  # Store username in state
        await message.answer(f'Здравствуйте {username}, введите пароль:')
        # await Registration.password.set()  # Move to password state
        await state.set_state(Registration.password)

    @dp.message(Registration.password)
    async def set_password(message: Message, state: FSMContext):
        password = message.text
        user_data = await state.get_data()  # Retrieve user data from state
        username = user_data.get('username')  # Get the stored username

        response = register_account(username=username, password=password)

        if response.status_code == 201:
            await state.clear()  # Clear the state
            access_token = response.json().get('access_token')
            await set_access_token(token=access_token, state=state)
            await message.answer("Аккаунт создан успешно, удалите пожалуйста сообщение с паролем",
                                 reply_markup=create_notification_keyboard())
        else:
            if 'detail' in response.json():
                await message.answer('Выберите другое имя, это уже занято')
                await state.set_state(Registration.username)  # Go back to username state
            else:
                await message.answer('Произошла ошибка при регистрации. Попробуйте еще раз.')

