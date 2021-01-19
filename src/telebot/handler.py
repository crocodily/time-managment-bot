import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from src.services.common import (
    create_user_if_not_exists,
    save_user_day_end_time,
    save_user_day_start_time,
)
from src.services.github.github import generate_github_auth_link
from src.services.vk.vk import generate_vk_auth_link
from src.singletones import engine
from src.telebot.inline_keyboards import get_inline_keyboard_with_link, get_time_keyboard, \
    time_callback, done_callback, get_accounts_keyboard, get_time_dict_from_str
from src.telebot.enums import Messages, get_all_accounts
from src.telebot.states import InitialStates, UpdateWorkTimeStates


async def init_dispatcher(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            BotCommand(command='start', description='Начальная команда'),
            BotCommand(command='help', description='Помощь'),
            BotCommand(
                command='change_work_time',
                description='Изменить рабочее время',
            ),
            BotCommand(command='accounts', description='Привязка аккаунтов'),
        ]
    )
    _register_handlers(dp)


def _register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(process_callback_github, text='github')
    dp.register_callback_query_handler(process_callback_vk, text='vk')
    dp.register_callback_query_handler(process_callback_done_accounts, text='done_accounts')
    dp.register_callback_query_handler(process_callback_time, time_callback.filter())
    dp.register_callback_query_handler(process_callback_done_start,
                                       done_callback.filter(state="start"))
    dp.register_callback_query_handler(process_callback_done_update_start,
                                       done_callback.filter(state="update_start"))
    dp.register_callback_query_handler(process_callback_done_finish,
                                       done_callback.filter(state="finish"))
    dp.register_callback_query_handler(process_callback_done_update_finish,
                                       done_callback.filter(state="update_finish"))
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(process_help_command, commands=['help'])
    dp.register_message_handler(process_set_accounts, commands=['accounts'])
    dp.register_message_handler(process_change_work_time, commands=['change_work_time'])
    dp.register_message_handler(
        process_initial_start_work_time,
        state=InitialStates.start_work_time
    )
    dp.register_message_handler(
        process_initial_end_work_time,
        state=InitialStates.end_work_time
    )
    dp.register_message_handler(
        process_update_start_work_time,
        state=UpdateWorkTimeStates.update_start_work_time,
    )
    dp.register_message_handler(
        process_update_end_work_time,
        state=UpdateWorkTimeStates.update_end_work_time
    )


async def process_callback_github(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = get_inline_keyboard_with_link("Авторизоваться", "https://www.ya.ru")
    await callback_query.message.answer(
        text=Messages.auth_github.value,
        reply_markup=inline_kb
    )


async def process_callback_vk(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = get_inline_keyboard_with_link("Авторизоваться", "https://www.ya.ru")
    await callback_query.message.answer(
        text=Messages.auth_vk.value,
        reply_markup=inline_kb
    )


async def process_callback_done_accounts(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer(Messages.end_set_accounts.value)


async def process_callback_time(callback_query: CallbackQuery, callback_data: dict) -> None:
    await callback_query.answer(cache_time=10)
    state = callback_data.get("state")
    time = get_time_dict_from_str(str(callback_data.get("time")))
    await callback_query.message.edit_reply_markup(
        get_time_keyboard(int(time["hours"]), int(time["minutes"]), state, callback_data['user_id']))


async def process_callback_done_start(callback_query: CallbackQuery, callback_data: dict) -> None:
    await callback_query.answer(cache_time=10)
    time = get_time_dict_from_str(str(callback_data.get("time")))

    async with engine.acquire() as conn:
        await save_user_day_start_time(callback_data['user_id'], f"{time['hours']}:{time['minutes']}", conn)

    await callback_query.message.edit_reply_markup()
    confirm_time = f"{Messages.start_time.value} {time['hours']}:{time['minutes']}"
    await callback_query.message.answer(text=confirm_time)
    await callback_query.message.answer(Messages.end_work_time.value,
                                        reply_markup=get_time_keyboard(18, 0, "finish", callback_data['user_id']),
                                        reply=False)


async def process_callback_done_update_start(callback_query: CallbackQuery, callback_data: dict) -> None:
    await callback_query.answer(cache_time=10)
    time = get_time_dict_from_str(str(callback_data.get("time")))

    # обновили налаго рабочего дня

    await callback_query.message.edit_reply_markup()
    confirm_time = f"{Messages.start_time.value} {time['hours']}:{time['minutes']}"
    await callback_query.message.answer(text=confirm_time)
    await callback_query.message.answer(Messages.end_work_time.value,
                                        reply_markup=get_time_keyboard(18, 0, "update_finish", callback_data['user_id']),
                                        reply=False)


async def process_callback_done_finish(callback_query: CallbackQuery, callback_data: dict) -> None:
    await callback_query.answer(cache_time=10)
    time = get_time_dict_from_str(str(callback_data.get("time")))

    async with engine.acquire() as conn:
        await save_user_day_end_time(callback_data['user_id'], f"{time['hours']}:{time['minutes']}", conn)

    await callback_query.message.edit_reply_markup()
    confirm_time = f"{Messages.end_time.value} {time['hours']}:{time['minutes']}"
    await callback_query.message.answer(text=confirm_time)
    await process_set_accounts(callback_query.message, callback_data['user_id'])


async def process_callback_done_update_finish(callback_query: CallbackQuery, callback_data: dict) -> None:
    await callback_query.answer(cache_time=10)
    time = get_time_dict_from_str(str(callback_data.get("time")))

    # обновили окончание рабочего дня

    await callback_query.message.edit_reply_markup()
    confirm_time = f"{Messages.end_time.value} {time['hours']}:{time['minutes']}"
    await callback_query.message.answer(text=confirm_time)
    await callback_query.message.answer(text=Messages.success_update_time.value)


async def process_start_command(message: types.Message) -> None:
    time_keyboard = get_time_keyboard(10, 0, "start", message.from_user.id)
    await message.reply(Messages.start_work_time.value, reply_markup=time_keyboard, reply=False)
    async with engine.acquire() as conn:
        await create_user_if_not_exists(message.from_user.id, conn)


async def process_help_command(message: types.Message) -> None:
    await message.reply(Messages.help.value, reply=False)


async def process_change_work_time(message: types.Message) -> None:
    time_keyboard = get_time_keyboard(0, 0, "update_start", message.from_user.id)
    await message.reply(Messages.start_work_time.value, reply_markup=time_keyboard, reply=False)


async def process_initial_start_work_time(
    message: types.Message, state: FSMContext
) -> None:

    await InitialStates.next()
    confirm_time = f'{Messages.start_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await message.reply(Messages.end_work_time.value, reply=False)


async def process_initial_end_work_time(
    message: types.Message, state: FSMContext
) -> None:

    # здесь сохраняем время конца рабочего дня для пользователя message.from_user.id

    await state.finish()
    confirm_time = f'{Messages.end_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await process_set_accounts(message)


async def process_update_start_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with engine.acquire() as conn:
        await save_user_day_start_time(message.from_user.id, message.text, conn)

    # здесь обновляем время начала рабочего дня для пользователя message.from_user.id

    await UpdateWorkTimeStates.next()
    confirm_time = f'{Messages.start_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await message.reply(Messages.end_work_time.value, reply=False)


async def process_update_end_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with engine.acquire() as conn:
        await save_user_day_end_time(message.from_user.id, message.text, conn)

    # здесь обновляем время отчета для пользователя message.from_user.id

    await state.finish()
    confirm_time = f'{Messages.end_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)


async def process_set_accounts(message: types.Message, user_id: str) -> None:
    github_auth_link = generate_github_auth_link(int(user_id))
    vk_auth_link = generate_vk_auth_link(int(user_id))
    exist = False  # получаем существуют ли настроенные аккаунты

    if exist:
        # создаем текст сообщения со списком существующих аккаунтов
        text = f'{Messages.existing_accounts.value}\n'
        await message.reply(text, reply=False)
        # клавиатура аккаунтов без подключенных
        accounts_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton('GitHub', callback_data='github'),
                    InlineKeyboardButton('VK', callback_data='vk'),
                ],
                [InlineKeyboardButton('Готово', callback_data='done')],
            ]
        )

        await message.reply(
            Messages.set_accounts.value, reply_markup=accounts_kb, reply=False
        )
    else:
        accounts_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        'GitHub', callback_data='github', url=github_auth_link
                    ),
                    InlineKeyboardButton('VK', callback_data='vk', url=vk_auth_link),
                ],
                [InlineKeyboardButton('Готово', callback_data='done')],
            ]
        )

        await message.reply(
            Messages.set_accounts.value, reply_markup=accounts_kb, reply=False
        )
