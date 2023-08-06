# -*- coding: utf-8 -*-
"""
Тесты для функций-помошников.
"""
import pytest

from NCryptoTools.tools.utilities import *


@pytest.mark.parametrize('test_input, expected', [
    ('127.0.0.1', True),
    ('274.125.125.0', False),
    ('127.abc.0.0', False),
    ('192.128.0.999', False),
    ('a.128.0.0', False),
    ('-1,128.0.0', False),
    ('192. 128.0.1', False),
    ('255.255.255.255', True),
    ('1.1.1.a', False),
    ('', False),
    ('128.0.0', False)
])
def test_is_correct_ipv4(test_input, expected):
    """
    Тестирование функции is_correct_ipv4() из модуля utilities.py
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert is_correct_ipv4(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('1022', False),
    ('1023', True),
    ('10202', True),
    ('33662', True),
    ('56999', True),
    ('65535', True),
    ('abdc', False),
    ('65555', False),
    ('', False),
    ('1000a', False)
])
def test_is_correct_port(test_input, expected):
    """
    Тестирование функции is_correct_port() из модуля utilities.py
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert is_correct_port(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('99', False),
    ('100', True),
    ('101', True),
    ('176', False),
    ('199', False),
    ('1000', False),
    ('201', True),
    ('407', True),
    ('500', True),
    ('501', False),
    ('abcd', False)
])
def test_is_correct_http_error_code(test_input, expected):
    """
    Тестирование функции is_correct_http_error_code() из модуля utilities.py
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert is_correct_http_error_code(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('#ChatroomName', True),
    ('#VeryLogNameeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', False),
    ('ChatroomName', False),
    ('#CH', False),
    ('#1234567', True),
    ('#_Chatroom_name_', True),
    ('#_____________', True)
])
def test_is_correct_chat_room_name(test_input, expected):
    """
    Тестирование функции is_correct_chat_room_name() из модуля utilities.py
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert is_correct_chat_room_name(test_input) == expected

