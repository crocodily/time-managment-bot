from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from src.telebot.messages import Messages
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
    dp.register_callback_query_handler(process_callback_done, text='done')
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(process_help_command, commands=['help'])
    dp.register_message_handler(process_set_accounts, commands=['accounts'])
    dp.register_message_handler(process_change_work_time, commands=['change_work_time'])
    dp.register_message_handler(
        process_initial_start_work_time, state=InitialStates.start_work_time
    )
    dp.register_message_handler(
        process_initial_end_work_time, state=InitialStates.end_work_time
    )
    dp.register_message_handler(
        process_update_start_work_time,
        state=UpdateWorkTimeStates.update_start_work_time,
    )
    dp.register_message_handler(
        process_update_end_work_time, state=UpdateWorkTimeStates.update_end_work_time
    )


async def process_callback_github(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Авторизоваться', url='https://www.ya.ru')
    )
    await callback_query.message.answer(
        text=Messages.auth_github.value, reply_markup=inline_kb
    )


async def process_callback_vk(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Авторизоваться', url='https://www.ya.ru')
    )
    await callback_query.message.answer(
        text=Messages.auth_vk.value, reply_markup=inline_kb
    )


async def process_callback_done(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer(Messages.end_set_accounts.value)
    await callback_query.message.edit_reply_markup()


async def process_start_command(message: types.Message) -> None:
    await InitialStates.start_work_time.set()
    await message.reply(Messages.start_work_time.value, reply=False)


async def process_help_command(message: types.Message) -> None:
    await message.reply(Messages.help.value, reply=False)


async def process_change_work_time(message: types.Message) -> None:
    await UpdateWorkTimeStates.update_start_work_time.set()
    await message.reply(Messages.start_work_time.value, reply=False)


async def process_initial_start_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь сохраняем время начала рабочего дня для пользователя message.from_user.id

    await InitialStates.next()
    confirm_time = f'{Messages.start_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await message.reply(Messages.end_work_time.value, reply=False)


async def process_initial_end_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь сохраняем время конца рабочего дня для пользователя message.from_user.id

    await state.finish()
    confirm_time = f'{Messages.end_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await process_set_accounts(message)


async def process_update_start_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь обновляем время начала рабочего дня для пользователя message.from_user.id

    await UpdateWorkTimeStates.next()
    confirm_time = f'{Messages.start_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)
    await message.reply(Messages.end_work_time.value, reply=False)


async def process_update_end_work_time(
    message: types.Message, state: FSMContext
) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь обновляем время отчета для пользователя message.from_user.id

    await state.finish()
    confirm_time = f'{Messages.end_time.value} {message.text}'
    await message.reply(confirm_time, reply=False)


async def process_set_accounts(message: types.Message) -> None:
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
                    InlineKeyboardButton('GitHub', callback_data='github'),
                    InlineKeyboardButton('VK', callback_data='vk'),
                ],
                [InlineKeyboardButton('Готово', callback_data='done')],
            ]
        )

        await message.reply(
            Messages.set_accounts.value, reply_markup=accounts_kb, reply=False
        )
