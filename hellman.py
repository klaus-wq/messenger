from primes import generator, isPrime, degree

def find_pq():
    q = generator(10**100, 10**101, 1)[0]
    p = 2*q + 1
    while isPrime(p) == False:
        q = generator(10**100, 10**101, 1)[0]
        p = 2 * q + 1
    return p, q

def find_g(q, p):
    g = 2
    while degree(g, q, p) == '1':
        g+=1
    return g