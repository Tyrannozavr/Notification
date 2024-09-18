from aiogram import F, types
from aiogram.fsm.context import FSMContext

from telegram.services.server import auth_request


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
        response = await auth_request(url=f'notifications/{notification_id}', data={}, state=state,
                                          user_data=callback.from_user.__dict__, type='get')
        if response.status_code == 200:
            notification = response.json()
            print('edit', notification)
            return await callback.message.answer(text=f"Изменить {notification_id}")
        else:
            return await callback.message.answer(text=response.text)
