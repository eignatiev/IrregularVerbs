#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from random import randint

__version__ = "1.0"


def main():

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
                    x1 = int(i.id.replace('from_button', ''))
            for i in self.ids.to_word.children:
                if i.state == 'down':
                    x2 = int(i.id.replace('to_button', ''))
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
                text = text.split('/')
                if len(text) > 2:
                    text = ', '.join(text[:2]) + ',\n{}'.format(text[2])
                else:
                    text = ', '.join(text)
                from_group = "from_group"
                to_group = "to_group"
                from_button = MyButton(text='[color=#a6a6a6]{}[/color]'.format(text),
                                       markup=True,
                                       size_hint_y=None,
                                       font_size='12px',
                                       font_name='Tahoma',
                                       halign='center',
                                       height='50px',
                                       background_down='',
                                       background_color=[212/255.0, 220/255.0, 217/255.0, 0.4],
                                       group=from_group,
                                       id="from_button" + str(i))
                to_button = MyButton(text='[color=#a6a6a6]{}[/color]'.format(text),
                                     markup=True,
                                     size_hint_y=None,
                                     font_size='12px',
                                     font_name='Tahoma',
                                     halign='center',
                                     height='50px',
                                     background_down='',
                                     background_color=[66/255.0, 80/255.0, 83/255.0, 0.8],
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
        saved_data = []
        true_counter = 0
        true_percent = 0

        def add_widgets(self, names):
            for name in [n.lower() for n in names]:
                label = Label(id=name + '_label',
                              size_hint=(1, 0.025),
                              font_size='14px',
                              color=(120, 102, 102, 1),
                              font_name='Tahoma-Regular',
                              text='[color=e4cfcf]{}:[/color].'.format(name),
                              markup=True,
                              align='bottom')
                text_inp = TextInput(size_hint=(1, 0.025),
                                     bold=True,
                                     markup=True,
                                     id=name + '_text_inp',
                                     on_touch_down=self.restore_but)
                self.ids.game_field_layout.add_widget(label)
                self.ids.game_field_layout.add_widget(text_inp)
            self.next_button = self.ids.next_button
            self.next_button.on_release = self.next_word

        def set_cur_word_text(self):
            self.current_word = self.in_game_list[self.current_word_number]
            if MODE == 'rus_eng':
                self.ids.cur_word.text = '[b][color=98e0ef]' + \
                                         self.current_word['Russian'] + \
                                         '[/color][/b]'
            elif MODE == 'eng_rus':
                self.ids.cur_word.text = '[b][color=98e0ef]' + \
                                         self.current_word['Simple'] + \
                                         '[/color][/b]'

        def restore_but(self, *a):
            self.next_button.text = '[color=#d4dcd9][b]Next[/b][/color]'
            self.next_button.font_size = '20px'
            self.next_button.background_normal = ''
            self.next_button.background_color = [34/255.0, 82/255.0, 102/255.0, 1]

        def add_items(self):
            self.set_cur_word_text()
            eng_labels = ['Present Simple', 'Past Simple', 'Past Participle']
            rus_label = ['Russian']
            if MODE == 'rus_eng':
                self.add_widgets(eng_labels)
            elif MODE == 'eng_rus':
                self.add_widgets(rus_label)

        def save_data(self, inp):
            self.saved_data.append(inp)

        def check_cur_words(self, _inp_rus=None, _inp_eng=None):
            data_to_be_saved = {}
            if _inp_rus:
                _inp_rus = (unicode(_inp_rus).encode('utf8'))
                data_to_be_saved['should_be'] = self.current_word['Russian']
                data_to_be_saved['inputted'] = _inp_rus
                data_to_be_saved['initial'] = self.current_word['Simple']
                if _inp_rus in self.current_word['Russian'].split('/'):
                    self.next_button.markup = True
                    self.next_button.text = '[color=#419f6d]Correct[/color]'
                    data_to_be_saved['is_correct'] = True
                    self.true_counter += 1
                else:
                    self.next_button.markup = True
                    self.next_button.text = '[color=#da7878]Wrong[/color]'
                    data_to_be_saved['is_correct'] = False
                self.save_data(data_to_be_saved)
            elif _inp_eng:
                data_to_be_saved['should_be1'] = self.current_word['Simple']
                data_to_be_saved['should_be2'] = self.current_word['PastSimple']
                data_to_be_saved['should_be3'] = self.current_word['PastParticiple']
                data_to_be_saved['inputted1'] = _inp_eng['Present Simple']
                data_to_be_saved['inputted2'] = _inp_eng['Past Simple']
                data_to_be_saved['inputted3'] = _inp_eng['Past Participle']
                data_to_be_saved['initial'] = self.current_word['Russian']
                if _inp_eng['Present Simple'] == self.current_word['Simple']:
                    data_to_be_saved['is_correct1'] = True
                else:
                    data_to_be_saved['is_correct1'] = False
                if _inp_eng['Past Simple'] in self.current_word['PastSimple'].split('/'):
                    data_to_be_saved['is_correct2'] = True
                else:
                    data_to_be_saved['is_correct2'] = False
                if _inp_eng['Past Participle'] == self.current_word['PastParticiple']:
                    data_to_be_saved['is_correct3'] = True
                else:
                    data_to_be_saved['is_correct3'] = False
                if data_to_be_saved['is_correct1'] and \
                        data_to_be_saved['is_correct2'] and \
                        data_to_be_saved['is_correct3']:
                    self.next_button.markup = True
                    self.next_button.text = '[color=#419f6d]Correct[/color]'
                    self.true_counter += 1
                else:
                    self.next_button.markup = True
                    self.next_button.text = '[color=#da7878]Wrong[/color]'
                self.save_data(data_to_be_saved)

        def inputs_are_filled(self):
            for child in self.ids.game_field_layout.children:
                if child.id == 'russian_text_inp' and child.text:
                    self.inp_rus = child.text.strip().lower()
                    self.check_cur_words(_inp_rus=self.inp_rus, _inp_eng=None)
                    return True
                if child.id == 'past participle_text_inp':
                    self.inp_eng['Past Participle'] = child.text.strip().lower()
                elif child.id == 'past simple_text_inp':
                    self.inp_eng['Past Simple'] = child.text.strip().lower()
                elif child.id == 'present simple_text_inp':
                    self.inp_eng['Present Simple'] = child.text.strip().lower()
            if self.inp_eng and all([value for key, value in self.inp_eng.iteritems()]):
                self.check_cur_words(_inp_rus=None, _inp_eng=self.inp_eng)
                return True
            else:
                self.inp_eng = {}
                return False

        def alert(self):
            self.next_button.text = '[b]Fill all the blank fields![/b]'
            self.next_button.font_size = '16px'

        def next_word(self, *a):
            if self.inputs_are_filled():
                self.current_word_number += 1
                if self.current_word_number < len(self.in_game_list):
                    self.set_cur_word_text()
                    for each in [child for child in self.ids.game_field_layout.children]:
                        if isinstance(each, TextInput):
                            each.text = ''
                else:
                    self.current_word_number = 0
                    self.true_percent = int(self.true_counter / (len(self.in_game_list) / 100.0))
                    self.true_counter = 0
                    FinalScreen.percent = self.true_percent
                    self.ids.game_field_layout.clear_widgets()
                    App.get_running_app().root.current = 'FinalScreen'
            else:
                self.alert()
        pass

    class FinalScreenLabel(Label):
        pass

    class LighterLabel(FinalScreenLabel):
        pass

    class DarkerLabel(FinalScreenLabel):
        pass

    class FinalScreen(Screen):
        saved_data = []
        percent = 0

        def set_resolution(self, percent, common_noun):
            resolution_text = '[color=98e0ef]You\'ve passed [b]{}%[/b] of words.\nYou are [b]{}[/b].[/color]'\
                .format(str(percent), common_noun)
            self.ids.resolution.text = resolution_text

        def add_result(self, percent):
            if percent >= 85:
                self.set_resolution(percent, 'brain')
            elif 60 < percent < 85:
                self.set_resolution(percent, 'middling')
            else:
                self.set_resolution(percent, 'moron')

        def output_data(self):
            self.saved_data = GameFieldScreen.saved_data
            self.add_result(self.percent)
            white_color = True

            def to_green(text):
                return '[color=87E987]{}'.format(text)

            def to_red(text):
                return '[color=DFB1B1]{}'.format(text)

            def is_wrong_answer(answer):
                keys = ['is_correct1', 'is_correct2', 'is_correct3']
                values = [answer[key] for key in keys]
                return not all(values)

            if MODE == 'rus_eng':
                for item in self.saved_data:
                    if is_wrong_answer(item):
                        for i in ['1', '2', '3']:
                            if item['is_correct' + i]:
                                item['inputted' + i] = to_green(item['inputted' + i])
                            else:
                                item['inputted' + i] = to_red(item['inputted' + i])
                        if white_color:
                            label_1 = LighterLabel(text='[color=#a6a6a6]{}'.format(item['initial'].replace('/', ',\n')))
                            self.ids.final_table.add_widget(label_1)
                            label_2 = LighterLabel(text='\n'.join(map('[color=#a6a6a6]{}'
                                                                      .format, [item['should_be1'],
                                                                                item['should_be2'],
                                                                                item['should_be3']])))
                            self.ids.final_table.add_widget(label_2)
                            label_3 = LighterLabel(text='\n'.join([item['inputted1'],
                                                                   item['inputted2'],
                                                                   item['inputted3']]))
                            self.ids.final_table.add_widget(label_3)
                            white_color = False
                        elif not white_color:
                            label_1 = DarkerLabel(text='[color=#a6a6a6]{}'.format(item['initial'].replace('/', ',\n')))
                            self.ids.final_table.add_widget(label_1)
                            label_2 = DarkerLabel(text='\n'.join(map('[color=#a6a6a6]{}'.format, [item['should_be1'],
                                                                                                  item['should_be2'],
                                                                                                  item['should_be3']])))
                            self.ids.final_table.add_widget(label_2)
                            label_3 = DarkerLabel(text='\n'.join([item['inputted1'],
                                                                  item['inputted2'],
                                                                  item['inputted3']]))
                            self.ids.final_table.add_widget(label_3)
                            white_color = True
            elif MODE == 'eng_rus':
                for item in self.saved_data:
                    if not item['is_correct']:
                        item['inputted'] = to_red(item['inputted'])
                        if white_color:
                            label_1 = LighterLabel(text=item['initial'])
                            self.ids.final_table.add_widget(label_1)
                            label_2 = LighterLabel(text=item['should_be'])
                            self.ids.final_table.add_widget(label_2)
                            label_3 = LighterLabel(text=item['inputted'])
                            self.ids.final_table.add_widget(label_3)
                            white_color = False
                        elif not white_color:
                            label_1 = DarkerLabel(text=item['initial'])
                            self.ids.final_table.add_widget(label_1)
                            label_2 = DarkerLabel(text=item['should_be'])
                            self.ids.final_table.add_widget(label_2)
                            label_3 = DarkerLabel(text=item['inputted'])
                            self.ids.final_table.add_widget(label_3)
                            white_color = True
            GameFieldScreen.saved_data = []

    class ScreenManagement(ScreenManager):
        pass

    program = Builder.load_file("irregularverbs.kv")

    class IrregularVerbsApp(App):
        def build(self):
            return program

    IrregularVerbsApp().run()

if __name__ == '__main__':
    main()
