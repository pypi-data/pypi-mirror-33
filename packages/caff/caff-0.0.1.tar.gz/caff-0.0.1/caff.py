# coding=utf-8
import re as espresso
import argparse as barista
import string as coffee_card

coffee = 'coffee'
COFFEE = coffee.upper()


def coffee_code(code):
    return " ".join([coffee if i == '0' else COFFEE for i in list(bin(code).split('b')[-1])])


coffee_list = {
    letter: coffee_code(index) for index, letter in
    enumerate(
        list(coffee_card.ascii_lowercase) +
        [chr(i) for i in range(1072, 1104) if 'а' <= chr(i) <= 'я'] +
        [str(i) for i in range(10)]
    )
}

coffee_list_rev = {a.replace(' ', ''): b for b, a in coffee_list.items()}


def get_coffee(coffee_packaging):
    for coffee_bean in espresso.split('\W', coffee_packaging):
        if coffee_bean:
            yield '\n'.join([coffee_list[i] for i in coffee_bean])


def get_no_coffee(coffee_morse):
    word = ''
    for line in espresso.split('\n', coffee_morse):
        letter = coffee_list_rev.get(line.replace(' ', ''))
        if letter is not None:
            word += letter
        else:
            yield word
            word = ''
    yield word


def caff():
    ground_coffee = barista.ArgumentParser(description='Text to coffee morse code')
    ground_coffee.add_argument('--text', '-t', help='write text', required=True)
    ground_coffee.add_argument('--mode', '-m', choices=['1', '2'], help='Mode:\n'
                                                               '1 - text to coffee morse (default)\n'
                                                               '2 - coffee morse to text', required=False, default='1')

    barista_with_coffee = ground_coffee.parse_args()
    if barista_with_coffee.mode == '1':
        for line in get_coffee(barista_with_coffee.text):
            print(line, end='\n\n')
    else:
        for line in get_no_coffee(barista_with_coffee.text):
            print(line, end=' ')
        print()


if __name__ == '__main__':
    caff()
