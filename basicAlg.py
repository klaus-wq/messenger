from PyQt5 import QtWidgets

#вычисляет a mod p или -a mod p
#первый символ числа может быть любой, если -, то отриц, иначе положит
def amodp(a, p):
    # numb = '0123456789'
    # if not a or not p:
    #     msgBox = QtWidgets.QMessageBox()
    #     msgBox.setWindowTitle("Ошибка")
    #     msgBox.setText("Введите a и p!")
    #     msgBox.exec_()
    # for i in p:
    #     if i not in numb:
    #         msgBox = QtWidgets.QMessageBox()
    #         msgBox.setWindowTitle("Ошибка")
    #         msgBox.setText("Введите число!")
    #         msgBox.exec_()
    # for i in range(1, len(a)):
    #     if a[i] not in numb:
    #         msgBox = QtWidgets.QMessageBox()
    #         msgBox.setWindowTitle("Ошибка")
    #         msgBox.setText("Введите число!")
    #         msgBox.exec_()
    # if a[0] == '-' and len(a) == 1:
    #     msgBox = QtWidgets.QMessageBox()
    #     msgBox.setWindowTitle("Ошибка")
    #     msgBox.setText("Введите число!")
    #     msgBox.exec_()
    a = str(a)
    if a[0] == '-' and len(a) != 1:
        newA = int(a[1:])
        k = 1
        while k*int(p) < newA:
            k+=1
        res = (-1)*newA + int(p)*k
    # elif a[0] not in numb:
    #     res = int(a[1:]) % int(p)
    else:
        res = int(a) % int(p)
    return res

def gcd(a, b):
    if a == 0 or a < 0 or b == 0 or b < 0:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Ошибка")
        msgBox.setText("Числа целые и положительные!")
        msgBox.exec_()
        return None
    # if a < b:
    #     a, b = b, a

    while b != 0:
        a, b = b, a % b
    return str(a)

    # x, xx, y, yy = 1, 0, 0, 1
    # while b:
    #     q = a // b
    #     a, b = b, a % b
    #     x, xx = xx, x - xx * q
    #     y, yy = yy, y - yy * q
    # return x

def exgcd(a, p):
    if a == 0 or a < 0 or p == 0 or p < 0:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Ошибка")
        msgBox.setText("Числа целые и положительные!")
        msgBox.exec_()
        return None
    if gcd(a, p) != '1':
        return 'Обратный элемент не существует!'
    a = int(a)
    p = int(p)
    p1 = p
    # if p == 0:
    #     return 'p != 0!'

    u2, v2 = 1, 0
    while p != 0:
        q = a // p
        t1, t2 = a % p, u2 - q * v2
        a, u2 = p, v2
        p, v2 = t1, t2
    if u2 < 0:
        u2 = (u2 + p1) % p1
    return str(u2)

def degree(a, x, p):
    x = str(bin(x))[2:]
    x = x[::-1]

    y = 1
    s = a
    for i in range(len(x)):
        if x[i] == '1':
            y = (y * s) % p
        s = (s * s) % p
    return str(y)

def degree1(a, x, p):
    r = 1
    while x > 2:
        if x % 2 == 0:
            a = (a * a) % p
            x = x // 2
        else:
            r = (r * a) % p
            x = x - 1
    a = (a * a) % p
    r = (r * a) % p
    return str(r)

def exgcd1(a, p):
    a = int(a)
    p = int(p)
    p1 = p
    # if p == 0:
    #     return 'p != 0!'

    u2, v2, u3, v3 = 1, 0, 0, 1
    while p != 0:
        q = a // p
        t1, t2, t3 = a % p, u2 - q * v2, u3 - q * v3
        a, u2, u3 = p, v2, v3
        p, v2, v3 = t1, t2, t3
    if u2 < 0:
        u2 = (u2 + p1) % p1
    if u3 < 0:
        u3 = (u3 + p1) % p1
    return str(u2), str(u3)