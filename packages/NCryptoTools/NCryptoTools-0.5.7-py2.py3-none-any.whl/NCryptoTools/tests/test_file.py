# -*- coding: utf-8 -*-
"""
Тесты для модуля file.py.
"""

import pytest
from NCryptoTools.Tools.file import IniFile


@pytest.mark.parametrize('test_input, expected', [
    ('[Server_information]', True),
    ('[Server information]', False),
    ('[12th_Block]', True),
    ('[]', False),
    ('[1]', True),
    ('[;Server_information]', False),
    ('[Server_information];comment\n', True)
])
def test_is_ini_title(test_input, expected):
    """
    Тестирование функции is_ini_title() из модуля file.py
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert IniFile.is_ini_title(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('key=val', True),
    ('key = val', False),
    ('12=12', True),
    ('key=val;comment', True),
    ('keyval', False),
    ('key=', True),
    ('=val', False),
    ('key=val\n', True)
])
def test_is_ini_element(test_input, expected):
    """
    Тестирование функции is_ini_element() из модуля file.py.
    @param test_input: входные данные.
    @param expected: ожидаемый результат.
    @return: -
    """
    assert IniFile.is_ini_element(test_input) == expected
