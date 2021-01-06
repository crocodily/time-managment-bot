from enum import Enum


class Messages(Enum):
    start = "Hello, I'm your time manager!"
    help = 'Я тебе помогу'
    report = 'Твой отчет: '
    time_for_report = 'Укажи время, в которое ты хочешь получать отчет:'
    done = 'Выполнено!'
    set_accounts = (
        'Привяжите ваши аккаунты для того, чтобы '
        'мы могли следить за вашей активностью:'
    )
