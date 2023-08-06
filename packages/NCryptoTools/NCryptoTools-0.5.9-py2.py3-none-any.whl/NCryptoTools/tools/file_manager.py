# -*- coding: utf-8 -*-
"""
Файловый менеджер. Позволяет работать файлами.
"""
import os
from shutil import copyfile
from NCryptoTools.tools.file import File, IniFile


class FileManager:
    """
    Основное назначение файлового менеджера - позволять работать с несколькими
    файлами (удалять, создавать, перемещать и т.д.). В контексте сетевого чата
    он предназначается для работы с файлом конфигурации приложения: autoexec.ini.
    """
    def __init__(self):
        """
        Конструктор. Изначально список файлов пустой. Пополнять его можно
        функцией add_file().
        """
        super().__init__()
        self._files = {}

    def open_file(self, file_path, open_mode=None):
        """
        Открывает дескриптор необходимого файла.
        @param file_path: путь к файлу.
        @param open_mode: режим открытия файла.
        @return: -
        """
        self._files[file_path].open(open_mode)

    def close_file(self, file_path):
        """
        Закрывает дескриптор необходимого файла.
        @param file_path: путь к файлу.
        @return: -
        """
        self._files[file_path].close()

    def add_file(self, file_path, open_mode, file_encoding):
        """
        Добавляет файл в список файлов класса.
        @param file_path: путь к файлу.
        @param open_mode: режим открытия файла.
        @param file_encoding: кодировка файла.
        @return: -
        """
        self._files[file_path] = File(file_path, open_mode, file_encoding)

    def remove_file(self, file_path):
        """
        Удаляет файл из списка файлов класса.
        @param file_path: путь к файлу (ключ для поиска в словаре).
        @return: -
        """
        del self._files[file_path]

    def delete_file(self, file_path):
        """
        Удаляет файл с физического носителя.
        @param file_path: путь к файлу (ключ для поиска в словаре).
        @return: -
        """
        # Удаляет файл c физического носителя
        self._files[file_path].delete()

        # Удаляет файл из списка зависимостей
        self.remove_file(file_path)

    def make_copy(self, src_file_path):
        """
        Делает дубликат файла.
        @param src_file_path: путь к файлу.
        @return: в случае успеха возвращает путь к копии файла, в ином случае
        возвращает None.
        """
        if src_file_path not in self._files.keys():
            raise IndexError('Ошибка: файл не найден!')
        dst_file_path = compose_file_copy_path(src_file_path,
                                               os.path.dirname(src_file_path))
        try:
            copyfile(src_file_path, dst_file_path)
        except IOError:
            return None
        return dst_file_path

    def read_to_buffer(self, file_path):
        """
        Зписывает данные из файла в буфер.
        @param file_path: путь к файлу.
        @return: -
        """
        self._files[file_path].read_to_buffer()

    def write_from_buffer(self, file_path):
        """
        Записывает данные из буфера в файл.
        @param file_path: путь к файлу.
        @return: -
        """
        self._files[file_path].write_from_buffer()

    def copy_buffer(self, src_file_path, dst_file_path):
        """
        Копирует данные из буфера одного файла в буфер другого файла.
        @param src_file_path: файл-источник.
        @param dst_file_path: файл-получатель.
        @return: -
        """
        buffer = self._files[src_file_path].get_buffer()
        self._files[dst_file_path].set_buffer(buffer)


class IniFileManager(FileManager):
    """
    Файловый менеджер с возможностями для работы с ini-файлами.
    """
    def add_file(self, file_path, open_mode, file_encoding):
        """
        Добавляет ini-файл в список файлов класса.
        @param file_path: путь к файлу.
        @param open_mode: режим открытия файла.
        @param file_encoding: кодировка файла.
        @return: -
        """
        self._files[file_path] = IniFile(file_path, open_mode, file_encoding)

    def get_item(self, file_path, title, element):
        """
        Возвращает необходимый элемент из заданного блока ini-файла.
        @param file_path: путь к ini-файлу.
        @param title: заголовок блока.
        @param element: название элемента.
        @return: значение необходимого элемента.
        """
        return self._files[file_path].get_item(title, element)

    def set_item(self, file_path, title, element, new_value):
        """
        Устанавливает новое значение необходимого элемента из заданного блока ini-файла.
        @param file_path: путь к ini-файлу.
        @param title: заголовок блока.
        @param element: название элемента.
        @param new_value: новое значение элемента.
        @return: -
        """
        self._files[file_path].set_item(title, element, new_value)


def compose_file_copy_path(stc_file_path, dst_folder_path):
    """
    При копировании файла нужно дать файлу новое имя. Задачей данной
    функции является составление нового имени для копии, учитывая со-
    держимое директории, в которую копируется файл.
    @param stc_file_path: путь к исходному файлу.
    @param dst_folder_path: путь к целевой папке.
    @return: путь к файлу-копии.
    """
    if not (os.path.exists(stc_file_path) and
            os.path.exists(dst_folder_path)):
        raise FileNotFoundError('Ошибка: файл не найден!')

    dir_path, file_full_name = os.path.split(stc_file_path)
    name, extension = os.path.splitext(file_full_name)

    suffix = 1
    multiplier = 1  # Количество повторений суффикса

    # Имя будет иметь вид: '...\...\~autoexec1.ini'
    # При обнаружении идентичного файла в папке, будут добавляться суффиксы, поэтому
    # название файла может принять следующий вид: '...\...\~autoexec355322323.ini'
    dst_file_name = '~' + name + str(suffix) * multiplier + extension

    # ВАЖНО: в конце пути dst_folder_path должен стоять '\'!
    dst_file_path = dst_folder_path + '\\' + dst_file_name

    while os.path.exists(dst_file_path):
        if suffix == 9:
            multiplier += 1
            suffix = 0
        else:
            suffix += 1
        dst_file_name = '~' + name + str(suffix) * multiplier + extension
        dst_file_path = dst_folder_path + '\\' + dst_file_name

    return dst_file_path
