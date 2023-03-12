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
    def __init__(self, filename):
        while filename.strip()[-4:-1] != '.csv':
            filename = input('Неверный формат файла, введите другое имя файла: ')
        self.ip_port_list = None
        self.upload_csv(filename)
        self.socket = socket.socket()

    def upload_csv(self, filename):
        with open(filename, 'r') as file:
            ip_port_list = []
            table = csv.reader(file, delimiter=' \n', quotechar=';')
            for row in table:
                self.ip_port_list = (row[1], row[2])


class InternetChecker(Checker):
    def __init__(self, ip):
        super(Checker, self).__init__()

    @property
    def port_checking(self):
        flag = 0
        try:
            self.socket.connect_ex((self.ip, 80))
            print(f'{datetime.datatime}:PORT_CHECKING: порт 80 доступен')
            logging.info(f'{datetime.datatime}:PORT_CHECKING: порт 80 доступен')
        except Exception:
            print(f'{datetime.datatime}:PORT_CHECKING: порт 80 закрыт')
            logging.info(f'{datetime.datatime}:PORT_CHECKING: порт 80 закрыт')
        finally:
            self.socket.close()
        try:
            self.socket.connect_ex((self.ip, 443))
            print(f'{datetime.datatime}:PORT_CHECKING: порт 443 доступен')
            logging.info(f'{datetime.datatime}:PORT_CHECKING: порт 443 доступен')
        except Exception:
            print(f'{datetime.datatime}:PORT_CHECKING: порт 443 закрыт')
            logging.info(f'{datetime.datatime}:PORT_CHECKING: порт 443 закрыт')
        finally:
            self.socket.close()

    @property
    def ip_checking(self, ip):
        try:
            result = ping(self.ip)
            loss = result.count('Request timed out')
            if loss == 4:
                print(f'{datetime.datatime}:IP_CHECKING:{ip} недоступен')
                logging.error(f'{datetime.datatime}:IP_CHECKING:{ip} недоступен')
            elif 2 <= loss <= 3:
                print(f'{datetime.datatime}:IP_CHECKING:{ip} доступен.Соединение нестабильно.')
                logging.warning(f'{datetime.datatime}:IP_CHECKING:{ip} доступен.Соединение нестабильно.')
            else:
                print(f'{datetime.datatime}:IP_CHECKING:{ip} доступен')
                logging.info(f'{datetime.datatime}:IP_CHECKING:{ip} доступен')
        except:
            print(f'{datetime.datatime}:IP_CHECKING:Ошибка во время проверки {ip}')
            logging.info(f'{datetime.datatime}:IP_CHECKING:Ошибка во время проверки {ip}')

    @property
    def dns_checking(self, ip, port):
        try:
            answers = dns.resolver.query(f'{ip}:{port}', 'NS')
            print(f'{datetime.datatime}:DNS_CHECKING:Ответ сервера DNS для {ip} получен: {answers}')
            logging.info(f'{datetime.datatime}:DNS_CHECKING:Ответ сервера DNS для {ip} получен')
        except:
            print(f'{datetime.datatime}:DNS_CHECKING:Нет ответа от сервера DNS {ip}')
            logging.error(f'{datetime.datatime}:DNS_CHECKING:Нет ответа от сервера DNS {ip}')


class ClientChecker(Checker):
    def __init__(self, ip):
        super(Checker, self).__init__()

    def client_checking(self):
        print('Future...')


class ServerChecker(Checker):
    def __init__(self, ip):
        super(Checker, self).__init__()

    def status_code_checking(self, ip):
        try:
            answer = requests.get(f"http://{ip}").status_code
            if answer == 200:
                print(f'{datetime.datatime}:STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
                logging.info(f'{datetime.datatime}:STATUS_CODE_CHECKING:Сервер {ip} работает без ошибок')
            elif answer in [503, 507]:
                print(f'{datetime.datatime}:STATUS_CODE_CHECKING:Сервер {ip} перегружен')
                logging.warning(f'{datetime.datatime}:STATUS_CODE_CHECKING:Сервер {ip} перегружен')
            else:
                print(f'{datetime.datatime}:STATUS_CODE_CHECKING:Ошибка конфигурации сервер {ip}')
                logging.warning(f'{datetime.datatime}:STATUS_CODE_CHECKING:Ошибка конфигурации сервера {ip}')
        except Exception:
            print(f'{datetime.datatime}:STATUS_CODE_CHECKING:Служба сервера {ip} остановлена')
            logging.warning(f'{datetime.datatime}:STATUS_CODE_CHECKING:Служба сервера {ip} остановлена')
        finally:
            self.socket.close()


class ServiceCheker(InternetChecker, ServerChecker, ClientChecker):
    def __init__(self, ip):
        super().__init__()
        self.flag = True

    @property
    def start_checker(self):
        self.flag = True
        while self.flag:
            self.full_checking
            sleep(26)


    @property
    def internet_checking(self):
        self.ip_checking
        self.dns_checking
        self.port_checking

    @property
    def server_side_checking(self):
        self.status_code_checking

    @property
    def client_side_checking(self):
        self.client_checking

    @property
    def full_checking(self):
        self.internet_checking
        self.server_side_checking
        self.client_side_checking




