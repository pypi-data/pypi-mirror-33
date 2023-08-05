#!/usr/bin/env python
from public import public
import shields

# http://shields.io/
# https://img.shields.io/badge/<SUBJECT>-<STATUS>-<COLOR>.svg

# brightgreen, green, yellowgreen, yellow, orange, red, lightgrey, blue


@public
class Badge(shields.Abstract):
    path = "badge/{subject}-{status}-{color}.svg"
    subject = None
    status = None
    color = "green"
