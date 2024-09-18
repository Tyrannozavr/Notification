from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.notifications import NotificationEdit
from services.server import auth_request



notification_dictionary = {
    "title": "Заголовок",
    "description": "Описание",
    "tags": "Тэги",
}


def register_notification_callback_query(dp):
    @dp.callback_query(F.data.startswith("delete:"))
    async def delete_notification_callback(callback: types.CallbackQuery, state: FSMContext):
        notification_id = callback.data.split(':')[1]
        await auth_request(url=f'notifications/{notification_id}', data={}, state=state,
                           user_data=callback.from_user.__dict__, type='delete')
        return await callback.message.answer(text=f"Удалено {notification_id}")

    @dp.callback_query(F.data.startswith("edit:"))
    async def edit_notification_callback(callback: types.CallbackQuery, state: FSMContext):
        notification_id = callback.data.split(':')[1]
        response = await auth_request(url=f'notifications/get/{notification_id}', data={}, state=state,
                                      user_data=callback.from_user.__dict__, type='get')
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

    @dp.callback_query(F.data.startswith("edit_"))
    async def edit_notification_part_callback(callback: types.CallbackQuery, state: FSMContext):
        notification_data = callback.data.split('_')[1]
        notification_key, notification_id = notification_data.split(':')
        NotificationEdit.id = notification_id
        await callback.message.answer(f'Введите новый {notification_dictionary.get(notification_key)}')
        NotificationEdit.key = notification_key
        await state.set_state(NotificationEdit.value)

    @dp.message(NotificationEdit.value)
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
        response = await auth_request(url=f'notifications/{notification_id}/', data=data, state=state,
                                      user_data=message.from_user.__dict__, type='patch')
        if response.status_code == 200:
            notification = response.json()
            response = (f"Успешно отредактировано! \n"
                        f"Заголовок: {notification.get('title')} \n"
                        f"Описание: {notification.get('description')} \n"
                        f"Тэги: {' '.join([tag.get('name') for tag in notification.get('tags', [])])}")
            return message.answer(response)
        else:
            return message.answer(response.text)

def render_notification(notification: dict) -> str:
    return (f"{notification.get('title')} \n "
            f"{notification.get('description')} \n"
            f"{[tag.get('name') for tag in notification.get('tags')]}")
