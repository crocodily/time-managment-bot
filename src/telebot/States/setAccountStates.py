from aiogram.dispatcher.filters.state import State, StatesGroup


class StateSetAccounts(StatesGroup):
    account = State()
