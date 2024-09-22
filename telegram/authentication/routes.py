from typing import Any

from aiogram import types, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from authentication.services import Registration
from authentication.services import register_account_request, complete_registration, link_account
from data import BOT_TOKEN
from logger import logger
from notifications.services import create_notification_keyboard
from services.requests import set_access_token, login_account

authentication_router = Router()

@authentication_router.errors()
async def error_handler(exception: types.ErrorEvent) -> Any:
    logger.error(f"Error in notifications application {exception}")

@authentication_router.message(Registration.username)
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


@authentication_router.message(Registration.password)
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


@authentication_router.callback_query(F.data.startswith("link_token:"))
async def link_account_handler(callback: types.CallbackQuery, state: FSMContext):
    link_token = callback.data.split(':')[1]
    user_data = callback.from_user.__dict__
    data = {**user_data, "link_token": link_token}
    response = link_account(data=data, bot_token=BOT_TOKEN)
    if response == 'success':
        await callback.message.edit_reply_markup(reply_markup=None)
        await login_account(data=callback.from_user.__dict__,
                            state=state)

        response_text = 'Успешно привязан! Выберите действие:'
        await callback.message.answer(response_text, reply_markup=create_notification_keyboard())

    else:
        response_text = response
        await callback.message.answer(response_text)


@authentication_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    """
    This handler receives messages with `/start` command
    """
    if len(message.text.split()) == 1:
        await message.answer("Введите ваше имя")
        await state.set_state(Registration.username)
        # await message.answer('Log in to your account on the website')
    else:
        access_token = message.text.split(' ')[1]
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Нажми меня",
            callback_data=f"link_token:{access_token}",
        )
        )
        await message.answer(
            "Чтобы привязать аккаунт нажмите кнопку",
            reply_markup=builder.as_markup()
        )
