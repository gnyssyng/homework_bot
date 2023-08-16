class IncorrectResponse(Exception):
    """Возникает при неверном  ответе API."""

    pass


class MissingToken(Exception):
    """Возникает при отсутсвии одного из токенов."""

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


class MissingKey(Exception):
    """Возникает при отсуствии одного из ключей словаря."""

    pass


class ResponseHaveNoData(Exception):
    """Возникает при отсуствии данных в словаре."""

    pass
