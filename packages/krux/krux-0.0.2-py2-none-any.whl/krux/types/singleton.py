# -*- coding:utf-8 -*-


class Singleton(object):
    """A do-nothing class.
    From A. Martelli et al. Python Cookbook. (O'Reilly)
    Thanks to Juergen Hermann."""
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst
