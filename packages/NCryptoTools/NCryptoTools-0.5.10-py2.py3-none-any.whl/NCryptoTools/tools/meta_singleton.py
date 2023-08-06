# -*- coding: utf-8 -*-
"""
Модуль определяет метакласс шаблона проектирования "Singleton".
"""


class Singleton(type):
    """
    Метакласс шаблона проектирования "Singleton"
    """
    def __init__(cls, *args, **kwargs):
        """
        Конструктор. У каждого подконтрольного класса будет атрибут __instance,
        который будет хранить ссылку на созданный экземпляр класса.
        @param args: дополнительные параметры в виде списка.
        @param kwargs: дополнительные параметры в виде словаря.
        """
        super().__init__(*args, **kwargs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        """
        Возвращает экземпляр класса. Наличие данной функции говорит о том,
        что класс является функтором (функциональным объектом).
        @param args: дополнительные параметры в виде списка.
        @param kwargs: дополнительные параметры в виде словаря.
        @return: экземпляр класса.
        """
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance

    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

