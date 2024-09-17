from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from telegram.services.server import login_account, get_auth_request


# Create a reply keyboard for notifications
def create_notification_keyboard():
    button_create = KeyboardButton(text="Создать уведомление")
    button_show = KeyboardButton(text="Показать все уведомления")
    button_edit = KeyboardButton(text="Редактировать уведомление")
    button_delete = KeyboardButton(text="Удалить уведомление")

    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[[button_show, button_create, button_edit, button_delete]])
    return greet_kb

async def get_all_notifications(state: FSMContext, user_data: dict) -> list:
    notifications = await get_auth_request('notifications', state=state, user_data=user_data)
    return [
        (f"{notification.get('id')}: {notification.get('title')} \n "
         f"{notification.get('description')} \n"
         f" {' #'.join([tag.get('name') for tag in notification.get('tags')])}")
        for notification in notifications
    ]

