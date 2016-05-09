# coding: utf8

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

"""Irregular verbs training program backend
    1. Запрос - русский инфинитив, ответ - все формы
    2. Запрос - английский инфинитив, ответ - русский инфинитив
    3. Выбор промежутков слов из списка с помощью двух выпадашек RANDOM
    4. 10, 20, 50 случайных слов RANDOM
"""


class StartScreen(Screen):
    pass


class GameModeScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass

program = Builder.load_file("irregularverbs.kv")


class IrregularVerbsApp(App):
    def build(self):
        return program


if __name__ == '__main__':
    IrregularVerbsApp().run()
