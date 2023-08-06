# -*- coding: utf-8 -*-
"""
Тестирование наследования от метакласса "Singleton".
Проверяется, действует ли данный шаблон проектирования:
при создаваемые объекты должны быть одной и той же сущностью.
"""
import unittest
from NCryptoTools.Tools.meta_singleton import Singleton


class TestSingletonImpl(unittest.TestCase):
    def setUp(self):
        """
        Определяет класс Foo, как наследника от метакласса Singleton.
        @return: -
        """
        class Foo(metaclass=Singleton):
            def __init__(self, a):
                self.a = a

        # Для тестирования создаём поле-класс, чтобы поток можно было обращаться к данному
        # полю при создании объектов как self.Foo()
        self.Foo = Foo

    def testSingletonImpl(self):
        """
        Проверка, что оба объекта ссылаются на один и тот же участок памяти, то
        есть являются одним и тем же объектом.
        @return: -
        """
        foo1 = self.Foo(1)
        foo2 = self.Foo(2)
        print('foo1.a =', foo1.a)  # равно 1
        print('foo2.a =', foo2.a)  # равно 1!
        self.assertIs(foo1, foo2)
