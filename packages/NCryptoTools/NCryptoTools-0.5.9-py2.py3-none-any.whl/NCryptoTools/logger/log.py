# -*- coding: utf-8 -*-
"""
Определяет класс-декоратор для логирования функций
"""
import logging
from functools import wraps


class Log:
    """
    Класс-декоратор для логирования функций.
    """

    def __init__(self, logger_instance, level=logging.INFO):
        """
        Запоминает логгер, чтобы была возможность использовать разные.
        @param logger_instance: сущность класса-логгера.
        @param level: уровень лога.
        """
        self._logger = logger_instance
        self._level = level

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """
        Формирует сообщение для записи в лог.
        @param result: результат работы функции.
        @param args: любые параметры в форме листа.
        @param kwargs: любые параметры в форме словаря.
        @return: сконкатенированная строка со всеми параметрами/результатами.
        """
        message = ''
        if args:
            message += 'args: {} '.format(args)
        if kwargs:
            message += 'kwargs: {} '.format(kwargs)
        if result:
            message += '= {}'.format(result)
        return message

    def __call__(self, func):
        """
        Метод, который вызывается при вызове задекорированной функции.
        @param func: ссылка/указатель на функцияю, которую нужно задекорировать.
        @return: ссылка/указатель на функцию-обёртку.
        """
        @wraps(func)
        def wrapped(*args, **kwargs):
            """
            Функция-обёртка вокруг исходной функции
            @param args: любые параметры в форме листа.
            @param kwargs: любые параметры в форме словаря.
            @return: результат выполнения исходной функции.
            """
            result = func(*args, **kwargs)
            message = Log._create_message(result, *args, **kwargs)

            # Пишем сообщение в лог
            self._logger.log_msg(self._level,
                                 '{} - {} - {}'.format(message,
                                                       wrapped.__name__,
                                                       wrapped.__module__))
            return result
        return wrapped
