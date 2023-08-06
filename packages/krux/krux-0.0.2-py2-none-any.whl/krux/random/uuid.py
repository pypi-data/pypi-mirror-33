# -*- coding:utf-8 -*-

import six
import string
from random import choice

__all__ = [
    'random_str',
    'gen_uuid4', 'gen_uuid8', 'gen_uuid10', 'gen_uuid12',
    'gen_uuid16', 'gen_uuid20', 'gen_uuid24', 'gen_uuid32',
    'gen_uuid48', 'gen_uuid64', 'gen_uuid96', 'gen_uuid128'
]

letters = string.letters if six.PY2 else string.ascii_letters
RANDOM_CHARS = letters + string.digits


def random_str(length=16, chars=RANDOM_CHARS):
    """generates random string.
    """
    return ''.join([choice(chars) for i in range(length)])


def gen_uuid4():
    return random_str(4)


def gen_uuid6():
    return random_str(6)


def gen_uuid8():
    return random_str(8)


def gen_uuid10():
    return random_str(10)


def gen_uuid12():
    return random_str(12)


def gen_uuid16():
    return random_str(16)


def gen_uuid20():
    return random_str(20)


def gen_uuid24():
    return random_str(24)


def gen_uuid32():
    return random_str(32)


def gen_uuid48():
    return random_str(48)


def gen_uuid64():
    return random_str(64)


def gen_uuid96():
    return random_str(96)


def gen_uuid128():
    return random_str(128)
