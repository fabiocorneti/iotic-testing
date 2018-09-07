# -*- coding: utf-8 -*-
"""Data collections.
"""
import string

__all__ = ['MACHINES']

MACHINES = ['{}.example.com'.format(machine_id) for machine_id in string.ascii_letters]
