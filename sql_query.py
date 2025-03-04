import sqlite3
from types import NoneType


def check_correct_int(digit: str) -> bool:
    '''Маленькая проверка на корректность введенного числа'''
    # Проверяет, что каждый элемент является цифрой и не начинается с нуля, без нее возможен ввод чисел, что начинаются
    # с нуля и плюса, т.к. int преобразует корректно, но, думаю, ввод +04749 нельзя считать корректным со стороны юзера
    if digit != '' and digit[0].isdigit() and digit[0] != '0':
        for el in digit:
            if el.isdigit() == False:
                return False
        return True
    return False


def check_digit_card(digit_card: str) -> bool:
    '''Проверка на корректный номер карты. Может начинаться с нуля, все элменты должны быть цифрами, равно 4 элементам'''
    if len(digit_card) == 4:
        for el in digit_card:
            if el.isdigit() == False:
                return False
        return True
    return False


class SQLatm:

    @staticmethod
    def create_table():
        '''Создание таблицы Users_data'''
        with sqlite3.connect('atm.db') as db:  # Данный способ позволяет не использовать commit
            cur = db.cursor()
            # Наличие счета необязательно
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Users_data
            (
                UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                Card_number INTEGER NOT NULL,
                Pin_code INTEGER NOT NULL,
                Pin_remaining_tries INTEGER NOT NULL DEFAULT 3,
                Status VARCHAR(255) NOT NULL DEFAULT 'open',
                Balance_RUB FLOAT,
                Balance_USD FLOAT,
                Balance_EUR FLOAT
            );
            ''')
            # Status = open, blocked


    @staticmethod
    def clear_table():
        '''Очистка таблицы Users_data'''
        with sqlite3.connect('atm.db') as db:  # Данный способ позволяет не использовать commit
            cur = db.cursor()
            cur.execute('''DELETE FROM Users_data''')


    @staticmethod
    def insert_user(
        card_number: int,
        pin_code: int,
        balance_RUB: int | float | None = None,
        balance_USD: int | float | None = None,
        balance_EUR: int | float | None = None,
        ) -> None:
        '''Создание нового пользователя'''

        # Проверка на типы данных
        if all((
            isinstance(card_number, (int)),
            isinstance(pin_code, (int)),
            isinstance(balance_RUB, (int, float, NoneType)),
            isinstance(balance_USD, (int, float, NoneType)),
            isinstance(balance_EUR, (int, float, NoneType)),
        )):
            pass
        else:
            print(f'ОШИБКА ДАННЫХ пользователя с номером карты {card_number} на этапе проверки типов данных.')
            return

        # Проверка на корректный размер значений
        if all((
            1000 <= card_number <= 9999,
            1000 <= pin_code <= 9999,
            balance_RUB == None or 0 <= balance_RUB <= 1e12,  # Важно, что сначала проверка на None, иначе ошибка при условии
            balance_USD == None or 0 <= balance_USD <= 1e12,
            balance_EUR == None or 0 <= balance_EUR <= 1e12,
        )):
            pass
        else:
            print(f'ОШИБКА ДАННЫХ пользователя с номером карты {card_number} на этапе проверки значений.')
            return

        user_data = (card_number, pin_code, balance_RUB, balance_USD, balance_EUR,)  # Пакуем в кортеж
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            # Проверка на наличие пользователя с таким номером карты в базе данных
            cur.execute('''
                SELECT Card_number
                FROM Users_data
                WHERE Card_number = ?;
            ''', (card_number,))  # Запятая в конце, этож кортежем быть должно!
            result_select = cur.fetchone()

            # Если пользователя нет и возвращается None - тогда создается в базе новый
            if result_select == None:
                user_data = (card_number, pin_code, balance_RUB, balance_USD, balance_EUR,)  # Пакуем данные в кортеж

                # Числа округляются при вставке до .4 для дальнейшего удобства в работе с ними при обмене
                cur.execute('''
                    INSERT INTO Users_data (Card_number, Pin_code, Balance_RUB, Balance_USD, Balance_EUR)
                    VALUES (?, ?, ROUND(?, 4), ROUND(?, 4), ROUND(?, 4));
                ''', user_data)
                print(f'Новый пользователь с номером карты {card_number} добавлен в базу данных.')
            else:
                print(f'Пользователь с номером карты {card_number} уже существует.')


    @staticmethod
    def input_card(card_number):
        '''Проверка наличия карты в БД'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            cur.execute('''
                SELECT Card_number
                FROM Users_data
                WHERE Card_number = ?;
            ''', (card_number,))
            result_card = cur.fetchone()
            if result_card == None:
                print('ОШИБКА. Введен неизвестный номер карты.')
                print()
                return False
            else:
                return True


    @staticmethod
    def input_code(card_number):
        '''Ввод и проверка пин-кода c 3 попытками'''

        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            cur.execute('''
                SELECT Status
                FROM Users_data
                WHERE Card_number = ?;
            ''', (card_number,))
            result_status = cur.fetchone()
            status = result_status[0]
            if status == 'blocked':
                print('КАРТА ЗАБЛОКИРОВАНА. Пожалуйста, обратитесь в отделение банка для разблокировки.')
                return False
            else:
                cur.execute('''
                    SELECT Pin_code, Pin_remaining_tries
                    FROM Users_data
                    WHERE Card_number = ?;
                ''', (card_number,))
                result_pin_and_tries = cur.fetchone()
                pin = result_pin_and_tries[0]
                tries = result_pin_and_tries[1]

                input_pin = input(f'Введите пин-код: ')

                if input_pin == str(pin):
                    # При правильном вводе пин-кода попытки обновляются
                    refresh_tries = 3
                    cur.execute('''
                        UPDATE Users_data
                        SET Pin_remaining_tries = ?
                        WHERE Card_number = ?;
                    ''', (refresh_tries, card_number))
                    return True
                else:
                    tries -= 1
                    if tries > 1:
                        cur.execute('''
                            UPDATE Users_data
                            SET Pin_remaining_tries = ?
                            WHERE Card_number = ?;
                        ''', (tries, card_number))
                        print('ОШИБКА. Введен некорректный пин-код.')
                        print(f'Осталось {tries} попытки, после чего карта заблокируется.')
                        return
                    elif tries == 1:
                        cur.execute('''
                            UPDATE Users_data
                            SET Pin_remaining_tries = ?
                            WHERE Card_number = ?;
                        ''', (tries, card_number))
                        print('ОШИБКА. Введен некорректный пин-код.')
                        print(f'Осталась {tries} попытка, после чего карта заблокируется.')
                        return
                    elif tries == 0:
                        cur.execute('''
                            UPDATE Users_data
                            SET Pin_remaining_tries = ?, Status = 'blocked'
                            WHERE Card_number = ?;
                        ''', (tries, card_number))
                        print('ОШИБКА. Введен некорректный пин-код.')
                        print(f'Осталось {tries} попыток, карта была автоматически заблокирована.')
                        print('Пожалуйста, обратитесь в отделение банка для разблокировки.')
                        return False


    @staticmethod
    def info_balance(card_number):
        '''Вывод на экран баланса карты'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            cur.execute('''
                SELECT Balance_RUB, Balance_USD, Balance_EUR
                FROM Users_data
                WHERE Card_number = ?;
            ''', (card_number,))
            result_info_balance = cur.fetchone()
            balance_rub = result_info_balance[0]
            balance_usd = result_info_balance[1]
            balance_eur = result_info_balance[2]
            res = ''  # Формируем результрующую строку для вывода баланса
            if balance_rub != None:
                res += f'{balance_rub} RUB'
            if balance_usd != None:
                res += f' | {balance_usd} USD'
            if balance_eur != None:
                res += f' | {balance_eur} EUR'
            print(f'Баланс Вашей карты: {res}')
            print('--------------------')


    @staticmethod
    def get_user_balance(card_number):
        '''Получение значения баланса карты'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            cur.execute('''
                SELECT Balance_RUB, Balance_USD, Balance_EUR
                FROM Users_data
                WHERE Card_number = ?;
            ''', (card_number,))
            result_info_balance = cur.fetchone()
            return result_info_balance


    @staticmethod
    def withdraw_money(card_number):
        '''Снятие денежных средств с баланса карты'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            balance = SQLatm.get_user_balance(card_number)
            balance_rub = balance[0]
            balance_usd = balance[1]
            balance_eur = balance[2]
            rub_yes = False  # Переменные для проверки доступности данной валюты для пользователя
            usd_yes = False
            eur_yes = False

            if ((balance_rub == None or balance_rub < 50)
                and (balance_usd == None or balance_usd < 5)
                and (balance_eur == None or balance_eur < 5)):
                print('Функционал снятия недоступен по причине отсутствия достаточных средств на карте.')
                print()
                return False

            while True:
                print('Вам доступны для снятия следующие валюты: ')
                if balance_rub != None and balance_rub >= 50:
                    print(f'1. RUB в размере не менее 50 RUB и не более {int(balance_rub // 50 * 50)} RUB')  # Нет для выдачи меньше 50 купюры
                    rub_yes = True  # Чтобы без отображения нельзя было выбрать данную валюту
                if balance_usd != None and balance_usd >= 5:
                    print(f'2. USD в размере не менее 5 USD и не более {int(balance_usd // 5 * 5)} USD')  # Нет для выдачи меньше 5 купюры
                    usd_yes = True  # Чтобы без отображения нельзя было выбрать данную валюту
                if balance_eur != None and balance_eur >= 5:
                    print(f'3. EUR в размере не менее 5 EUR и не более {int(balance_eur // 5 * 5)} EUR')  # Нет для выдачи меньше 5 купюры
                    eur_yes = True  # Чтобы без отображения нельзя было выбрать данную валюту
                # Нумерация пусть будет уникальной в списке, не стал привязывать к выводу. Может 1 и 3 быть

                choice_currency = input('\nКакую валюту желаете снять? Введите номер или название валюты: ')
                if choice_currency == '00':
                    print('--> возвращение в главное меню')
                    print()
                    return

                if rub_yes and (choice_currency in ['1', 'RUB', 'rub']):  # Снятие для рубля
                    print('\nВы выбрали RUB')
                    print('(!) Допускается снятие не менее 50 RUB и не более 1000000 RUB за операцию.')
                    while True:
                        desired_withdraw = input('Введите сумму (целое число), которую желаете снять: ')
                        if desired_withdraw == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(desired_withdraw):
                            desired_withdraw = int(desired_withdraw)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        rounded_withdraw = (desired_withdraw // 50 * 50)  # Округленное число с учетом выдачи

                        if desired_withdraw < 50 or desired_withdraw > 1000000:
                            print('ОШИБКА. Некорректная сумма снятия.')
                            print('(!) Допускается снятие не менее 50 RUB и не более 1000000 RUB за операцию.')
                            print()

                        elif desired_withdraw > (balance_rub // 50 * 50):
                            print('На балансе недостаточно средств для снятия данной суммы.')
                            print(f'Ваша максимальная сумма для снятия: {int(balance_rub // 50 * 50)} RUB')
                            print()

                        elif desired_withdraw != rounded_withdraw:  # Если требует округления - спрашиваем, согласен ли пользователь
                            print(f'Желаемая сумма для снятия {desired_withdraw} RUB была округлена до {rounded_withdraw} RUB')
                            print('в связи с отсутствием купюр номиналом менее 50 RUB для выдачи.')
                            print(f'Желаете снять {rounded_withdraw} RUB?')
                            choice = input('Введите 1 или YES для согласия. Или любую цифру, сообщение для отмены операции: ')
                            if choice in ['1', 'YES', 'yes']:
                                new_balance_rub = balance_rub - rounded_withdraw
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_RUB = ?
                                    WHERE Card_number = ?;
                                ''', (new_balance_rub, card_number))
                                db.commit()
                                print(f'Снятие {rounded_withdraw} RUB успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            else:
                                print('Операция отменена.')
                                return

                        elif desired_withdraw == rounded_withdraw:
                            new_balance_rub = balance_rub - rounded_withdraw
                            cur.execute('''
                                UPDATE Users_data
                                SET Balance_RUB = ?
                                WHERE Card_number = ?;
                            ''', (new_balance_rub, card_number))
                            db.commit()
                            print(f'Снятие {rounded_withdraw} RUB успешно!')
                            SQLatm.info_balance(card_number)
                            return


                if usd_yes and (choice_currency in ['2', 'USD', 'usd']):  # Снятие для доллара
                    print('\nВы выбрали USD')
                    print('(!) Допускается снятие не менее 5 USD и не более 100000 USD за операцию.')
                    while True:
                        desired_withdraw = input('Введите сумму (целое число), которую желаете снять: ')
                        if desired_withdraw == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(desired_withdraw):
                            desired_withdraw = int(desired_withdraw)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        rounded_withdraw = (desired_withdraw // 5 * 5)  # Округленное число с учетом выдачи

                        if desired_withdraw < 5 or desired_withdraw > 100000:
                            print('ОШИБКА. Некорректная сумма снятия.')
                            print('(!) Допускается снятие не менее 5 USD и не более 100000 USD за операцию.')
                            print()

                        elif desired_withdraw > (balance_usd // 5 * 5):
                            print('На балансе недостаточно средств для снятия данной суммы.')
                            print(f'Ваша максимальная сумма для снятия: {int(balance_usd // 5 * 5)} USD')
                            print()

                        elif desired_withdraw != rounded_withdraw:  # Если требует округления - спрашиваем, согласен ли пользователь
                            print(f'Желаемая сумма для снятия {desired_withdraw} USD была округлена до {rounded_withdraw} USD')
                            print('в связи с отсутствием купюр номиналом менее 5 USD для выдачи.')
                            print(f'Желаете снять {rounded_withdraw} USD?')
                            choice = input('Введите 1 или YES для согласия. Или любую цифру, сообщение для отмены операции: ')
                            if choice in ['1', 'YES', 'yes']:
                                new_balance_usd = balance_usd - rounded_withdraw
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_USD = ?
                                    WHERE Card_number = ?;
                                ''', (new_balance_usd, card_number))
                                db.commit()
                                print(f'Снятие {rounded_withdraw} USD успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            else:
                                print('Операция отменена.')
                                return

                        elif desired_withdraw == rounded_withdraw:
                            new_balance_usd = balance_usd - rounded_withdraw
                            cur.execute('''
                                UPDATE Users_data
                                SET Balance_USD = ?
                                WHERE Card_number = ?;
                            ''', (new_balance_usd, card_number))
                            db.commit()
                            print(f'Снятие {rounded_withdraw} USD успешно!')
                            SQLatm.info_balance(card_number)
                            return


                if eur_yes and (choice_currency in ['3', 'EUR', 'eur']):  # Снятие для евро
                    print('\nВы выбрали EUR')
                    print('(!) Допускается снятие не менее 5 EUR и не более 100000 EUR за операцию.')
                    while True:
                        desired_withdraw = input('Введите сумму (целое число), которую желаете снять: ')
                        if desired_withdraw == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(desired_withdraw):
                            desired_withdraw = int(desired_withdraw)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        rounded_withdraw = (desired_withdraw // 5 * 5)  # Округленное число с учетом выдачи

                        if desired_withdraw < 5 or desired_withdraw > 100000:
                            print('ОШИБКА. Некорректная сумма снятия.')
                            print('(!) Допускается снятие не менее 5 EUR и не более 100000 EUR за операцию.')
                            print()

                        elif desired_withdraw > (balance_eur // 5 * 5):
                            print('На балансе недостаточно средств для снятия данной суммы.')
                            print(f'Ваша максимальная сумма для снятия: {int(balance_eur // 5 * 5)} EUR')
                            print()

                        elif desired_withdraw != rounded_withdraw:  # Если требует округления - спрашиваем, согласен ли пользователь
                            print(f'Желаемая сумма для снятия {desired_withdraw} EUR была округлена до {rounded_withdraw} EUR')
                            print('В связи с отсутствием купюр номиналом менее 5 EUR для выдачи.')
                            print(f'Желаете снять {rounded_withdraw} EUR?')
                            choice = input('Введите 1 или YES для согласия. Или любую цифру, сообщение для отмены операции: ')
                            if choice in ['1', 'YES', 'yes']:
                                new_balance_eur = balance_eur - rounded_withdraw
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_EUR = ?
                                    WHERE Card_number = ?;
                                ''', (new_balance_eur, card_number))
                                db.commit()
                                print(f'Снятие {rounded_withdraw} EUR успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            else:
                                print('Операция отменена.')
                                return

                        elif desired_withdraw == rounded_withdraw:
                            new_balance_eur = balance_eur - rounded_withdraw
                            cur.execute('''
                                UPDATE Users_data
                                SET Balance_EUR = ?
                                WHERE Card_number = ?;
                            ''', (new_balance_eur, card_number))
                            db.commit()
                            print(f'Снятие {rounded_withdraw} EUR успешно!')
                            SQLatm.info_balance(card_number)
                            return

                else:
                    print('ОШИБКА. Недоступная валюта.')
                    print()
                    continue


    @staticmethod
    def deposit_money(card_number):
        '''Внесение денежных средств на баланс карты'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            balance = SQLatm.get_user_balance(card_number)
            balance_rub = balance[0]
            balance_usd = balance[1]
            balance_eur = balance[2]
            rub_yes = False  # Переменные для проверки доступности данной валюты для пользователя
            usd_yes = False
            eur_yes = False

            if (balance_rub == None and balance_usd == None and balance_eur == None):
                print('Функционал внесения средств недоступен по причине отсутствия счета на карте. Обратитесь в банк.')
                print()
                return

            while True:
                print('Для внесения Вам доступны следующие валюты:')
                if balance_rub != None:
                    print('1. RUB')
                    rub_yes = True
                if balance_usd != None:
                    print('2. USD')
                    usd_yes = True
                if balance_eur != None:
                    print('3. EUR')
                    eur_yes = True
                print('\nКакую валюту Вы желаете внести? Введите цифру или название валюты')

                choice_deposit = input(': ')
                if choice_deposit == '00':
                    print('--> возвращение в главное меню')
                    print()
                    return

                if rub_yes and (choice_deposit in ['1', 'RUB', 'rub']):
                    print('\nВНЕСЕНИЕ RUB')
                    print('(!) Сумма вносимых средств не может быть менее 10 RUB и более 1000000 RUB')
                    print('(!) Банкомат принимает только купюры номиналом от 10 RUB')
                    while True:
                        rub_deposit = input('Введите сумму внесения средств (целое число): ')
                        if rub_deposit == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(rub_deposit):
                            rub_deposit = int(rub_deposit)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        if 10 <= rub_deposit <= 1000000:
                            if rub_deposit == (rub_deposit // 10 * 10):  # Корректные купюры
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_RUB = Balance_RUB + ?
                                    WHERE Card_number = ?;
                                ''', (rub_deposit, card_number))
                                db.commit()
                                print(f'Внесение {rub_deposit} RUB успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            elif rub_deposit != (rub_deposit // 10 * 10):
                                print('ОШИБКА внесения средств. Банкомат не принимают купюры номиналом менее 10 RUB.')
                                print(f'*Попробуйте внести {rub_deposit // 10 * 10}')
                                print()
                                continue
                        else:
                            print('ОШИБКА. Недопустимая сумма.')
                            print()


                if usd_yes and (choice_deposit in ['2', 'USD', 'usd']):
                    print('\nВНЕСЕНИЕ USD')
                    print('(!) Сумма вносимых средств не может быть менее 5 USD и более 100000 USD')
                    print('(!) Банкомат принимает только купюры номиналом от 5 USD')
                    while True:
                        usd_deposit = input('Введите сумму внесения средств (целое число): ')
                        if usd_deposit == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(usd_deposit):
                            usd_deposit = int(usd_deposit)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        if 5 <= usd_deposit <= 100000:
                            if usd_deposit == (usd_deposit // 5 * 5):  # Корректные купюры
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_USD = Balance_USD + ?
                                    WHERE Card_number = ?;
                                ''', (usd_deposit, card_number))
                                db.commit()
                                print(f'Внесение {usd_deposit} USD успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            elif usd_deposit != (usd_deposit // 5 * 5):
                                print('ОШИБКА внесения средств. Банкомат не принимают купюры номиналом менее 5 USD')
                                print(f'*Попробуйте внести {usd_deposit // 5 * 5}')
                                print()
                                continue
                        else:
                            print('ОШИБКА. Недопустимая сумма.')
                            print()


                if eur_yes and (choice_deposit in ['3', 'EUR', 'eur']):
                    print('\nВНЕСЕНИЕ EUR')
                    print('(!) Сумма вносимых средств не может быть менее 5 EUR и более 100000 EUR')
                    print('(!) Банкомат принимает только купюры номиналом от 5 EUR')
                    while True:
                        eur_deposit = input('Введите сумму внесения средств (целое число): ')
                        if eur_deposit == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if check_correct_int(eur_deposit):
                            eur_deposit = int(eur_deposit)
                        else:
                            print('ОШИБКА. Некорректный ввод суммы')
                            print()
                            continue

                        if 5 <= eur_deposit <= 100000:
                            if eur_deposit == (eur_deposit // 5 * 5):  # Корректные купюры
                                cur.execute('''
                                    UPDATE Users_data
                                    SET Balance_EUR = Balance_EUR + ?
                                    WHERE Card_number = ?;
                                ''', (eur_deposit, card_number))
                                db.commit()
                                print(f'Внесение {eur_deposit} EUR успешно!')
                                SQLatm.info_balance(card_number)
                                return
                            elif eur_deposit != (eur_deposit // 5 * 5):
                                print('ОШИБКА внесения средств. Банкомат не принимают купюры номиналом менее 5 EUR')
                                print(f'*Попробуйте внести {eur_deposit // 5 * 5}')
                                print()
                                continue
                        else:
                            print('ОШИБКА. Недопустимая сумма.')
                            print()
                else:
                    print('ОШИБКА. Недоступная валюта.')
                    print()
                    continue


    @staticmethod
    def transfer_money(card_number):
        '''Перевод денег на карту другого пользователя'''
        with sqlite3.connect('atm.db') as db:
            cur = db.cursor()
            print('ВАЛЮТНЫЙ ПЕРЕВОД')
            print('(!) Поддерживаются любые суммы, но не менее 0.0001 или')
            while True:

                recipient_card = input('Введите номер карты, на которую желаете осуществить перевод: ')
                if recipient_card == '00':
                    print('--> возвращение в главное меню')
                    print()
                    return

                if check_digit_card(recipient_card):
                    recipient_card = int(recipient_card)
                else:
                    print('ОШИБКА. Некорректный номер карты')
                    print()
                    continue

                if recipient_card == card_number:
                    print('ОШИБКА. Невозможно осуществить перевод самому себе.')
                    print()

                elif SQLatm.get_user_balance(recipient_card) == None:
                    print('ОШИБКА. Пользователя с данным номером карты не существует.')
                    print()

                elif SQLatm.get_user_balance(recipient_card) != None:
                    # Необходимо убедиться, что у получателя и отправителя есть счета в валюте, что перевод возможен
                    recipient_user_balance = SQLatm.get_user_balance(recipient_card)
                    r_balance_rub = recipient_user_balance[0]
                    r_balance_usd = recipient_user_balance[1]
                    r_balance_eur = recipient_user_balance[2]

                    user_balance = SQLatm.get_user_balance(card_number)
                    balance_rub = user_balance[0]
                    balance_usd = user_balance[1]
                    balance_eur = user_balance[2]

                    rub_transfer = False
                    usd_transfer = False
                    eur_transfer = False

                    if balance_rub != None and balance_rub > 0 and r_balance_rub != None:
                        rub_transfer = True  # Рублевый перевод между пользователями возможен
                    if balance_usd != None and balance_usd > 0 and r_balance_usd != None:
                        usd_transfer = True
                    if balance_eur != None and balance_eur > 0 and r_balance_eur != None:
                        eur_transfer = True

                    if rub_transfer == False and usd_transfer == False and eur_transfer == False:
                        print('К сожалению, перевод невозможен по причине отсутствия у получателя счетов в вашей валюте.')
                        print('Или по причине отсутствия денег на вашем счете.')
                        print()
                        return

                    while True:
                        print('Для перевода получателю доступны следующие валюты: ')
                        if rub_transfer:
                            print(f'1. RUB в размере не более {balance_rub} RUB')
                        if usd_transfer:
                            print(f'2. USD в размере не более {balance_usd} USD')
                        if eur_transfer:
                            print(f'3. EUR в размере не более {balance_eur} EUR')
                        print('\nКакую валюту Вы желаете перевести? Введите цифру или название валюты')
                        choice_cur_transfer = input(': ')
                        if choice_cur_transfer == '00':
                            print('--> возвращение в главное меню')
                            print()
                            return

                        if rub_transfer and (choice_cur_transfer in ['1', 'RUB', 'rub']):
                            print('\nВы выбрали RUB')
                            while True:
                                desired_transfer = input('Введите сумму, которую желаете перевести: ')
                                if desired_transfer == '00':
                                    print('--> возвращение в главное меню')
                                    print()
                                    return

                                for el in desired_transfer:
                                    if el.isdigit() or el == '.':
                                        pass
                                    else:
                                        print('ОШИБКА. Некорректная сумма')
                                        print()

                                try:
                                    desired_transfer = float(desired_transfer)
                                except:
                                    print('ОШИБКА. Некорректная сумма')
                                    print()
                                    continue

                                if desired_transfer % 1 < 0.0001:
                                    print('ОШИБКА. Некорректное значение, после точки не может быть более 4 цифр')
                                    continue

                                if desired_transfer < 0.0001:
                                    print('ОШИБКА. Сумма перевода не может быть меньше 0.0001.')
                                    print()

                                elif desired_transfer > balance_rub:
                                    print('На балансе недостаточно средств для перевода данной суммы.')
                                    print(f'Ваша максимальная сумма для перевода: {balance_rub} RUB')
                                    print()

                                else:
                                    # Снимаем средства со счета отправителя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_RUB = Balance_RUB - ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, card_number))
                                    # Зачисляем средства на счет получателя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_RUB = Balance_RUB + ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, recipient_card))
                                    db.commit()
                                    print(f'Перевод {desired_transfer} RUB успешно!')
                                    SQLatm.info_balance(card_number)
                                    return


                        if usd_transfer and (choice_cur_transfer in ['2', 'USD', 'usd']):
                            print('\nВы выбрали USD')
                            while True:
                                desired_transfer = input('Введите сумму, которую желаете перевести: ')
                                if desired_transfer == '00':
                                    print('--> возвращение в главное меню')
                                    print()
                                    return

                                for el in desired_transfer:
                                    if el.isdigit() or el == '.':
                                        pass
                                    else:
                                        print('ОШИБКА. Некорректная сумма')
                                        print()

                                try:
                                    desired_transfer = float(desired_transfer)
                                except:
                                    print('ОШИБКА. Некорректная сумма')
                                    print()
                                    continue

                                if desired_transfer % 1 < 0.0001:
                                    print('ОШИБКА. Некорректное значение, после точки не может быть более 4 цифр')
                                    continue

                                if desired_transfer < 0.0001:
                                    print('ОШИБКА. Сумма перевода не может быть меньше 0.0001.')
                                    print()

                                elif desired_transfer > balance_usd:
                                    print('На балансе недостаточно средств для перевода данной суммы.')
                                    print(f'Ваша максимальная сумма для перевода: {balance_usd} USD')
                                    print()

                                else:
                                    # Снимаем средства со счета отправителя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_USD = Balance_USD - ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, card_number))
                                    # Зачисляем средства на счет получателя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_USD = Balance_USD + ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, recipient_card))
                                    db.commit()
                                    print(f'Перевод {desired_transfer} USD успешно!')
                                    SQLatm.info_balance(card_number)
                                    return

                        if eur_transfer and (choice_cur_transfer in ['3', 'EUR', 'eur']):
                            print('\nВы выбрали EUR')
                            while True:
                                desired_transfer = input('Введите сумму, которую желаете перевести: ')
                                if desired_transfer == '00':
                                    print('--> возвращение в главное меню')
                                    print()
                                    return

                                for el in desired_transfer:
                                    if el.isdigit() or el == '.':
                                        pass
                                    else:
                                        print('ОШИБКА. Некорректная сумма')
                                        print()

                                try:
                                    desired_transfer = float(desired_transfer)
                                except:
                                    print('ОШИБКА. Некорректная сумма')
                                    print()
                                    continue

                                if desired_transfer % 1 < 0.0001:
                                    print('ОШИБКА. Некорректное значение, после точки не может быть более 4 цифр')
                                    continue

                                if desired_transfer < 0.0001:
                                    print('ОШИБКА. Сумма перевода не может быть меньше 0.0001.')
                                    print()

                                elif desired_transfer > balance_eur:
                                    print('На балансе недостаточно средств для перевода данной суммы.')
                                    print(f'Ваша максимальная сумма для перевода: {balance_eur} EUR')
                                    print()

                                else:
                                    # Снимаем средства со счета отправителя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_EUR = Balance_EUR - ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, card_number))
                                    # Зачисляем средства на счет получателя
                                    cur.execute('''
                                        UPDATE Users_data
                                        SET Balance_EUR = Balance_EUR + ?
                                        WHERE Card_number = ?;
                                    ''', (desired_transfer, recipient_card))
                                    db.commit()
                                    print(f'Перевод {desired_transfer} EUR успешно!')
                                    SQLatm.info_balance(card_number)
                                    return

                        else:
                            print('ОШИБКА. Недоступная валюта')
                            print()
                            continue


    @staticmethod
    def input_operation(card_number):
        print('\nДобро пожаловать в ATM Script!')
        print('(!) Для возвращения с любого этапа операции в главное меню введите 00')
        print()
        while True:
            operation = input('Введите номер операции, которую хотите совершить:\n'
                              '1. Узнать баланс\n'
                              '2. Снять денежные средства \n'
                              '3. Внести денежные средства\n'
                              '4. Перевести средства\n'
                              '0. Завершить работу\n'
                              ': ')
            print()
            if operation == '1':
                SQLatm.info_balance(card_number)
            elif operation == '2':
                SQLatm.withdraw_money(card_number)
            elif operation == '3':
                SQLatm.deposit_money(card_number)
            elif operation == '4':
                SQLatm.transfer_money(card_number)
            elif operation == '0':
                print('Завершение работы. До скорых встреч!')
                break
            else:
                print('ОШИБКА. Действие не распознано.')
                print()