class APIIsNotAvaliable(Exception):
    """Возникает, если API недоступен."""

    pass


class IncorrectResponse(Exception):
    """Возникает при неверном  ответе API."""

    pass


class PracticumTokenErorr(Exception):
    """Возниает при отсутсвии токена практикума."""

    pass


class TelegramBotTokenError(Exception):
    """Возниает при отутствии токена телеграм-бота."""

    pass


class InvalidChatId(Exception):
    """Возниает при неверном chat_id."""

    pass


class MessageError(Exception):
    """Возникает при неудачной попытке отправки сообщения."""

    pass


class HomeworkIsNotInResponse(Exception):
    """Возниакет при отсутсвии ключа 'homeworks' в ответе API."""

    pass


class CurrentDateIsNotInResponse(Exception):
    """Возниакет при отсутсвии ключа 'current_date' в ответе API."""

    pass


class HomeworkNameIsNotInHomework(Exception):
    """Возникает при отсутсвии ключа 'homework_name'."""

    pass


class StatusIsNotInHomework(Exception):
    """Возникает при отсутсвии ключа 'homework_name'."""

    pass


class IncorrectStatusCode(Exception):
    """Возникает при неверном статусе ответа API."""

    pass
