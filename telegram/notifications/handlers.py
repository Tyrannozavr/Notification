from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from notifications.routes import render_notification
from notifications.services import render_notification_list, Notification, get_all_notifications, TagSearch
from services.requests import auth_request

notification_router = Router()


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
