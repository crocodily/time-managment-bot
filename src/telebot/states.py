from aiogram.dispatcher.filters.state import State, StatesGroup


class InitialStates(StatesGroup):
    start_work_time = State()
    end_work_time = State()


class UpdateWorkTimeStates(StatesGroup):
    update_start_work_time = State()
    update_end_work_time = State()
