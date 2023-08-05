#!/usr/bin/env python
from string import Formatter
from public import public


@public
def format_keys(string):
    return [fname for _, fname, _, _ in Formatter().parse(string) if fname]
