# -*- coding: utf-8 -*-
"""
Всё, что связано с непосредственной работой с самим файлом, описывается в данном модуле.
"""
import os
import re


class File:
    """
    Класс-обёртка для файла.
    """
    def __init__(self, file_path, open_mode, file_encoding):
        """
        Конструктор.
        @param file_path: путь к файлу (абсолютный)
        @param open_mode: режим открытия файла.
        @param file_encoding: кодировка файла.
        """
        self._file_path = file_path
        self._file_name = os.path.basename(file_path)
        self._file_folder = os.path.dirname(file_path)
        self._open_mode = open_mode
        self._file_encoding = file_encoding
        self._file_handle = None
        self._buffer = []

    def open(self, open_mode=None):
        """
        Открывает файл в нужном режиме.
        @param open_mode: режим открытия файла.
        @return: -
        """
        mode = self._open_mode if open_mode is None else open_mode
        try:
            self._file_handle = open(self._file_path, mode, encoding=self._file_encoding)
        except OSError as e:
            print(str(e))

    def delete(self):
        """
        Удаляет файл с физического носителя.
        @return: -
        """
        self.close()
        try:
            os.remove(self._file_path)
        except OSError as e:
            print(str(e))

    def close(self):
        """
        Иногда возникают ситуации, когда требуется вручную закрывать файл.
        Данный метод позволяет производить это действие.
        @return: -
        """
        self._file_handle.close()

    def write(self, data):
        """
        Осуществляет запись данных в файл. Данные должны быть представлены
        в виде списка. Файл должен иметь флаги, которые позволяют осуществлять
        в него запись, в ином случае будет выкинуто исключение.
        @param data: данные для записи в файл.
        @return: -
        """
        self._file_handle.writelines(data)

    def write_from_buffer(self):
        """
        Осуществляет запись данных в файл из буфера.
        @return: -
        """
        self._file_handle.writelines(self._buffer)

    def read_to_buffer(self):
        """
        Считывает данные из файла в буфер.
        @return: -
        """
        self._buffer = self._file_handle.readlines()


class IniFile(File):
    """
    Класс, который предназначается специально для работы с ini-файлами, так как
    там данные организованы определённым образом. В данном классе переопределены
    методы считывания и записывания данных файла. Данные в ini-файле представлены
    следующим образом:
    [Заголовок]
    элемент_1=1
    элемент_2=Андрей
    """
    def __init__(self, file_path, open_mode, file_encoding):
        super().__init__(file_path, open_mode, file_encoding)
        self._buffer = {}

    def get_buffer(self):
        """
        Геттер. Возвращает буфер с данными файла.
        @return: буфер с данными файла.
        """
        return self._buffer

    def set_buffer(self, new_buffer):
        """
        Сеттер. Обновляет данные буфера целиком. Предыдущие значения стераются.
        @param new_buffer: новый буфер.
        @return: -
        """
        self._buffer = new_buffer

    def get_item(self, title, element):
        """
        Возвращает необходимый элемент из заданного блока ini-файла.
        @param title: заголовок блока.
        @param element: название элемента.
        @return: значение необходимого элемента.
        """
        return self._buffer[title][element]

    def set_item(self, title, element, new_value):
        """
        Устанавливает новое значение необходимого элемента из заданного блока ini-файла.
        @param title: заголовок блока.
        @param element: название элемента.
        @param new_value: новое значение элемента.
        @return: -
        """
        self._buffer[title][element] = new_value

    def write_from_buffer(self):
        """
        Записывает данные в файл из буфера в формате, предназначенном для ini-файлов.
        @return: -
        """
        for title, elements_dict in self._buffer.items():
            self._file_handle.write(title + '\n')
            for element, value in elements_dict.items():
                self._file_handle.write('{}={}\n'.format(element, value))
        self._file_handle.write('\n[EOF]')
        self._file_handle.close()  # Подтверждает изменения

    def read_to_buffer(self):
        """
        Считывает данные из файла в буфер.
        @return: -
        """
        title_tmp = ''
        elements = {}
        for line in self._file_handle:
            if line.isspace() and len(title_tmp) != 0 and len(elements) != 0:
                self._buffer[title_tmp] = elements
                elements = {}
                continue

            if self.is_ini_title(line):
                title_tmp = line.strip()
                continue

            if self.is_ini_element(line):
                comment_block_pos = line.find(';')

                # Комментарии отсутствуют
                if comment_block_pos == -1:
                    key, val = line.strip().split('=')
                else:
                    key, val = line.strip().split(';')[0].split('=')

                elements[key] = val
                continue

    @staticmethod
    def is_ini_title(line):
        """
        Проверяет, является ли входящая строка заголовком в ini-файле.
        @param line: строка, которая нуждается в валидации.
        @return: логическое значение результата валидации строки.
        """
        return re.fullmatch('^(\[[\w\d]+\](;.*)*\n*)$', line) is not None

    @staticmethod
    def is_ini_element(line):
        """
        Проверяет, является ли входящая строка элементом в ini-файле.
        @param line: строка, которая нуждается в валидации.
        @return: логическое значение результата валидации строки.
        """
        return re.fullmatch('^([\w\d]+=[\w\d.]*(;.*)*\n*)$', line) is not None




