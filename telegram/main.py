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
from services.server import link_account, login_account, get_auth_request
from telegram.services.notifications import create_notification_keyboard, get_all_notifications

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
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Получить уведомления",
            callback_data="notification_list",
        )
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await login_account(data=callback.from_user.__dict__,
                            state=state)  # Assuming this function is defined elsewhere

        response_text = 'Успешно привязан! Выберите действие:'
        await callback.message.answer(response_text, reply_markup=create_notification_keyboard())

    else:
        response_text = response
        await callback.message.answer(response_text)

@dp.callback_query(F.data == 'create')
async def test(callback: types.CallbackQuery, state: FSMContext) -> SendMessage:
    notifications = await get_auth_request(url='notifications/', state=state,
                                           user_data=callback.from_user.__dict__)
    print('only create ')
    builder = InlineKeyboardBuilder()
    for notification in notifications:
        builder.add(types.InlineKeyboardButton(text=notification.title,
                                               callback_data="notification_view"))
    return callback.message.answer(str(notifications))


# @dp.callback_query(F.data == "notification_list")
# async def handle_notification_list(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_reply_markup(reply_markup=None)
#     await login_account(data=callback.from_user.__dict__, state=state)  # Assuming this function is defined elsewhere
#
#     response_text = 'Успешно привязан! Выберите действие:'
#     await callback.message.answer(response_text, reply_markup=create_notification_keyboard())

@dp.message(F.text == 'Показать все уведомления')
async def any_handler(message: Message, state: FSMContext):
    notifications = await get_all_notifications(state=state, user_data=message.from_user.__dict__)
    if notifications:
        await message.answer("\n".join(notifications))
    else:
        await message.answer("Нет уведомлений.")

@dp.callback_query(F.data == "Создать уведомление с тегом")
async def create_notification(message: types.Message):
    await message.answer("Введите текст уведомления и тег (например: 'Уведомление #тег'):")



async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
