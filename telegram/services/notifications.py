from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from services.server import auth_request


class Notification(StatesGroup):
    title = State()
    description = State()
    tags = State()

class NotificationEdit(StatesGroup):
    id = State()
    key = State()
    value = State()

class TagSearch(StatesGroup):
    tag_name = State()

# Create a reply keyboard for notifications
def create_notification_keyboard():
    button_create = KeyboardButton(text="Создать уведомление")
    button_show = KeyboardButton(text="Показать все уведомления")
    button_edit = KeyboardButton(text="Редактировать уведомление")
    button_delete = KeyboardButton(text="Удалить уведомление")
    button_search = KeyboardButton(text="Поиск по тэгу")

    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[[button_show, button_create, button_edit, button_delete, button_search]])
    return greet_kb


async def get_all_notifications(state: FSMContext, user_data: dict) -> list | str:
    notifications = await auth_request('notifications', state=state, user_data=user_data, method='get')
    return notifications

async def render_notification_list(notifications: List[dict]) -> list:
    return [
        (f"{notification.get('id')}: {notification.get('title')} \n "
         f"{notification.get('description')} \n"
         f" {' '.join([tag.get('name') for tag in notification.get('tags')])}")
        for notification in notifications
    ]

