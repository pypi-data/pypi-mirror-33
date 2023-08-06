# -*- coding: utf-8 -*-
"""
Логгер

Возможные настройки для форматирования:
-----------------------------------------------------------------------------
| Формат         | Описание
-----------------------------------------------------------------------------
| %(name)s       | Имя регистратора.
| %(levelno)s    | Числовой уровень важности.
| %(levelname)s  | Символическое имя уровня важности.
| %(pathname)s   | Путь к исходному файлу, откуда была выполнена запись в журнал.
| %(filename)s   | Имя исходного файла, откуда была выполнена запись в журнал.
| %(funcName)s   | Имя функции, выполнившей запись в журнал.
| %(module)s     | Имя модуля, откуда была выполнена запись в журнал.
| %(lineno)d     | Номер строки, откуда была выполнена запись в журнал.
| %(created)f    | Время, когда была выполнена запись в журнал. Значением
|                | должно быть число, такое как возвращаемое функцией time.time().
| %(asctime)s    | Время в формате ASCII, когда была выполнена запись в журнал.
| %(msecs)s      | Миллисекунда, когда была выполнена запись в журнал.
| %(thread)d     | Числовой идентификатор потока выполнения.
| %(threadName)s | Имя потока выполнения.
| %(process)d    | Числовой идентификатор процесса.
| %(message)s    | Текст журналируемого сообщения (определяется пользователем).
-----------------------------------------------------------------------------

Возможные уровни логгирования:
-----------------------------------------------------------------------------
| Уровень важности | Использование
-----------------------------------------------------------------------------
| CRITICAL         | log.critical(fmt [, *args [, exc_info [, extra]]])
| ERROR            | log.error(fmt [, *args [, exc_info [, extra]]])
| WARNING          | log.warning(fmt [, *args [, exc_info [, extra]]])
| INFO             | log.info(fmt [, *args [, exc_info [, extra]]])
| DEBUG            | log.debug(fmt [, *args [, exc_info [, extra]]])
-----------------------------------------------------------------------------
"""
import logging
import logging.handlers


class UnknownLogLevelError(Exception):
    def __init__(self, log_level):
        """
        Конструктор. Создаёт экземпляр исключения для оповещения пользователя,
        что он передал некорректное значение уровня лога.
        @param log_level: ошибочный уровень лога.
        """
        self.log_level = log_level

    def __str__(self):
        """
        Придаёт читаемость ошибке.
        @return: строка с оповещением пользователя об ошибке в переданном уровне лога.
        """
        return 'Некорректное значение уровня логгера: {}'.format(self.log_level)


class Logger:
    """
    Класс-логгер
    """
    def __init__(self, caller_module_name, log_file_path,
                 log_format='%(asctime)s - %(levelname)s - %(message)s',
                 time_rotation='d',
                 logger_level=logging.INFO,
                 handler_level=logging.INFO):
        """
        Конструктор. Создаёт сущность, которая, по сути, является обёрткой
        стандартного логгера, чтобы инкапсулировать весь нужный функционал.
        Потом можно будет создавать сущности логгера с настройками как для
        клиентской части, так и для серверной.
        @param caller_module_name: имя модуля из которого вызывается логгер.
        @param log_file_path: путь к лог-файлу.
        @param time_rotation: частота ротаций файла.
        @param log_format: формат вывода данных в файл.
        @param logger_level: уровень логгера.
        @param handler_level: уровень обработчика.
        """
        # Определяет правильный формат имени для логгера
        logger_name = 'SuperChat.' + caller_module_name
        # Создаёт объект-форматтер
        formatter = logging.Formatter(log_format)

        # Создаёт обработчик, который пишет в указанный файл с необходимыми
        # параметрами уровня и формата
        self._handler = logging.FileHandler(log_file_path,
                                            encoding='utf-8')
        self._handler.setLevel(handler_level)
        self._handler.setFormatter(formatter)

        # Опциональная ротация файлов по дням
        if time_rotation:
            logging.handlers.TimedRotatingFileHandler(log_file_path, when=time_rotation)

        # Создаёт экземпляр логгера с нужным именем, связанным обработчиком и уровнем
        self._logger = logging.getLogger(logger_name)
        self._logger.addHandler(self._handler)
        self._logger.setLevel(logger_level)

    def set_handler_level(self, level):
        """
        Устанавливает уровень обработчика.
        @param level: новое значение уровня обработчика.
        @return: -
        """
        self._handler.setLevel(level)

    def set_logger_level(self, level):
        """
        Устанавливает уровень логгера.
        @param level: новое значение уровня логгера.
        @return: -
        """
        self._logger.setLevel(level)

    def set_format(self, format_str):
        """
        Устанавливает новый формат вывода данных.
        @param format_str: строка с новым форматом.
        @return: -
        """
        formatter = logging.Formatter(format_str)
        self._handler.setFormatter(formatter)

    def log_msg(self, level, msg, *args, **kwargs):
        """
        Вызывает логирование с соответствующим уровнем.
        @param level: уровень сообщения.
        @param msg: текст сообщения.
        @param args: лист с дополнительными аргументами.
        @param kwargs: словарь с дополнительными аргкументами.
        @return:
        """
        if level == logging.DEBUG:
            self._logger.debug(msg, *args, **kwargs)
        elif level == logging.INFO:
            self._logger.info(msg, *args, **kwargs)
        elif level == logging.WARNING:
            self._logger.warning(msg, *args, **kwargs)
        elif level == logging.ERROR:
            self._logger.error(msg, *args, **kwargs)
        elif level == logging.CRITICAL:
            self._logger.critical(msg, *args, **kwargs)
        else:
            raise UnknownLogLevelError(level)
