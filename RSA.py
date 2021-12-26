from basicAlg import degree, gcd, exgcd
from primes import isPrime, generator

def generate_p_q(prime_number, start_prime):
    tmp = start_prime
    pq = []
    for i in range(2):
        while len(str(tmp)) < prime_number:
            N = 4 * tmp + 2
            U = 0
            while True:
                candidate = (N + U) * tmp + 1
                if degree(2, int(candidate - 1), int(candidate)) == '1' and degree(2, int(N + U), int(candidate)) != '1':
                    tmp = candidate
                    break
                else:
                    U = U - 2
        pq.append(tmp)
        start_prime = start_prime + 2
        while isPrime(start_prime) != True:
            start_prime = start_prime + 2
        tmp = start_prime
    p = pq[0]
    q = pq[1]
    return p, q

def find_e(p, q):
    e = generator(2, (p-1)*(q-1) - 1, 1)[0]
    while gcd(e, (p-1)*(q-1)) != '1' or exgcd(e, (p-1)*(q-1)) == 'Обратный элемент не существует!':
        #e += 1
        e = generator(2, (p-1)*(q-1) - 1, 1)[0]
    return e % (p * q)

def find_d(e, p, q):
    return int(exgcd(e, (p-1)*(q-1)))

def RSA(text, p, q, flag, file, path='', e='', d=''):
    res = ''
    if flag == 1 and file == 0:
        for i in text:
            tmp = ord(i)
            if p*q < tmp:
                return False
            res += (degree(tmp, int(e), p * q) + ' ')
    if flag == 0 and file == 0:
        text = text[:len(text) - 1]
        for i in text.split(' '):
            try:
                i = int(i)
            except Exception:
                return False
            if p*q < int(i):
                return i
            res += chr(int(degree(int(i), int(d), p * q)))
    if flag == 1 and file == 1:
        for i in text:
            res += (degree(int(i), int(e), p * q) + ' ')
    if flag == 0 and file == 1:
        text = text[:len(text) - 1]
        file = open(path, 'wb')
        for i in text.split(' '):
            file.write(bytes([int(degree(int(i), int(d), p * q))]))
        file.close()
    return res

