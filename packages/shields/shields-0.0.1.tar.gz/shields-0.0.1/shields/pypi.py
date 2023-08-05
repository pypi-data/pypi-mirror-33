#!/usr/bin/env python
from public import public
import shields

# http://shields.io/
# version:              https://img.shields.io/pypi/v/Django.svg

# License:              https://img.shields.io/pypi/l/Django.svg
# Wheel:                https://img.shields.io/pypi/wheel/Django.svg
# Format:               https://img.shields.io/pypi/format/Django.svg
# pyversions:           https://img.shields.io/pypi/pyversions/Django.svg
# Implementation:       https://img.shields.io/pypi/implementation/Django.svg
# Status:               https://img.shields.io/pypi/status/Django.svg


@public
class Pypi(shields.Abstract):
    name = None
    link = "https://pypi.org/pypi/{name}/"
    path = "pypi/{cls}/{name}.svg"

    def __init__(self, name, **kwargs):
        self.name = name
        self.update(kwargs)

    @property
    def cls(self):
        return self.__class__.__name__.lower()


@public
class V(Pypi):
    pass


@public
class L(Pypi):
    pass


@public
class Wheel(Pypi):
    pass


@public
class Format(Pypi):
    pass


@public
class Pyversions(Pypi):
    pass


class Implementation(Pypi):
    pass


class Status(Pypi):
    pass
