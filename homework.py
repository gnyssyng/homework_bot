import logging
import os
import sys
import time
from http import HTTPStatus
from os.path import abspath

import requests
import telegram
import exceptions

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abspath('log.log'), encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

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
    TOKENS = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'CHAT_ID': TELEGRAM_CHAT_ID
    }
    unobtainable_tokens = []
    logger.debug('Начинается проверка токенов')
    for token in TOKENS:
        if TOKENS[token] is None:
            logger.critical(f'Отсутсвует {token}.')
            unobtainable_tokens.append(token)
    if not unobtainable_tokens:
        logger.debug('Пройдена проверка токенов.')
    else:
        logger.critical(f'Отсутсвуют следующие токены:{unobtainable_tokens}')
        raise exceptions.MissingToken(
            f'Отсутсвуют необходимые токены.{unobtainable_tokens}'
        )


def send_message(bot, message):
    """Функция отправляет сообщение через телеграм-бота."""
    logger.debug('Начинаем отправлять сообщение.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение успешно отправлено.')
    except telegram.error.TelegramError as error:
        raise exceptions.MessageError(
            f'Не удалость отправить сообщение:{error}'
        )


def get_api_answer(timestamp):
    """Функция получает ответ API."""
    playload = {'from_date': timestamp}
    requset_data = {
        'URL': ENDPOINT,
        'headers': HEADERS,
        'params': playload
    }
    logger.debug(
        'Начался запрос к API.\n'
        'Адрес запроса: {URL}\n'
        'Заголовки: {headers}\n'
        'Параметры: {params}\n'.format(
            URL=requset_data['URL'],
            headers=requset_data['headers'],
            params=requset_data['params']
        )
    )
    try:
        response = requests.get(
            requset_data['URL'],
            headers=requset_data['headers'],
            params=requset_data['params']
        )
    except requests.RequestException('Не удалось совершить запрос к API'):
        pass
    if response.status_code != HTTPStatus.OK:
        raise exceptions.IncorrectStatusCode('Неверный код ответа API.')
    logger.debug('Получен ответ от API.')
    return response.json()


def check_response(response):
    """Функция проверяет ответ API."""
    logger.debug('Начинается проверка ответа API.')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарём.')
    if 'homeworks' not in response:
        raise exceptions.HomeworkIsNotInResponse
    if 'current_date' not in response:
        raise exceptions.CurrentDateIsNotInResponse
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(
            'Некорректная структура данных, '
            'находящихся под ключом "homeworks".'
        )
    return homeworks


def parse_status(homework):
    """Функция возрващает сообщение о статусе домашней работы."""
    if 'homework_name' not in homework:
        raise exceptions.HomeworkNameIsNotInHomework(
            'Отсутсвует ключ "homework_name".'
        )
    if 'status' not in homework:
        raise exceptions.StatusIsNotInHomework(
            'Отсутсвует ключ "status".'
        )
    if homework.get('status') not in HOMEWORK_VERDICTS:
        raise exceptions.IncorrectResponse(
            'Недокументированный статус домашней работы.'
        )
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    current_report = {
        'name': None,
        'messages': None,
    }
    prev_report = {
        'name': None,
        'messages': None,
    }

    while True:
        try:
            response = get_api_answer(timestamp)
            if not response['current_date']:
                timestamp = response['current_date']
            response = check_response(response)
            last_hw = -len(response)
            current_report['name'] = response[last_hw]['homework_name']
            current_report['messages'] = parse_status(response[last_hw])
            logger.debug('Отчёт о домашней работе записан в current_report.')
            if len(response) > 0:
                if current_report != prev_report:
                    try:
                        send_message(bot, current_report['messages'])
                    except telegram.error.TelegramError as error:
                        logger.error(
                            f'Сбой при попытке отправки сообщения {error}'
                        )
                    prev_report = current_report.copy()
                    logger.debug(
                        'Отчёт о домашней работе записан в prev_report.'
                    )
            else:
                logger.error('Пустой ответ API.')
                raise exceptions.ResponseHaveNoData('Пустой словарь ответа')
        except Exception as error:
            logger.error(f'Сбой в работе программы {error}')
            current_report['name'] = error
            current_report['messages'] = 'Cбой в работе программы'
            logger.debug('Отчёт об ошибке записан в current_report.')
            if current_report != prev_report:
                send_message(bot, current_report['messages'])
                prev_report = current_report.copy()
                logger.debug('Отчёт об ошибке скопирован в prev_report.')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
