# -*- coding: utf-8 -*-
"""utility functions and classes

`jspcap.utilities` contains several useful functions and
classes which are fundations of `jspcap`, including
decorater function `seekset` and `beholder`, 
dict-like class `Info`, tuple-like class `VersionInfo`,
and special class `ProtoChain`.

"""
from jspcap.utilities.decorators import *
from jspcap.utilities.exceptions import *
from jspcap.utilities.validations import *


__all__ = ['seekset_ng', 'beholder_ng']
