from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDesktopWidget
import clientui
import requests
from datetime import datetime
import time
from random import randint
from RSA import find_d, find_e, RSA
from SHA1 import SHA1
from gost import GOST_zamena
from primes import generator

class Messenger(QtWidgets.QMainWindow, clientui.Ui_ClientWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.send.pressed.connect(self.send_msg)
        self.genKeys.pressed.connect(self.get_keys_from_server)

        self.p_dh = 0
        self.g_dh = 0

        primes = generator(10 ** 100, 10 ** 101, 2)
        self.p_rsa = primes[0]
        self.q_rsa = primes[1]
        self.client_N = self.p_rsa*self.q_rsa
        self.server_N = 0

        self.common_key_dh = 0
        self.serv_pubkey_dh = 0
        self.serv_pubkey_rsa = 0

        self.client_pubkey_dh = 0
        self.client_seckey_dh = 0

        self.client_pubkey_rsa = find_e(self.p_rsa, self.q_rsa)
        self.client_seckey_rsa = find_d(self.client_pubkey_rsa, self.p_rsa, self.q_rsa)

        self.after = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.get_msg)
        self.timer.start(1000)

    def get_keys_from_server(self):
        try:
            response = requests.get(
                'http://127.0.0.1:5000/keys',
            )
        except:
            return
        try:
            name = self.name.toPlainText()
            if name == '':
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Обмен ключами")
                msgBox.setText("Заполните все поля!")
                msgBox.exec_()
                return ("")

            self.server_N = response.json()['server_N']

            self.serv_pubkey_dh = response.json()['serv_pubkey_dh']
            self.serv_pubkey_rsa = response.json()['serv_pubkey_rsa']

            self.p_dh = response.json()['p_dh']
            self.g_dh = response.json()['g_dh']
            self.client_seckey_dh  = randint(10 ** 50, self.p_dh - 1)
            self.client_pubkey_dh = pow(self.g_dh, self.client_seckey_dh, self.p_dh)

            self.common_key_dh = pow(self.serv_pubkey_dh, self.client_seckey_dh, self.p_dh)

            client_N = self.client_N
            client_pubkey_dh = self.client_pubkey_dh
            client_pubkey_rsa = self.client_pubkey_rsa
            client_name = name
            response = requests.post(
                'http://127.0.0.1:5000/get_keys',
                json={
                    'client_pub_key_dh': client_pubkey_dh,
                    'client_pubkey_rsa': client_pubkey_rsa,
                    'client_name': client_name,
                    'client_N': client_N
                }
            )

            flag = response.json()['ok']
            if flag == True:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Успешно")
                msgBox.setText("Обмен ключами прошёл успешно!")
                msgBox.exec_()
                return ("")
        except:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Ошибка")
            msgBox.setText("Ошибка при обмене ключами!")
            msgBox.exec_()
            return ("")

    def print_msg(self, message):
        t = message['time']
        dt = datetime.fromtimestamp(t)
        dt = dt.strftime('%H:%M:%S')
        self.textBrowser.append(dt + ' From ' + message['name'] + ' to ' + message['reciever_name'] + ':')
        self.textBrowser.append(message['text'])
        self.textBrowser.append('')

    def get_msg(self):
        reciever_name = self.name.toPlainText()
        try:
            response = requests.post(
                'http://127.0.0.1:5000/get_msg',
                json={'after': self.after, 'client_name': reciever_name}
            )
        except:
            return

        try:
            sender_name = response.json()['name']
            shifr_h = response.json()['shifr_h']
            shifr_text_1 = response.json()['shifr_text_1_str']

            #12 Боб (Алиса) расшифровывает хэш с помощью своего закрытого ключа
            rasshirf_h = pow(shifr_h, self.serv_pubkey_rsa, self.server_N)

            key_for_gost = bin(self.common_key_dh)[2:][:256]

            #13 Боб (Алиса) расшифровывает сообщение с помощью сессионного ключа Боба и Сервера (Алисы и Сервера)
            rasshifr_text = GOST_zamena(key_for_gost, shifr_text_1, 0)

            #14 Боб (Алиса) вычисляет хэш сообщения и сравнивает его с полученным расшифрованным хэшем
            rasshifr_text_h = int(SHA1(rasshifr_text), 16)
            #rasshifr_text_h = int(GOST94(rasshifr_text, '00000'.zfill(256)), 16)
            #15 Если они совпадают, то в служебной информации Боба (Алисы) фиксируется «Успешная проверка ЭП сообщения», иначе сигнализируется «Ошибка проверки ЭП сообщения» и отправляется через сервер сообщение Алисе (Бобу), что произошла ошибка на стороне Боба (Алисы)
            if rasshifr_text_h == rasshirf_h:
                message = {
                    'time': response.json()['time'],
                    'name': sender_name,
                    'reciever_name': reciever_name,
                    'text': rasshifr_text,
                }

                #16 Расшифрованное сообщение показывается только в случае успешной проверки ЭП
                self.print_msg(message)
                self.after = response.json()['time']

            # if rasshifr_text_h != rasshirf_h:
            #     msgBox = QtWidgets.QMessageBox()
            #     msgBox.setWindowTitle("Вывод")
            #     msgBox.setText("Ошибка проверки ЭП сообщения!")
            #     msgBox.exec_()
            #     return ("")
        except:
            return

    def send_msg(self):
        try:
            name = self.name.toPlainText()
            text = self.textInput.toPlainText()
            reciever = self.reciever.toPlainText()

            if name == '' or text == '' or reciever == '':
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Отправка")
                msgBox.setText("Заполните все поля!")
                msgBox.exec_()
                return ("")

            #1 Вычисляется хэш сообщения
            h_text = int(SHA1(text), 16)
            #h_text = int(GOST94(text, '00000'.zfill(256)), 16)

            #2 Значение хэша зашифровывается с помощью асимметричного алгоритма RSA на открытом ключе Сервера
            shift_h_text = pow(h_text, self.client_seckey_rsa, self.client_N)

            #3 Сообщение зашифровывается симметричным алгоритмом (DES или ГОСТ) на общем сессионном ключе Алисы и Сервера (или Боба и Сервера, если отправляется сообщение от Боба Алисе)
            key_for_des = bin(self.common_key_dh)[2:][:256]
            shifr_text_str = GOST_zamena(key_for_des, text, 1)

            #4 Зашифрованное сообщение и зашифрованный хэш отправляются на Сервер
            try:
                response = requests.post(
                    'http://127.0.0.1:5000/send_msg',
                    json={
                        'shift_h_text': shift_h_text,
                        'shifr_text_str': shifr_text_str,
                        'sender_name': name,
                        'reciever_name': reciever
                    }
                )
            except Exception:
                return

            flag = response.json()['ok']
            if flag == True:
                message = {
                    'time': time.time(),
                    'name': name,
                    'reciever_name': reciever,
                    'text': text,
                }
                self.print_msg(message)
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Отправка")
                msgBox.setText("Успешная проверка ЭП сообщения!")
                msgBox.exec_()
                return ("")
            if flag == False:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle("Отправка")
                msgBox.setText("Ошибка проверки ЭП сообщения!")
                msgBox.exec_()
                return ("")

            self.textInput.setPlainText('')

        except:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Отправка")
            msgBox.setText("Не удалось отправить сообщение!")
            msgBox.exec_()
            return ("")



app = QtWidgets.QApplication([])
app.setWindowIcon(QtGui.QIcon('tree.png'))
application = Messenger()
application.show()
app.exec()