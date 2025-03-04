# В данный момент не требуется
# Для работы скрипта требуется ввод в консоль:
# pip install -r requirements.txt

from sql_query import SQLatm
from sql_query import check_digit_card


def atm_test_insert_users_test():
    '''Часть кода для создания базы, таблицы и наполнения юзерами'''
    SQLatm.create_table()
    print('Проверка добавления юзеров с корректными данными')
    SQLatm.insert_user(1111, 1111, 10000, None, None)
    SQLatm.insert_user(1112, 1111, 10000, None, 50)
    SQLatm.insert_user(1113, 1111, 10000, 50, None)
    SQLatm.insert_user(1114, 1111, 10000, 50, 50)
    SQLatm.insert_user(1119, 1111, None, None, None)
    # Значения должны округлиться при добавлении в базу
    SQLatm.insert_user(1115, 1111, 10000.929292929, 50.555555555, 50.6666666)

    print('\nПроверка на ошибку при добавлении')
    # Косячные типы
    SQLatm.insert_user(1116, 1111, 10000, 'g', None)
    SQLatm.insert_user(1117, 1111, 10000, None, 'g')
    SQLatm.insert_user(1118, 1111, 'g', None, None)
    SQLatm.insert_user(1120, 1111, 10000, 123, 'g')
    SQLatm.insert_user(1121, 1111, 10000, 'g', 1234)
    SQLatm.insert_user(1121, 1111, 'lol', 'g', 1234)

    # Косяки с пин-кодом
    SQLatm.insert_user(1122, 111, 10000, 10000, 1234)
    SQLatm.insert_user(1123, 11, 10000, 10000, 1234)
    SQLatm.insert_user(1124, 1, 10000, 10000, 1234)
    SQLatm.insert_user(1125, 11111, 10000, 10000, 1234)

    # Косячный номер карты
    SQLatm.insert_user(111, 1111, 10000, 10000, 1234)
    SQLatm.insert_user(11, 1111, 10000, 10000, 1234)
    SQLatm.insert_user(1, 1111, 10000, 10000, 1234)
    SQLatm.insert_user(11111, 1111, 10000, 10000, 1234)

    # Косячные значения
    SQLatm.insert_user(1990, 1111, 1000000000000000000000000, 10000000000000000000000000, 100000000000000000000000000)
    SQLatm.insert_user(1998, 1111, 10000000000000000000, 1000, 1000)
    SQLatm.insert_user(1997, 1111, 10000000000000000000000000, 100000000000000000000000000, 100000)
    SQLatm.insert_user(1996, 1111, 1000000000000000000000000, 1000000, 100000000000000000000000000)
    SQLatm.insert_user(1995, 1111, 1000000, 1000000000000000000000000000, 100000000000000000000000000)
    SQLatm.insert_user(1912, 1111, 12000, -2000000, -2000000)
    SQLatm.insert_user(1913, 1111, -2000, 22000000, -2000000)
    SQLatm.insert_user(1914, 1111, -2000, -2000000, 32000000)
    SQLatm.insert_user(1915, 1111, -2000, -2000000, -2000000)
    SQLatm.insert_user(1918, 1111, 2000, 2000000, -2000000)
    print()
    SQLatm.clear_table()
    print('Тестовые данные очищены')
    print('--------------------')


def atm_setup_db():
    '''Часть кода для создания базы, таблицы и наполнения юзерами'''
    print('---atm setup---')
    SQLatm.create_table()
    SQLatm.insert_user(1234, 1111, 10000, None, None)
    SQLatm.insert_user(2345, 2222, 10000, None, None)
    SQLatm.insert_user(3333, 3333, 10000, 1000, None)
    SQLatm.insert_user(4444, 4444, 10000, None, 1000)
    SQLatm.insert_user(5555, 5555, 10000, 1000, 1000)
    SQLatm.insert_user(6666, 6666, None, 1000, 1000)
    SQLatm.insert_user(7777, 7777, 100000, 10000, 10000)
    SQLatm.insert_user(8888, 8888, None, None, None)
    print('---setup OK!---')
    print('--------------------')


def atm_logic():
    print('ATM Script Login')
    while True:
        card_number = input('Введите номер карты: ')
        if check_digit_card(card_number):
            card_number = int(card_number)
            if SQLatm.input_card(card_number):  # Проверка существования карты с введенным значением

                while True:
                    start = SQLatm.input_code(card_number) # Проверка совпадения пин-кода к введенной карте

                    if start == True:  # Проверка совпадения пин-кода к введенной карте
                        SQLatm.input_operation(card_number)
                        return

                    elif start == False:  # Для того чтобы не уйти в бесконечность при блокировке карты
                        break

                    else:
                        continue
            else:
                continue
        else:
            print('ОШИБКА. Введен некорретный номер карты')
            print()



'''Сам скрипт'''
atm_test_insert_users_test()

atm_setup_db()
atm_logic()

# SQLatm.clear_table()