import random
from math import log
import math
import sys

sys.setrecursionlimit(1000)


class PrimerGenerator:
    def extract_nums(self, exp):
        symbols = list(exp)
        NUM = "1234567890."
        for i in range(len(symbols)):
            symbols[i] = "N" if symbols[i] in NUM else "T"
        begins = []
        ends = []
        for i in range(len(symbols) - 1):
            fn = symbols[i] + symbols[i + 1]
            if fn == "TN":
                begins.append(i)
            elif fn == "NT":
                ends.append(i)
        if exp[-1] in NUM:
            ends.append(len(exp) - 1)
        if exp[0] in NUM:
            begins = [-1] + begins
        return [(x + 1, y + 1) for x, y in zip(begins, ends)]

    def __init__(self):
        self.funcs = []

    def add_expander(self, func):
        self.funcs.append(func)

    def complexify(self, num):
        return random.choice(self.funcs)(num)

    def __rxp__(self, exp):
        x, y = random.choice(self.extract_nums(exp))
        exp = exp[:x] + "(" + self.complexify(float(exp[x:y])) + ")" + exp[y:]
        return exp

    def randexpr(self, ans, steps):
        e = str(ans)
        for i in range(steps):
            e = self.__rxp__(e)
        return e


def unmin(*args, acc=2):
    r = []
    for arg in args:
        f = round(arg, acc)
        if f > 0:
            f = str(f)
        else:
            f = "(" + str(f) + ")"
        r.append(f)
    return r


def __c_sum(num):
    a = round(random.random() * 100, 3)
    b = num - a
    a, b = unmin(a, b)
    return a + " + " + b


def __c_mul(num):
    a = num / (random.random() * 100 + 10)
    if a == 0.0:
        b = random.random()
    else:
        b = num / a
    a, b = unmin(a, b, acc=5)
    return a + " * " + b


def __c_sub(num):
    a = num + 100 ** (random.random() * 2)
    b = (a - num)
    a, b = unmin(a, b)
    return a + " - " + b


def __c_log(num):
    fr = random.randint(300, 500)
    a = math.e ** (num / fr)
    a, fr = unmin(a, fr, acc=5)
    return "log(" + a + ") * " + fr


def __l_sum(num):
    a = 100 ** (random.random() * 2)
    b = num - a
    a, b = unmin(a, b)
    return a + " + " + b


def __l_div(num):
    a = num * (random.random() * 100 + 10)
    if a == 0.0:
        b = random.random()
    else:
        b = a / num
    a, b = unmin(a, b)
    return "\\frac{" + a + "}{" + b + "}"


def __l_pow(num):
    if num == 0:
        return str(random.randint(2, 7)) + "^{-\\infty}"
    a = random.randint(0, 10) + 3
    b = math.log(abs(num), a)
    a, b = unmin(a, b)
    return ("-" if num < 0 else "") + a + "^{" + b + "}"


def __l_sqrt(num):
    a = num ** 0.5
    a = unmin(a)[0]
    return "\\sqrt{" + a + "}"


def __l_int(num):
    patterns = [
        ("x^{2}", (3 * num) ** (1 / 3), "dx"),
        ("y^{3}", (4 * num) ** (1 / 4), "dy"),
        ("\sqrt{t}", (1.5 * num) ** (2 / 3), "dt")
    ]
    p, b, f = random.choice(patterns)
    b = str(round(b, 3))
    return "\\int_{0}^{" + b + "} " + p + " " + f


def __l_sig(num):
    a = random.randint(1, 10)
    b = random.randint(1, 10) + a
    s = sum([i for i in range(a, b + 1)])
    c = num / s
    a, b, c = unmin(a, b, c)
    return "\\sum_{i=" + a + "}^{" + b + "} i*" + c


def generate_math_example(num: int):
    gen = PrimerGenerator()
    gen.add_expander(__c_sum)
    return gen.complexify(num)

