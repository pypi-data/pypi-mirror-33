# -*- coding: utf-8 -*-
"""
Серия функций-помошников, к которым часто приходится обращаться
"""
import re
import datetime


def is_correct_ipv4(ipv4_address):
    """
    Проверяет правильность Ip адреса.
    IPv4 адрес должен быть представлен в виде последовательности из 4 октетов,
    раздетённых точками; значение каждого октета должно быть от 0 до 255.
    @param ipv4_address: IPv4 адрес.
    @return: логическое значение проверки правильности IPv4.
    """
    re_ipv4 = re.compile('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' +
                         '([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    return re.fullmatch(re_ipv4, ipv4_address) is not None


def is_correct_port(port_number):
    """
    Проверяет правильность порта.
    Порт должен представлять из себя число в диапазоне от 1023 до 65535.
    Значения до 1023 являются зарезирвированными, поэтому не должны быть использованы.
    @param port_number: номер порта.
    @return: логическое значение проверки правильности порта.
    """
    re_port = re.compile('^(102[3-9]|1[3-9][0-9]{2}|[2-9][0-9]{3}|[1-5][0-9]{4}' +
                         '|6[0-4][0-9]{3}|655[0-2][0-9]|6553[0-5])$')
    return re.fullmatch(re_port, port_number) is not None


def is_correct_http_error_code(http_error_code):
    """
    Проверяет правильность кода ошибки HTTP.
    @param http_error_code: код ошибки HTTP.
    @return: логическое значение проверки правильности кода ошибки HTTP.
    """
    re_code = re.compile('^(10[01]|20[012]|40[0-9]|410|500)$')
    return re.fullmatch(re_code, http_error_code) is not None


def is_correct_chat_room_name(chat_room_name):
    """
    Проверяет правильность названия чат комнаты.
    Note: решение не окончательное, может быть изменено, пока
    ограничиваемся длинной названия (3 - 20 символов) и используемыми
    символами (латиница).
    @param chat_room_name: название чат-комнаты.
    @return: логическое значение проверки правильности названия
    чат-комнаты.
    """
    re_chat_room = re.compile('^(#[A-Za-z_\d]{3,31})$')
    return re.fullmatch(re_chat_room, chat_room_name) is not None


def get_current_time():
    """
    Возвращает текущее время.
    @return: отформатированная строка с текущим временем.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_formatted_date(unix_time_ms):
    """
    Форматирует UNIX-время, переводя его в читаемую форму.
    @param unix_time_ms: UNIX-время в миллисекундах.
    @return: строка с текущим временем и датой.
    """
    return datetime.datetime.fromtimestamp(unix_time_ms).strftime("%Y-%m-%d %H:%M:%S")
