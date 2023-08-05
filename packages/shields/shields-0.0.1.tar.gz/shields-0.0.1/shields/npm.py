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
class Npm(shields.Abstract):
    name = None
    link = "https://www.npmjs.com/package/{name}"

    def __init__(self, name, **kwargs):
        self.name = name
        self.update(kwargs)


@public
class V(Npm):
    path = "npm/v/{name}.svg"
