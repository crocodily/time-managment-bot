from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup


from src.telebot.messages import Messages
from src.telebot.States.setTimeStates import StateSetReportTime
from src.telebot.States.setAccountStates import StateSetAccounts


TOKEN = ""
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.callback_query_handler(text="github")
async def process_callback_github(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Авторизуйтесь в GitHub по ссылке:\nhttps://www.ya.ru")


@dp.callback_query_handler(text="jira")
async def process_callback_jira(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Авторизуйтесь в Jira по ссылке:\nhttps://www.ya.ru")


@dp.callback_query_handler(text="vk")
async def process_callback_vk(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Авторизуйтесь в VK по ссылке:\nhttps://www.ya.ru")


@dp.callback_query_handler(text="discord")
async def process_callback_discord(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Авторизуйтесь в Discord по ссылке:\nhttps://www.ya.ru")


@dp.callback_query_handler(text="zoom")
async def process_callback_zoom(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Авторизуйтесь в Zoom по ссылке:\nhttps://www.ya.ru")


@dp.callback_query_handler(text="done")
async def process_callback_done(callback_query: types.CallbackQuery):
    await callback_query.answer(cache_time=20)
    await callback_query.message.answer("Вы закончили настройку аккаунтов")
    await callback_query.message.edit_reply_markup()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await StateSetReportTime.time_for_report.set()
    await message.reply(Messages.start, reply=False)
    await message.reply(Messages.time_for_report, reply=False)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(Messages.help, reply=False)


@dp.message_handler(state=StateSetReportTime.time_for_report)
async def process_work_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['work_time'] = message.text

    await state.finish()
    await message.reply(Messages.done, reply=False)

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('GitHub', callback_data='github'),
                InlineKeyboardButton('Jira', callback_data='jira'),
                InlineKeyboardButton('VK', callback_data='vk')
            ],
            [
                InlineKeyboardButton('Discord', callback_data='discord'),
                InlineKeyboardButton('Zoom', callback_data='zoom')
            ],
            [
                InlineKeyboardButton('Готово', callback_data='done')
            ]
        ]
    )

    await message.reply(Messages.set_accounts, reply_markup=inline_kb, reply=False)


@dp.message_handler(state=StateSetAccounts.account)
async def process_work_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['work_time'] = message.text

    await state.finish()
    await message.reply(Messages.done, reply=False)
    await message.reply(Messages.help, reply=False)


@dp.message_handler()
async def echo_message(message: types.Message):
    await message.reply(Messages.unknown, reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
