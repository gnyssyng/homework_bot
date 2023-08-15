import logging
import os
import time

import exceptions
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет валидность токенов."""
    if PRACTICUM_TOKEN is None:
        logging.critical('Отсутсвует токен практикума.')
        raise exceptions.PracticumTokenErorr
    elif TELEGRAM_TOKEN is None:
        logging.critical('Отсутсвует токен телеграм-бота.')
        raise exceptions.TelegramBotTokenError
    elif TELEGRAM_CHAT_ID is None:
        logging.critical('Отсутсвует chat_id.')
        raise exceptions.InvalidChatId


def send_message(bot, message):
    """Функция отправляет сообщение через телеграм-бота."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение успешно отправлено.')
    except telegram.error.TelegramError as error:
        logging.error(f'Не удалось отправить сообщение{error}')
        raise exceptions.MessageError


def get_api_answer(timestamp):
    """Функция получает ответ API."""
    playload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=playload
        )
    except requests.RequestException:
        logging.error('Возникла ошибка при попытке получения ответа API.')
    if response.status_code != 200:
        logging.error(f'Неверный код ответа API.{response.status_code}')
        raise exceptions.IncorrectStatusCode
    return response.json()


def check_response(response):
    """Функция проверяет ответ API."""
    if type(response) is not dict:
        logging.error('Некорректная структура данных ответа API.')
        raise TypeError
    if 'homeworks' not in response:
        raise exceptions.HomeworkIsNotInResponse
    if 'current_date' not in response:
        raise exceptions.CurrentDateIsNotInResponse
    if type(response['homeworks']) is not list:
        logging.error(
            'Некорректная структура данных, '
            'находящихся под ключом "homeworks".'
        )
        raise TypeError


def parse_status(homework):
    """Функция возрващает сообщение о статусе домашней работы."""
    if 'homework_name' not in homework:
        logging.error('Отсутсвует ключ "homework_name".')
        raise exceptions.HomeworkNameIsNotInHomework
    if 'status' not in homework:
        logging.error('Отсутсвует ключ "status".')
        raise exceptions.StatusIsNotInHomework
    if homework.get('status') not in HOMEWORK_VERDICTS:
        logging.error('Недокументированный статус домашней работы.')
        raise exceptions.IncorrectResponse
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0

    while True:
        try:
            response = get_api_answer(timestamp)
            if isinstance(response, dict) is False:
                raise TypeError(
                    'Структура данных ответа API не соответсвует ожидаемой'
                )
            check_response(response)
            response = response['homeworks']
            send_message(bot, parse_status(response[-len(response)]))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
