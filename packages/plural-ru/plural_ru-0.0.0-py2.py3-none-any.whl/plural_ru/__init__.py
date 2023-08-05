#!/usr/bin/env python
# -*- coding: utf-8 -*-
from public import public


@public
def ru(value, quantitative):
    if value % 100 in (11, 12, 13, 14):
        return quantitative[2]
    if value % 10 == 1:
        return quantitative[0]
    if value % 10 in (2, 3, 4):
        return quantitative[1]
    return quantitative[2]
