from aiogram.dispatcher.filters.state import State, StatesGroup


class InitialStates(StatesGroup):
    time_for_report = State()
