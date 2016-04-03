# coding=UTF-8

import csv
from random import randint


def main():

    """Preparing tuple with dictionaries for every word"""
    global words
    words = tuple()
    with open('import.csv', 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words += (row,)

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
