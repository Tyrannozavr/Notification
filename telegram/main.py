import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import SendMessage
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data import BOT_TOKEN
from services import link_account, login_account

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


@dp.callback_query(F.data.startswith("link_token:"))
async def link_account_handler(callback: types.CallbackQuery, state: FSMContext):
    access_token = callback.data.split(':')[1]
    user_data = callback.from_user.__dict__
    data = {**user_data, "link_token": access_token}
    response = link_account(data=data, bot_token=BOT_TOKEN)
    if response == 'success':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Получить уведомления",
            callback_data="notification_list",
        )
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await login_account(data=callback.from_user.__dict__, bot_token=BOT_TOKEN, state=state)
        response_text = 'Успешно привязан!'
        await callback.message.answer(response_text, reply_markup=builder.as_markup())

    else:
        response_text = response
        await callback.message.answer(response_text)


@dp.callback_query(F.data == 'notification_list')
async def test(callback: types.CallbackQuery) -> SendMessage:
    print('list')
    return callback.message.answer('list')


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
