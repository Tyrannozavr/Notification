from typing import Any

from aiogram import F, types
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from logger import logger
from notifications.services import NotificationEdit
from notifications.services import render_notification_list, Notification, get_all_notifications, TagSearch
from services.requests import auth_request

notification_router = Router()


@notification_router.errors()
async def error_handler(exception: types.ErrorEvent) -> Any:
    logger.error(
        f"Error in notifications application {exception.exception} \n Error: {exception}")


@notification_router.message(F.text == 'Показать все уведомления')
async def notification_list(message: Message, state: FSMContext):
    notifications = await auth_request('notifications', state=state,
                                       user_data=message.from_user.__dict__, method='get')
    if isinstance(notifications, str):
        return notifications
    if notifications.json():
        notification_response = await render_notification_list(notifications.json())

        return await message.answer("\n".join(notification_response))
    else:
        return await message.answer("Нет уведомлений.")


@notification_router.message(F.text == 'Удалить уведомление')
async def delete_notification(message, state: FSMContext):
    notifications = await get_all_notifications(state=state, user_data=message.from_user.__dict__)
    buttons = []
    for notification in notifications:
        button = InlineKeyboardButton(text=f"{notification.get('id')} {notification.get('title')}",
                                      callback_data=f"delete:{notification.get('id')}")
        buttons.append(button)
    builder = InlineKeyboardBuilder()
    builder.row(*buttons, width=1)
    return await message.answer('выберите какое уведомление удалить', reply_markup=builder.as_markup())


@notification_router.message(F.text == 'Создать уведомление')
async def register_cmd_handler(message: Message, state: FSMContext):
    await message.answer("Введите заголовок уведомления:")
    await state.set_state(Notification.title)


@notification_router.message(Notification.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание уведомления:")
    await state.set_state(Notification.description)


@notification_router.message(Notification.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите теги уведомления разделенные через пробел (необязательно)")
    await state.set_state(Notification.tags)


@notification_router.message(Notification.tags)
async def process_tags(message: Message, state: FSMContext):
    await state.update_data(tags=message.text.split())
    user_data = await state.get_data()
    data = {
        "title": user_data["title"],
        "description": user_data["description"],
        "tags": user_data["tags"],
    }
    response = await auth_request(url='notifications/', data=data, state=state,
                                  user_data=message.from_user.__dict__, method='post')
    if isinstance(response, str):
        return await message.answer(response)
    else:
        if response.status_code == 201:
            await state.clear()
            return await message.answer('Создано успешно')
        else:
            return await message.answer(response.text)


@notification_router.message(F.text == 'Поиск по тэгу')
async def notification_list(message: Message, state: FSMContext):
    await message.answer("Введите тэг по которому хотите произвести поиск")
    return await state.set_state(TagSearch.tag_name)


@notification_router.message(TagSearch.tag_name)
async def notification_tag_search(message: Message, state: FSMContext):
    tag_name = message.text
    tag_name = tag_name[1:]
    url = f'notifications/tags/{tag_name}/'
    response = await auth_request(url, state=state,
                                  user_data=message.from_user.__dict__, method='get')
    await state.clear()
    if response.status_code == 200:
        notifications = response.json()
        if isinstance(notifications, str):
            return await message.answer(notifications)
        if notifications:
            return await message.answer('\n\n'.join([render_notification(notification) for notification
                                                     in notifications]))
        else:
            return await message.answer("Нет уведомлений.")
    else:
        return await message.answer(response.text)


@notification_router.message(F.text == 'Редактировать уведомление')
async def editable_notification_list(message: Message, state: FSMContext):
    notifications = await get_all_notifications(state=state, user_data=message.from_user.__dict__)
    buttons = []
    for notification in notifications:
        button = InlineKeyboardButton(text=f"{notification.get('id')} {notification.get('title')}",
                                      callback_data=f"edit:{notification.get('id')}")
        buttons.append(button)

    builder = InlineKeyboardBuilder()
    builder.row(*buttons, width=1)

    return await message.answer('выберите какое уведомление редактировать', reply_markup=builder.as_markup())



notification_dictionary = {
    "title": "Заголовок",
    "description": "Описание",
    "tags": "Тэги",
}


@notification_router.callback_query(F.data.startswith("delete:"))
async def delete_notification_callback(callback: types.CallbackQuery, state: FSMContext):
    notification_id = callback.data.split(':')[1]
    await auth_request(url=f'notifications/{notification_id}', data={}, state=state,
                       user_data=callback.from_user.__dict__, method='delete')
    return await callback.message.answer(text=f"Удалено {notification_id}")


@notification_router.callback_query(F.data.startswith("edit:"))
async def edit_notification_callback(callback: types.CallbackQuery, state: FSMContext):
    notification_id = callback.data.split(':')[1]
    response = await auth_request(url=f'notifications/get/{notification_id}', data={}, state=state,
                                  user_data=callback.from_user.__dict__, method='get')
    if response.status_code == 200:
        notification = response.json()
        btns = []
        for key, value in notification.items():
            if key == 'tags':
                value = ' '.join([tag.get('name') for tag in value])
            elif key == 'id':
                continue
            button = types.InlineKeyboardButton(text=f'{notification_dictionary.get(key)} - {value}',
                                                callback_data=f'edit_{key}:{notification_id}')
            btns.append(button)
        NotificationEdit.id = notification_id
        builder = InlineKeyboardBuilder()
        builder.row(*btns, width=1)
        return await callback.message.answer(text="Выберите что отредактировать", reply_markup=builder.as_markup())
    else:
        return await callback.message.answer(text=response.text)


@notification_router.callback_query(F.data.startswith("edit_"))
async def edit_notification_part_callback(callback: types.CallbackQuery, state: FSMContext):
    notification_data = callback.data.split('_')[1]
    notification_key, notification_id = notification_data.split(':')
    NotificationEdit.id = notification_id
    await callback.message.answer(f'Введите новый {notification_dictionary.get(notification_key)}')
    NotificationEdit.key = notification_key
    await state.set_state(NotificationEdit.value)


@notification_router.message(NotificationEdit.value)
async def process_title(message: Message, state: FSMContext):
    key = NotificationEdit.key
    if key == 'tags':
        value = message.text.split(' ')
    else:
        value = message.text
    data = {
        key: value
    }
    notification_id = NotificationEdit.id
    await state.clear()
    response = await auth_request(url=f'notifications/{notification_id}/', data=data, state=state,
                                  user_data=message.from_user.__dict__, method='patch')
    if response.status_code == 200:
        notification = response.json()
        response = (f"Успешно отредактировано! \n"
                    f"Заголовок: {notification.get('title')} \n"
                    f"Описание: {notification.get('description')} \n"
                    f"Тэги: {' '.join([tag.get('name') for tag in notification.get('tags', [])])}")
        return await message.answer(response)
    else:
        return await message.answer(response.text)


def render_notification(notification: dict) -> str:
    return (f"{notification.get('title')} \n "
            f"{notification.get('description')} \n"
            f"{[tag.get('name') for tag in notification.get('tags')]}")
