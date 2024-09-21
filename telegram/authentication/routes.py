from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data import BOT_TOKEN
from services.Authentication import Registration, set_access_token, get_access_token
from services.notifications import create_notification_keyboard
from services.server import register_account_request, complete_registration


def register_authentication_handlers(dp):
    @dp.message(Registration.username)
    async def set_username(message: Message, state: FSMContext):
        username = message.text
        await state.update_data(username=username)  # Store username in state
        user_data = await state.get_data()
        if user_data.get('password') is None:
            await message.answer(f'Здравствуйте {username}, введите пароль:')
            # await Registration.password.set()  # Move to password state
            await state.set_state(Registration.password)
        else:
            await set_password(message=message, state=state)

    @dp.message(Registration.password)
    async def set_password(message: Message, state: FSMContext):
        user_data = await state.get_data()  # Retrieve user data from state
        username = user_data.get('username')  # Get the stored username

        password = user_data.get('password')
        if password is None:
            password = message.text
            await state.update_data(password=password)
        response = register_account_request(username=username, password=password)

        if response.status_code == 201:
            access_token = response.json().get('access_token')
            state = await set_access_token(token=access_token, state=state)
            is_telegram_linked = await complete_registration(state=state, user_data=message.from_user.__dict__)
            await state.clear()  # Clear the state
            if is_telegram_linked == 'success':
                await message.answer("Аккаунт создан успешно, удалите пожалуйста сообщение с паролем",
                                     reply_markup=create_notification_keyboard())
            else:
                await message.answer("Аккаунт создан успешно, но не удалось привязать аккаунт телеграм к "
                                     "существующему аккаунту, удалите пожалуйста сообщение с паролем и попробуйте "
                                     "получить ссылку на привязку акканут на нашем веб сайте",
                                     reply_markup=create_notification_keyboard())
        else:
            if 'detail' in response.json():
                await message.answer('Выберите другое имя, это уже занято')
                await state.set_state(Registration.username)  # Go back to username state
            else:
                await message.answer('Произошла ошибка при регистрации. Попробуйте еще раз.')

