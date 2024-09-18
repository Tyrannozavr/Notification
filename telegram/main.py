import asyncio
import json
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from notifications.handlers import register_notification_handlers

from data import BOT_TOKEN
from services.server import link_account, login_account, post_auth_request
from telegram.services.notifications import create_notification_keyboard, notifications_list_view

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    """
    This handler receives messages with `/start` command
    """
    if len(message.text.split()) == 1:
        await message.answer('Log in to your account on the website')
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


# @dp.message_handler(lambda message: message.text == "Создать уведомление с тегом")
# async def create_notification(message: types.Message):
#     await message.answer("Введите текст уведомления и тег (например: 'Уведомление #тег'):")
@dp.callback_query(F.data.startswith("link_token:"))
async def link_account_handler(callback: types.CallbackQuery, state: FSMContext):
    access_token = callback.data.split(':')[1]
    user_data = callback.from_user.__dict__
    data = {**user_data, "link_token": access_token}
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

register_notification_handlers(dp)

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
