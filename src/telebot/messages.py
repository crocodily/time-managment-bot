from enum import Enum


class Messages(Enum):
    start = "Hello, I'm your time manager!",
    help = "Я тебе помогу",
    report = "Твой отчет: ",
    time_for_report = "Укажи время, в которое ты хочешь получать отчет:",
    done = "Выполнено!",
    unknown = "Прости, я не понял :(\nПопробуй ещё раз или обратись за помощью к @Puzanovim ;)",
    set_accounts = "Настройка аккаунтов:\n"
