#!-*- coding: utf-8 -*-

from itertools import cycle
from random import randint

import pytest
from faker import Faker

fake = Faker()


def calculate_dv(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    dv = (-s) % 11
    if dv == 10:
        return 'K'
    return dv


def generate_rut():
    rut = randint(10000000, 99999999)
    return '{rut}-{dv}'.format(rut=rut, dv=calculate_dv(rut))


@pytest.fixture(scope='function')
def customer_kwargs():
    customer_id = generate_rut()
    return dict(
        customer_id=customer_id,
        customer_code=fake.ssn(),
        name=fake.company(),
        address=fake.street_address(),
        city=fake.city(),
        zip_code=fake.postcode(),
        website=fake.url()
    )
