# -*- coding: utf-8 -*-
"""
Модуль, который предназначается для реализации вспомогательного класса,
который бы удерживал ссылки на экземпляры различных классов и предоставлял
нужный экземпляр по требованию пользователя. Во многих случаях такой класс требуется,
чтобы избежать циклических зависимостей в коде, и когда речь заходит о том, что
необходимо работать только с одной сущностью данного класса, а не с её копией.
"""


class Holder:
    """
    Класс, который содержит ссылки на экземпляры классов
    """
    def __init__(self):
        self._instances = {}

    def get_instance(self, name):
        """
        Возвращает экземпляр конкретного класса по его идентификатору (имени).
        @param name: идентификатор класса (имя).
        @return: ссылка на экземпляр класса.
        """
        return self._instances[name]

    def update_instance(self, name, instance):
        """
        Обновляет значение для конкретного ключа в словаре.
        @param name: идентификатор класса (имя).
        @param instance: ссылка на экземпляр класса.
        @return: -
        """
        if name in self._instances.keys():
            self._instances[name] = instance
        else:
            raise LookupError('Ключ не найден!')

    def add_instance(self, name, instance):
        """
        Добавляет новую пару в словарь, если сущность такого типа
        ещё не находится в словаре.
        @param name: идентификатор класса (имя).
        @param instance: ссылка на экземпляр класса.
        @return: -
        """
        for key, val in self._instances.items():
            if type(instance) == type(val):
                raise TypeError('Сущность данного типа уже существует!')
        self._instances[name] = instance
