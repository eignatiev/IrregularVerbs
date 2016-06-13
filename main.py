#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from random import randint

__version__ = "1.0"

""" Irregular verbs training program
    1. Запрос - русский инфинитив, ответ - все формы
    2. Запрос - английский инфинитив, ответ - русский инфинитив
    3. Выбор промежутков слов из списка с помощью двух выпадашек RANDOM
    4. 10, 20, 50 случайных слов RANDOM
"""


class StartScreen(Screen):
    @staticmethod
    def initial_preparation(mode):
        """Preparing the tuple of lists with all the words
        :param mode: toggles between English and Russian"""
        global WORDS, RUS_WORDS, ENG_WORDS
        WORDS = tuple()
        with open('import.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                WORDS += (row,)

        RUS_WORDS = []
        ENG_WORDS = []

        for i in range(len(WORDS)):
            rus_text = WORDS[i]['Russian']
            RUS_WORDS.append(rus_text)

            eng_text = WORDS[i]['Simple']
            ENG_WORDS.append(eng_text)

        RUS_WORDS = tuple(RUS_WORDS)
        ENG_WORDS = tuple(ENG_WORDS)

        global MODE
        MODE = mode

        global WORDS_LIST
        if MODE == 'rus_eng':
            WORDS_LIST = RUS_WORDS
        else:
            WORDS_LIST = ENG_WORDS


class GameModeScreen(Screen):
    in_game_words = ListProperty()

    def set_words_list(self, n, random=True):
        self.in_game_words = []
        if random:
            i = 0
            while i < n:
                random_word = WORDS[randint(0, len(WORDS) - 1)]
                if random_word in self.in_game_words:
                    continue
                else:
                    self.in_game_words.append(random_word)
                    i += 1
        elif not random:
            for i in xrange(min(n), max(n)):
                self.in_game_words.append(WORDS[i])
        return self.in_game_words


class MyButton(ToggleButton):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.CurrentScreen = WordsChoosingScreen


class WordsChoosingScreen(Screen):
    def __init__(self, **kw):
        super(WordsChoosingScreen, self).__init__(**kw)
        self.ListButton = MyButton

    def choose_words(self):

        x1, x2 = None, None
        for i in self.ids.from_word.children:
            if i.state == 'down':
                x1 = WORDS_LIST.index(i.text)
        for i in self.ids.to_word.children:
            if i.state == 'down':
                x2 = WORDS_LIST.index(i.text)

        if x1 is not None and x2 is not None:
            # Choosing the sub-list
            if x1 < x2:
                from_to = [x1, x2 + 1]
            else:
                from_to = [x2, x1 + 1]
            return from_to

    def set_words_list(self, lst):
        if self.choose_words():
            game_mode_sc_inst = GameModeScreen()
            return game_mode_sc_inst.set_words_list(lst, False)
        else:
            self.ids.start_button.text = '[b][i]Choose something![/i][/b]'
            self.ids.start_button.font_size = 20

    @mainthread
    def on_enter(self):

        if MODE == 'rus_eng':
            lang = 'Russian'
        else:
            lang = 'Simple'

        for i in xrange(len(WORDS)):
            text = WORDS[i][lang]

            from_group = "from_group"
            to_group = "to_group"

            from_button = MyButton(text=text,
                                   size_hint_y=None,
                                   font_size=10,
                                   height="29sp",
                                   background_color=(0, 1, 1, 1),
                                   group=from_group,
                                   id="from_button" + str(i))

            to_button = MyButton(text=text,
                                 size_hint_y=None,
                                 font_size=10,
                                 height="29sp",
                                 background_color=(0, 1, 1, 1),
                                 group=to_group,
                                 id="to_button" + str(i))

            self.ids.from_word.add_widget(from_button)
            self.ids.to_word.add_widget(to_button)

    def on_leave(self):
        self.ids.from_word.clear_widgets()
        self.ids.to_word.clear_widgets()


class GameFieldScreen(Screen):
    in_game_list = []
    current_word_number = 0
    current_word = {}
    # Text from text inputs
    inp_rus = None
    inp_eng = {}
    next_button = ObjectProperty()

    def add_widgets(self, names):
        button = Button(text='[b]next[/b]',
                        markup=True,
                        size_hint=(1, 0.1),
                        font_size=20,
                        background_color=(0, 1, 0, 1),
                        id="next_button",
                        on_release=self.next_word)
        for name in names:
            label = Label(id=name.lower() + '_label',
                          size_hint=(1, 0.1),
                          font_size=10,
                          text=name,
                          markup=True)
            text_inp = TextInput(size_hint=(1, 0.15),
                                 bold=True,
                                 font_size=16,
                                 markup=True,
                                 id=name.lower() + '_text_inp',
                                 on_touch_down=self.restore_but)
            self.ids.game_field_layout.add_widget(label)
            self.ids.game_field_layout.add_widget(text_inp)
        self.ids.game_field_layout.add_widget(button)
        self.next_button = self.ids.game_field_layout.children[0]

    def set_cur_word_text(self):
        self.current_word = self.in_game_list[self.current_word_number]
        if MODE == 'rus_eng':
            self.ids.cur_word.text = '[b][color=ff0000]' + \
                                     self.current_word['Russian'] + \
                                     '[/color][/b]'
        elif MODE == 'eng_rus':
            self.ids.cur_word.text = '[b][color=ff0000]' + \
                                     self.current_word['Simple'] + \
                                     '[/color][/b]'

    def restore_but(self, *a):
        self.next_button.text = '[b]next[/b]'
        self.next_button.background_color = (0, 1, 0, 1)

    def add_items(self):
        self.set_cur_word_text()
        eng_labels = ['Present Simple', 'Past Simple', 'Past Participle']
        rus_label = ['Russian']
        if MODE == 'rus_eng':
            self.add_widgets(eng_labels)
        elif MODE == 'eng_rus':
            self.add_widgets(rus_label)

    def check_cur_words(self, _inp_rus=None, _inp_eng=None):
        if _inp_rus:
            _inp_rus = unicode(_inp_rus).encode('utf8')
            if _inp_rus in self.current_word['Russian'].split('/'):
                self.next_button.text = 'True'
            else:
                self.next_button.text = 'False'
                self.next_button.background_color = (1, 0, 0, 1)
        elif _inp_eng:
            print(_inp_eng)
            if _inp_eng['Past Simple'] == self.current_word['PastSimple'] and \
               _inp_eng['Past Participle'] == self.current_word['PastParticiple'] and \
               _inp_eng['Present Simple'] == self.current_word['Simple']:
                self.next_button.text = 'True'
            else:
                self.next_button.text = 'False'
                self.next_button.background_color = (1, 0, 0, 1)

    def inputs_are_filled(self):
        for child in self.ids.game_field_layout.children:
            if child.id == 'russian_text_inp' and child.text:
                self.inp_rus = child.text.strip()
                self.check_cur_words(_inp_rus=self.inp_rus, _inp_eng=None)
                return True
            if child.id == 'past participle_text_inp':
                self.inp_eng['Past Participle'] = child.text.strip()
            elif child.id == 'past simple_text_inp':
                self.inp_eng['Past Simple'] = child.text.strip()
            elif child.id == 'present simple_text_inp':
                self.inp_eng['Present Simple'] = child.text.strip()
        if self.inp_eng and all([value for key, value in self.inp_eng.iteritems()]):
            self.check_cur_words(_inp_rus=None, _inp_eng=self.inp_eng)
            return True
        else:
            self.inp_eng = {}
            return False

    def alert(self):
        self.next_button.text = '[b]Fill all the fields![/b]'
        self.next_button.background_color = (0, 1, 0, 1)

    def save_data(self):
        pass

    def next_word(self, *a):
        if self.inputs_are_filled():
            self.save_data()

            self.current_word_number += 1
            if self.current_word_number < len(self.in_game_list):
                self.set_cur_word_text()
                for each in [child for child in self.ids.game_field_layout.children]:
                    if isinstance(each, TextInput):
                        each.text = ''
            else:
                self.current_word_number = 0

                self.ids.game_field_layout.clear_widgets()

                App.get_running_app().root.current = 'StartScreen'
        else:
            self.alert()


class FinalScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


program = Builder.load_file("irregularverbs.kv")


class IrregularVerbsApp(App):
    def build(self):
        return program


if __name__ == '__main__':
    IrregularVerbsApp().run()
