from aiogram.fsm.context import FSMContext

from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram.notifications.services import register_notification_callback_query
from telegram.services.notifications import notifications_list_view, Notification, get_all_notifications
from telegram.services.server import post_auth_request, auth_request


def register_notification_handlers(dp):
    register_notification_callback_query(dp)

    @dp.message(F.text == 'Удалить уведомление')
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
        response = await auth_request(url='notifications/', data=data, state=state,
                                      user_data=message.from_user.__dict__, type='post')
        if isinstance(response, str):
            return await message.answer(response)
        else:
            if response.status_code == 201:
                await state.clear()
                return await message.answer('Создано успешно')
            else:
                return await message.answer(response.text)

    @dp.message(F.text == 'Показать все уведомления')
    async def notification_list(message: Message, state: FSMContext):
        notifications = await notifications_list_view(state=state, user_data=message.from_user.__dict__)
        if isinstance(notifications, str):
            return await message.answer(notifications)
        if notifications:
            return await message.answer("\n".join(notifications))
        else:
            return await message.answer("Нет уведомлений.")

    @dp.message(F.text == 'Редактировать уведомление')
    async def editable_notification_list(message: Message, state: FSMContext):
        notifications = await get_all_notifications(state=state, user_data=message.from_user.__dict__)
        buttons = []
        for notification in notifications:
            button = InlineKeyboardButton(text=f"{notification.get('id')} {notification.get('title')}",
                                          callback_data=f"edit:{notification.get('id')}")
            buttons.append(button)

        builder = InlineKeyboardBuilder()
        builder.row(*buttons, width=1)

        return await message.answer('выберите какое уведомление удалить', reply_markup=builder.as_markup())
