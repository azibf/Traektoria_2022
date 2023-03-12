import socket
import datetime
import csv
import dns.resolver
from pythonping import ping
import logging
import requests
from time import sleep

logging.basicConfig(filename=f'{datetime.datetime}.log', encoding='utf-8', level=logging.DEBUG)


class Checker:
    '''
    Базовый класс для всех чекеров
    '''
    def __init__(self, filename):
        while filename.strip()[-4:-1] != '.csv':
            filename = input('Неверный формат файла, введите другое имя файла: ')
        self.ip_port_list = None
        self.upload_csv(filename)
        self.socket = socket.socket()

    def upload_csv(self, filename):
        '''
        Обработка файла, поданного программе на вход
        :param filename: Имя файла
        :return: Сохраняет список из кортежей (IP, port)
        '''
        with open(filename, 'r') as file:
            ip_port_list = []
            table = csv.reader(file, delimiter=' \n', quotechar=';')
            for row in table:
                self.ip_port_list = (row[1], row[2])


class InternetChecker(Checker):
    '''
    Наследник Checker
    Класс для проверки стабильности сети
    '''
    def __init__(self, ip):
        super(Checker, self).__init__()

    @property
    def port_checking(self):
        '''
        Проверка для все указанных адресов, открыты ли заданные порты
        :return: Вывод в консоль и логирование проверки порта
        '''
        for elem in self.ip_port_list:
            ip, port = elem[0], elem[1]
            flag = 0
            try:
                self.socket.connect_ex((ip, port))
                print(f'{datetime.datetime}:PORT_CHECKING:У IP {ip} порт {port} доступен')
                logging.info(f'{datetime.datetime}:PORT_CHECKING:У IP {ip} порт {port} доступен')
            except Exception:
                print(f'{datetime.datetime}:PORT_CHECKING: порт {port} закрыт')
                logging.info(f'{datetime.datetime}:PORT_CHECKING:У IP {ip} порт {port} закрыт')
            finally:
                self.socket.close()

    @property
    def ip_checking(self):
        '''
        Проверка всех указанныз адресов на доступность
        :return: Вывод в консоль и логирование проверки доступности адресов
        '''
        for elem in self.ip_port_list:
            ip = elem[0]
            try:
                result = str(ping(ip))
                loss = result.count('Request timed out')
                if loss == 4:
                    print(f'{datetime.datetime}:IP_CHECKING:{ip} недоступен')
                    logging.error(f'{datetime.datetime}:IP_CHECKING:{ip} недоступен')
                elif 2 <= loss <= 3:
                    print(f'{datetime.datetime}:IP_CHECKING:{ip} доступен.Соединение нестабильно.')
                    logging.warning(f'{datetime.datetime}:IP_CHECKING:{ip} доступен.Соединение нестабильно.')
                else:
                    print(f'{datetime.datetime}:IP_CHECKING:{ip} доступен')
                    logging.info(f'{datetime.datetime}:IP_CHECKING:{ip} доступен')
            except:
                print(f'{datetime.datetime}:IP_CHECKING:Ошибка во время проверки {ip}')
                logging.info(f'{datetime.datetime}:IP_CHECKING:Ошибка во время проверки {ip}')

    @property
    def dns_checking(self):
        '''
        Проверка для всех указанных служб на ответ DNS (наличие A записи)
        :return: Вывод в консоль и логирование проверки ответа DNS сервера
        '''
        for elem in self.ip_port_list:
            ip, port = elem[0], elem[1]
            try:
                answers = dns.resolver.query(f'{ip}:{port}', 'NS')
                print(f'{datetime.datetime}:DNS_CHECKING:Ответ сервера DNS для {ip} получен: {answers}')
                logging.info(f'{datetime.datetime}:DNS_CHECKING:Ответ сервера DNS для {ip} получен')
            except:
                print(f'{datetime.datetime}:DNS_CHECKING:Нет ответа от сервера DNS {ip}')
                logging.error(f'{datetime.datetime}:DNS_CHECKING:Нет ответа от сервера DNS {ip}')


class ClientChecker(Checker):
    '''
    Наследние Cheker
    Класс для проверки стабильности соединения с клиентской стороны
    '''
    def __init__(self, ip):
        super(Checker, self).__init__()

    def client_checking(self):
        '''
        Проверка для всех указанных адресов состояния сервера в соответсвии со код состояния
        200 - успешное функционирование
        4хх - ошибка на стороне клиента
        :return: Вывод в консоль и логирование ответа сервера на GET-запрос
        '''
        for elem in self.ip_port_list:
            ip, port = elem[0], elem[1]
            try:
                answer = requests.get(f"http://{ip}").status_code
                if answer == 200:
                    print(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
                    logging.info(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
                elif 400 <= answer <= 499:
                    print(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Ошибка на стороне клиента {ip}')
                    logging.warning(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Ошибка на стороне клиента{ip}')
            except Exception:
                print(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Для {ip} неизвестная проблема')
                logging.warning(f'{datetime.datetime}:CLIENT_STATUS_CODE_CHECKING:Для {ip} неизвестная проблема')
            finally:
                self.socket.close()

class ServerChecker(Checker):
    '''
    Наследник Cheker
    Класс для проверки соединения со стороны сервера
    '''
    def __init__(self, ip):
        super(Checker, self).__init__()

    @property
    def status_code_checking(self):
        '''
        Проверка для всех указанных адресов состояния сервера в соответсвии со код состояния
        200 - успешное функционирование
        503, 507 - сервер перегружен
        5хх - остальные коды ошибки
        :return: Вывод в консоль и логирование ответа сервера на GET-запрос
        '''
        for elem in self.ip_port_list:
            ip, port = elem[0], elem[1]
            try:
                answer = requests.get(f"http://{ip}").status_code
                if answer == 200:
                    print(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
                    logging.info(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
                elif answer in [503, 507]:
                    print(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Сервер {ip} перегружен')
                    logging.warning(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Сервер {ip} перегружен')
                elif 500 <= answer <= 599:
                    print(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Ошибка конфигурации сервер {ip}')
                    logging.warning(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Ошибка конфигурации сервера {ip}')
            except Exception:
                print(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Служба сервера {ip} остановлена')
                logging.warning(f'{datetime.datetime}:SERVER_STATUS_CODE_CHECKING:Служба сервера {ip} остановлена')
            finally:
                self.socket.close()


class ServiceCheker(InternetChecker, ServerChecker, ClientChecker):
    '''
    Наследник InternetChecker, ServerChecker, ClientChecker
    Общая проверка служб
    '''
    def __init__(self, ip):
        super().__init__()
        self.flag = True

    @property
    def start_checker(self):
        '''
        Запуск проверок
        :return: Начало проверок
        '''
        print(f'{datetime.datetime}:START:Начало проверки')
        logging.warning(f'{datetime.datetime}:START:Начало проверки')
        self.flag = True
        while self.flag:
            self.full_checking
            sleep(25)

    @property
    def stop_cheker(self):
        '''
        Остановка проверок
        :return: Остановка проверок
        '''
        print(f'{datetime.datetime}:STOP:Завершение проверки')
        logging.warning(f'{datetime.datetime}:STOP:Завершение проверки')
        self.flag = False


    @property
    def internet_checking(self):
        '''
        Вызов всех проверок на состояние сети
        :return: None
        '''
        self.ip_checking
        self.dns_checking
        self.port_checking

    @property
    def server_side_checking(self):
        '''
        Вызов всех проверок на стороне сервера
        :return: None
        '''
        self.status_code_checking

    @property
    def client_side_checking(self):
        '''
        Вызов всех проверок на стороне клиента
        :return: None
        '''
        self.client_checking

    @property
    def full_checking(self):
        '''
        Вызов всех проверок
        :return: None
        '''
        self.internet_checking
        self.server_side_checking
        self.client_side_checking
