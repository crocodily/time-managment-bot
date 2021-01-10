from enum import Enum


class Messages(Enum):
    start = "Hello, I'm your time manager!"
    help = 'Я тебе помогу'
    report = 'Твой отчет:'
    start_work_time = 'Укажи время, в которое ты начинаешь рабочий день:'
    end_work_time = 'Укажи время, в которое ты заканчиваешь рабочий день:'
    done = 'Выполнено!'
    set_accounts = (
        'Привяжите ваши аккаунты для того, чтобы мы могли следить за вашей активностью:'
    )
    existing_accounts = 'Подключенные аккаунты:'
    time_is = 'время:'
    end_set_accounts = 'Вы закончили настройку аккаунтов'
    auth_github = 'Авторизуйтесь в GitHub по ссылке:'
    auth_vk = 'Авторизуйтесь в VK по ссылке:'
    start_time = 'Время начала рабочего дня:'
    end_time = 'Время конца рабочего дня:'
