
from aiogram import F, types
from aiogram.fsm.context import FSMContext


def register_notification_callback_query(dp):
    @dp.callback_query(F.data.startswith("delete:"))
    async def delete_notification_callback(callback: types.CallbackQuery, state: FSMContext):
        notification_id = callback.data.split(':')[1]
        return await callback.message.answer(text=f"Удалено {notification_id}")
