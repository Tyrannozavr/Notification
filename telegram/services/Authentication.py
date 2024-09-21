from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    username = State()
    password = State()


async def set_access_token(token, state: FSMContext):
    await state.update_data({'token': token})
    return state

async def get_access_token(state: FSMContext):
    data = await state.get_data()
    return data.get('token', None)
