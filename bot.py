from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


from config import TOKEN
from messages import MESSAGES

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'], reply=False)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'], reply=False)


@dp.message_handler()
async def echo_message(message: types.Message):
    if message.text in MESSAGES.keys():
        text = MESSAGES[message.text]
    else:
        text = MESSAGES['unknown']
    await message.reply(text, reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
