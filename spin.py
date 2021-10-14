import roles
import random


def spin(case_id: int):
    prize = []
    if case_id == 1:
        prize = spin_case_1()
    elif case_id == 2:
        prize = spin_case_2()
    elif case_id == 3:
        prize = spin_case_3()

    return prize


def spin_case_1():
    return random.choices(roles.CASE_1, weights=[10, 10, 10, 400])


def spin_case_2():
    return random.choices(roles.CASE_2, weights=[10, 10, 10, 10, 250])


def spin_case_3():
    return random.choices(roles.CASE_3, weights=[10, 10, 10, 120])
