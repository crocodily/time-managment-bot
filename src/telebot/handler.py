from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from src.telebot.messages import Messages
from src.telebot.states import InitialStates, UpdateTimeReportStates


async def init_dispatcher(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            BotCommand(command='start', description='Начальная команда'),
            BotCommand(command='help', description='Помощь'),
            BotCommand(
                command='change_report_time',
                description='Изменить время получения отчета',
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
    dp.register_message_handler(process_markup_for_auth, commands=['accounts'])
    dp.register_message_handler(process_set_report_time_command, commands=['change_report_time'])
    dp.register_message_handler(
        process_initial_time_for_report, state=InitialStates.time_for_report
    )
    dp.register_message_handler(
        process_update_time_for_report, state=UpdateTimeReportStates.update_time_for_report
    )


async def process_callback_github(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Авторизоваться', url="https://www.ya.ru"))
    await callback_query.message.answer(
        'Авторизуйтесь в GitHub по ссылке:',
        reply_markup=inline_kb
    )


async def process_callback_vk(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Авторизоваться', url="https://www.ya.ru"))
    await callback_query.message.answer(
        text='Авторизуйтесь в VK по ссылке:',
        reply_markup=inline_kb
    )


async def process_callback_done(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer('Вы закончили настройку аккаунтов')
    await callback_query.message.edit_reply_markup()


async def process_start_command(message: types.Message) -> None:
    await InitialStates.time_for_report.set()
    await message.reply(Messages.time_for_report.value, reply=False)


async def process_help_command(message: types.Message) -> None:
    await message.reply(Messages.help.value, reply=False)


async def process_set_report_time_command(message: types.Message) -> None:
    await UpdateTimeReportStates.update_time_for_report.set()
    await message.reply(Messages.time_for_report.value, reply=False)


async def process_initial_time_for_report(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь сохраняем время отчета для пользователя message.from_user.id

    await state.finish()
    text = Messages.report_time_is.value + message.text
    await message.reply(text, reply=False)
    await process_markup_for_auth(message)


async def process_update_time_for_report(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text

    # здесь обновляем время отчета для пользователя message.from_user.id

    await state.finish()
    text = f"{Messages.report_time_is.value} {message.text}"
    await message.reply(text, reply=False)


async def process_markup_for_auth(message: types.Message) -> None:
    exist = False  # получаем существуют ли настроенные аккаунты
    if exist:
        # создаем текст сообщения со списком существующих аккаунтов
        text = f"{Messages.existing_accounts.value}\n"
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
