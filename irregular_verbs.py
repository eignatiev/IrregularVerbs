# coding=UTF-8

import csv
from kivy.app import App
from kivy.uix.label import Label
from random import randint


def main():

    """Irregular verbs training program backend
        1. Запрос - русский инфинитив, ответ - все формы
        2. Запрос - английский инфинитив, ответ - русский инфинитив
        3. Выбор промежутков слов из списка с помощью двух выпадашек RANDOM
        4. 10, 20, 50 случайных слов RANDOM
    """

    '''Preparing the tuple of lists with all the words'''
    global words
    words = tuple()
    with open('import.csv', 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words += (row,)
    print'\n'.join([word['Russian'] for word in words])

    '''Getting random words'''
    def random_word(_number_of_words=len(words) - 1):
        return words[randint(0, _number_of_words)]

    '''Asking to input the answer'''
    for test in range(3):
        current_word = random_word()
        answer = raw_input('Please enter the ' +
                           "{0} word forms\n".format(current_word['Simple'].upper()))

        if answer != current_word['PastSimple'] + ' ' + current_word['PastParticiple'] + '':
            raise Exception("Йобана")


if __name__ == '__main__':
    main()
