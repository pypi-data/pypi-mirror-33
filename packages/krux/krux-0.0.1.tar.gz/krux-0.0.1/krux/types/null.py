# -*- coding:utf-8 -*-

from .singleton import Singleton


class NullClass(Singleton):
    """A do-nothing class.
    From A. Martelli et al. Python Cookbook. (O'Reilly)
    Thanks to Dinu C. Gherman, Holger Krekel.
    """
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "Null"
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return  self
    def __delattr__(self, name): return self
    def __len__(self): return 0
    def __iter__(self): return iter(())
    def __getitem__(self, i): return self
    def __delitem__(self, i): return self
    def __setitem__(self, i): return self


Null = NullClass()

