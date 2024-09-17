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

from data import BOT_TOKEN
from services.server import link_account, login_account, post_auth_request
from telegram.services.notifications import create_notification_keyboard, get_all_notifications

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher(storage=MemoryStorage())


class Notification(StatesGroup):
    title = State()
    description = State()
    tags = State()


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
                            state=state)  # Assuming this function is defined elsewhere

        response_text = 'Успешно привязан! Выберите действие:'
        await callback.message.answer(response_text, reply_markup=create_notification_keyboard())

    else:
        response_text = response
        await callback.message.answer(response_text)


@dp.message(F.text == 'Показать все уведомления')
async def notification_list(message: Message, state: FSMContext):
    notifications = await get_all_notifications(state=state, user_data=message.from_user.__dict__)
    if isinstance(notifications, str):
        return await message.answer(notifications)
    if notifications:
        return await message.answer("\n".join(notifications))
    else:
        return await message.answer("Нет уведомлений.")


@dp.message(F.text == 'Создать уведомление')
async def register_cmd_handler(message: Message, state: FSMContext):
    await message.answer("Введите заголовок уведомления:")
    await state.set_state(Notification.title)

@dp.message(Notification.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание уведомления:")
    await state.set_state(Notification.description)

@dp.message(Notification.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите теги уведомления разделенные через пробел (необязательно)")
    await state.set_state(Notification.tags)

@dp.message(Notification.tags)
async def process_tags(message: Message, state: FSMContext):
    await state.update_data(tags=message.text.split())
    user_data = await state.get_data()
    data = {
        "title": user_data["title"],
        "description": user_data["description"],
        "tags": user_data["tags"],
    }
    response = await post_auth_request(url='notifications/', data=data, state=state, user_data=message.from_user.__dict__)
    if isinstance(response, str):
        await message.answer(response)
    else:
        if response.status_code == 201:
            await message.answer('Создано успешно')
        else:
            await message.answer(response.text)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
