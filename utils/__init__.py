# -*- coding: utf-8 -*-
"""
Created on Fri Nov 1 10:39:55 2024

@author: carbonnelleg
"""

from .export_data import get_root, Root, Data, get_filenames, get_roots, get_data
from .datatypes import (ns, get_tag,
                        DataType, Int32, String, Double, ComplexDouble, Boolean,
                        Error, Enumeration, IntArray, DoubleArray, ComplexDoubleArray,
                        WfmDouble, TypeTable, RefTable, Array, Cluster)
import os
import importlib

__all__ = []

current_dir = os.path.dirname(os.path.realpath(__file__))

for file in os.listdir(current_dir):
    if file.endswith('.py') and file != '__init__.py':
        module_name = file[:-3]  # Remove the .py extension

        module = importlib.import_module(f'.{module_name}', package=__name__)

        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
        else:
            __all__.append(module_name)
