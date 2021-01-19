from aiogram import Bot

from src import URI


async def send_report_message(bot: Bot, user_id: int, telegram_id: int) -> None:
    await bot.send_message(telegram_id, text=f'Ваш отчёт готов: {URI}/report_page/{user_id}')