from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from src.telebot.messages import Messages
from src.telebot.states import InitialStates


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
    dp.register_message_handler(
        process_time_for_report, state=InitialStates.time_for_report
    )


async def process_callback_github(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer(
        'Авторизуйтесь в GitHub по ссылке:\nhttps://www.ya.ru'
    )


async def process_callback_vk(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer(
        'Авторизуйтесь в VK по ссылке:\nhttps://www.ya.ru'
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


async def process_time_for_report(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['work_time'] = message.text
    await InitialStates.next()
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('GitHub', callback_data='github'),
                InlineKeyboardButton('VK', callback_data='vk'),
            ],
            [InlineKeyboardButton('Готово', callback_data='done')],
        ]
    )

    await message.reply(
        Messages.set_accounts.value, reply_markup=inline_kb, reply=False
    )
