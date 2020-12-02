from aiogram.dispatcher.filters.state import State, StatesGroup


class StateSetReportTime(StatesGroup):
    time_for_report = State()
