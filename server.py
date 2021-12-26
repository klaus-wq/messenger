import time
from datetime import datetime

from flask import Flask, request, abort
from primes import generator
from hellman import find_pq, find_g
from random import randint
from RSA import find_d, find_e, RSA
from SHA1 import SHA1
from gost import GOST_zamena
from GOSTh import GOST94

app = Flask(__name__)

msg = []

cmkeys = []

primes = generator(10 ** 100, 10 ** 101, 2)
p_rsa = primes[0]
q_rsa = primes[1]
serv_pubkey_rsa = find_e(p_rsa, q_rsa)
serv_seckey_rsa = find_d(serv_pubkey_rsa, p_rsa, q_rsa)
p_dh, q_dh = find_pq()
g_dh = find_g(q_dh, p_dh)
serv_seckey_dh = randint(10 ** 50, p_dh - 1)
serv_pubkey_dh  = pow(g_dh, serv_seckey_dh, p_dh)
common_key_dh = 0
client_pubkey_rsa = 0
client_pub_key_dh = 0
server_N = p_rsa * q_rsa
client_N = 0

@app.route("/keys")
def gen_keys():
    return {'server_N': server_N, 'serv_pubkey_dh': serv_pubkey_dh, 'serv_pubkey_rsa': serv_pubkey_rsa, 'p_dh': p_dh, 'g_dh': g_dh}

@app.route("/get_keys", methods=['POST'])
def get_keys():
    data = request.json
    client_pubkey_dh = int(data['client_pub_key_dh'])
    client_pubkey_rsa = int(data['client_pubkey_rsa'])
    client_N = int(data['client_N'])
    client_name = data['client_name']
    common_key_dh = pow(client_pubkey_dh, serv_seckey_dh, p_dh)
    key = {
        'client_name': client_name,
        'client_pubkey_rsa': client_pubkey_rsa,
        'client_N': client_N,
        'common_key_dh': common_key_dh
    }
    cmkeys.append(key)
    return {'ok': True}

@app.route("/send_msg", methods=['POST'])
def send_msg():
    data = request.json
    shift_h_text = data['shift_h_text']
    shifr_text = data['shifr_text_str']
    sender_name = data['sender_name']
    reciever_name = data['reciever_name']

    for i in range(len(cmkeys)):
        if cmkeys[i]['client_name'] == sender_name:
            common_key_dh = cmkeys[i]['common_key_dh']
            client_pubkey_rsa = cmkeys[i]['client_pubkey_rsa']
            client_N = cmkeys[i]['client_N']

    #5 Сервер расшифровывает хэш с помощью своего закрытого ключа
    rasshifr_h_text = pow(shift_h_text, client_pubkey_rsa, client_N)

    key_for_gost = bin(common_key_dh)[2:][:256]

    #6 Сервер расшифровывает сообщение с помощью сессионного ключа Алисы и Сервера (или Боба и Сервера, если отправляется сообщение от Боба Алисе)
    rasshifr_text = GOST_zamena(key_for_gost, shifr_text, 0)

    #7 Сервер вычисляет хэш сообщения и сравнивает его с полученным расшифрованным хэшем
    h_text = int(SHA1(rasshifr_text), 16)
    #h_text = int(GOST94(rasshifr_text, '00000'.zfill(256)), 16)
    #8 Если они совпадают, то в служебной информации сервера фиксируется «Успешная проверка ЭП сообщения», иначе сигнализируется «Ошибка проверки ЭП сообщения» и отправляется сообщение Алисе, что произошла ошибка на стороне сервера
    if h_text != rasshifr_h_text:
        return {'ok': False}

    for i in range(len(cmkeys)):
        if cmkeys[i]['client_name'] == reciever_name:
            reciever_pubkey_rsa = cmkeys[i]['client_pubkey_rsa']
            reciever_common_key_dh = cmkeys[i]['common_key_dh']
            reciever_N = cmkeys[i]['client_N']

    key_for_gost = bin(reciever_common_key_dh)[2:][:256]

    #9 В случае успешной проверки ЭП, Сервер зашифровывает хэш на открытом ключе Боба (в случае отправки сообщения от Боба Алисе – на открытом ключе Алисы)
    shifr_h = pow(h_text, serv_seckey_rsa, server_N)
    #10 .В случае успешной проверки ЭП, Сервер зашифровывает сообщение симметричным алгоритмом на сессионном ключе Боба и Сервера (в случае отправки сообщения от Боба Алисе – на сессионном ключе Алисы и Сервера)
    shifr_text_1_str = GOST_zamena(key_for_gost, rasshifr_text, 1)

    #11 Зашифрованное сообщение и зашифрованный хэш отправляются Бобу (или Алисе)
    message = {
        'time': time.time(),
        'name': sender_name,
        'reciever_name': reciever_name,
        'shifr_h': shifr_h,
        'shifr_text_1_str': shifr_text_1_str,
    }
    msg.append(message)
    return {'ok': True}

@app.route("/get_msg", methods=['POST'])
def get_msg():
    data = request.json
    reciever_name = data['client_name']
    after = data['after']

    try:
        after = float(after)
    except:
        return abort(400)

    res = {}
    for message in msg:
        if reciever_name == message['reciever_name']:
            if message['time'] > after:
                res = message
    return res

app.run()