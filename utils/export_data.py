# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 19:10:43 2024

@author: carbonnelleg
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from .datatypes import (ns, get_tag,
                        DataType, Int32, String, Double, ComplexDouble, Boolean,
                        Error, Enumeration, IntArray, DoubleArray, ComplexDoubleArray,
                        WfmDouble, TypeTable, RefTable, Array, Cluster)
import os


def get_filenames(filenames_approx: list[str], dir_name: str) -> dict[str, str]:
    """
    Retrieves the exact filenames in a directory based on approximate names.

    Parameters
    ----------
    filenames_approx : list[str]
        List of approximate filenames (well-defined parts of filenames).
    dir_name : str
        The path to the directory containing the files.

    Returns
    -------
    list[str]
        List of exact filenames matching the approximate names.
    """
    exact_filenames = {}
    all_files = os.listdir(dir_name)  # List all files in the directory

    for approx in filenames_approx:
        for file in all_files:
            if approx in file:  # Check if the approximate part matches the current file
                exact_filenames[approx] = file
                break  # Stop searching for this approximate name once a match is found

    return exact_filenames


def get_root(filepath: str) -> ET.Element:
    # Load the XML file
    tree = ET.parse(filepath)
    return tree.getroot()


class Root:

    def __init__(self, root: ET.Element):
        assert (root.tag == '{'+ns['pf']+'}SourceFile')

        reftable = root.find('.//pf:DataTypeReferenceTable', ns)
        if reftable is not None:
            self.reftable = RefTable(reftable)
        else:
            self.reftable = None

        self.items = root.findall('.//lv:DataItem', ns)
        for item in self.items:
            value = item.find('lv:p.DefaultValue', ns)
            match item.get('Name'):
                case 'Data':
                    self.dataitem = Data(item, reftable=self.reftable)
                case 'DisplayName':
                    self.name = value.text
                case 'Source':
                    self.source = value.text
                case 'Timestamp':
                    self.timestamp = datetime(
                        1, 1, 1) + timedelta(seconds=int(value.text.split(';')[0]))

    def __str__(self):
        s = ''
        if self.reftable is not None:
            s += str(self.reftable) + '\n'
        s += f'{self.name} = {self.dataitem}\n'
        return s

    def __repr__(self):
        return self.__str__()


def get_roots(names: list[str], dir_name: str) -> dict[str, Root]:
    filenames: list[str] = get_filenames(names, dir_name)
    roots: dict = {}
    for name, filename in filenames.items():
        roots[name] = Root(get_root(f'{dir_name}/{filename}'))

    return roots


def get_data(roots: dict[str, Root]) -> dict[str, DataType]:
    data: dict = {}
    for name, root in roots.items():
        data[name] = root.dataitem

    return data


class Data(DataType):

    datatypes = TypeTable.datatypes

    def __init__(self, item: ET.Element, reftable: RefTable = None):
        assert (item.tag == '{'+ns['lv']+'}DataItem'
                and item.get('Name') == 'Data')
        value = item.find('lv:p.DefaultValue', ns)

        if reftable is not None:
            self.reftable = reftable
            self.reftable.typetable.type.__init__(
                self, value, typetable=self.reftable.typetable)

        else:
            key = item.get('DataType').replace(',', '')
            globals()[self.datatypes[key]].__init__(self, value)


__all__ = [
    'get_filenames',
    'get_root',
    'Root',
    'get_roots',
    'get_data',
    'Data'
]
