######!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import  division
# This to be sure that the result of the division of 2 integers is a real, not an integer
from __future__ import absolute_import
from __future__ import print_function


__version__ = "2.0.0"

# Import modules
import sys
import os
import copy
import numpy as np

# Import all the functions
__all__ = ['kapteyn']

from .vertprof import *
from .statsfuncs import *
