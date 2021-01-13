from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData


time_callback = CallbackData("counter", "state", "time")
done_callback = CallbackData("done", "state", "time")


def get_time_keyboard(hours: int, minutes: int, state: str):

    hours_down = hours - 1
    hours_up = hours + 1
    minutes_down = minutes - 15
    minutes_up = minutes + 15

    if hours_down < 0:
        hours_down = 23
    if hours_up > 23:
        hours_up = 0
    if minutes_down < 0:
        minutes_down = 45
    if minutes_up > 45:
        minutes_up = 0

    hours_down_text = f"counter:{state}:{hours_down}.{minutes}"
    hours_up_text = f"counter:{state}:{hours_up}.{minutes}"
    minutes_down_text = f"counter:{state}:{hours}.{minutes_down}"
    minutes_up_text = f"counter:{state}:{hours}.{minutes_up}"
    done_text = f"done:{state}:{hours}.{minutes}"

    time_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(f'{hours}', callback_data='hour'),
                InlineKeyboardButton(f'{minutes}', callback_data='minute'),
            ],
            [
                InlineKeyboardButton('-', callback_data=hours_down_text),
                InlineKeyboardButton('+', callback_data=hours_up_text),
                InlineKeyboardButton('-', callback_data=minutes_down_text),
                InlineKeyboardButton('+', callback_data=minutes_up_text),
            ],
            [
                InlineKeyboardButton('Готово', callback_data=done_text)
            ]
        ]
    )
    return time_keyboard


def get_accounts_keyboard(accounts: list):
    accounts_buttons = []
    for account in accounts:
        accounts_buttons.append(InlineKeyboardButton(f"{account}", callback_data=f"{account}".lower()))

    accounts_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            accounts_buttons,
            [
                InlineKeyboardButton('Готово', callback_data='done_accounts')
            ],
        ]
    )
    return accounts_kb


def get_inline_keyboard_with_link(text: str, link: str):
    inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text, url=link))
    return inline_kb


def get_reply_keyboard(text: str):
    keyboard = ReplyKeyboardMarkup().add(KeyboardButton(text))
    return keyboard


def get_time_dict_from_str(callback_str: str):
    time = callback_str.split(".")
    hours = int(time[0])
    minutes = int(time[1])

    if -1 < hours < 10:
        hours = f"0{hours}"
    if -1 < minutes < 10:
        minutes = f"0{minutes}"

    return {"hours": hours, "minutes": minutes}
