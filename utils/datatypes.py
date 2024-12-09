# -*- coding: utf-8 -*-
"""
Created on Fri Nov 1 11:02:07 2024

@author: carbonnelleg
"""

import xml.etree.ElementTree as ET
import struct
import numpy as np
from dataclasses import dataclass
from typing import Any

# xml structures (ElementTree) use namespaces to identify each element in the structure
# We define the namespaces that are used through all LabView data files
ns = {
    'lv': 'http://www.ni.com/LabVIEW.VI',
    'pf': 'http://www.ni.com/PlatformFramework',
    'ctrl': 'http://www.ni.com/Controls.LabVIEW.Design'
}


def get_tag(elem: ET.Element) -> str:
    """
    Parameters
    ----------
    elem : ET.Element
        Any ET.Element of an ElementTree structure

    Returns
    -------
    str
        Returns tag of elem with its namespace stripped
    """
    tag: str = elem.tag
    namespace: str
    for namespace in ns.values():
        tag = tag.removeprefix('{'+namespace+'}')
    return tag


@dataclass(slots=True)
class DataType:

    tag: str
    data: Any

    def __init__(self, elem: ET.Element) -> None:
        """
        Parameters
        ----------
        elem : ET.Element
            Any ET.Element which value can be the data of one of
            the supported subclasses of DataType

        Returns
        -------
        None
            Sets the attribute 'tag' to get_tag(elem)
            Asserts tag is either p.DefaultValue, Array, Elem or Field
            Sets the attribute 'data' to None
        """
        self.tag: str = get_tag(elem)
        assert (self.tag == 'p.DefaultValue' or self.tag == 'Array' or
                self.tag == 'Elem' or 'Field' in self.tag)
        self.data = None

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()


class TypeTable:

    # Define datatypes
    datatypes = {
        'UInt16': 'Int32',
        'UInt32': 'Int32',
        'Int32': 'Int32',
        'Double': 'Double',
        'ComplexDouble': 'ComplexDouble',
        'Boolean': 'Boolean',
        'String': 'String',
        'Error': 'Error',
        'Enumeration': 'Enumeration',
        'Double[]': 'DoubleArray',
        'Wfm(Double)': 'WfmDouble',
    }

    def __init__(self, root: ET.Element):
        self.tag = get_tag(root).strip('(),').replace('[]', 'Array')
        match self.tag:
            case 'Class':
                self.type = Cluster
                self.subtables = [TypeTable(field.find(
                    'pf:DataType/', ns)) for field in root.findall(
                    'pf:Members/pf:Field', ns)]
                self.names = [field.get('Name') for field in root.findall(
                    'pf:Members/pf:Field', ns)]
                pass
            case 'VariableArray':
                array_type = get_tag(root.find('pf:DereferenceType/', ns))
                match array_type:
                    case 'Double':
                        self.type = DoubleArray
                        self.subtables = None
                        pass
                    case 'ComplexDouble':
                        self.type = ComplexDoubleArray
                        self.subtables = None
                        pass
                    case 'UInt32':
                        self.type = IntArray
                        self.subtables = None
                        pass
                    case _:
                        self.type = Array
                        self.subtables = [
                            TypeTable(root.find('pf:DereferenceType/', ns))]
                        pass
            case 'Enumeration':
                self.type = Enumeration
                self.subtables = None
                self.enum = {}
                for member in root.findall('.//pf:EnumerationMember', ns):
                    self.enum[member.get('Value')] = member.get('Name')
            case _:
                self.type = globals()[self.datatypes[self.tag]]
                self.subtables = None

    def __len___(self):
        return self.subtables.__len__()

    def __iter__(self):
        return self.subtables.__iter__()

    def _str_list(self):
        s = [self.type.__name__]
        if self.subtables is not None:
            s += [' of [', '\n']
            for table in self:
                s += table._str_list()
                s.append('\n')
            for i, elem in enumerate(s):
                if elem == '\n':
                    s.insert(i + 1, '\t')
            s.append(']')
        return s

    def __str__(self):
        s = ''
        for elem in self._str_list():
            s += elem
        return s


class RefTable(TypeTable):

    def __init__(self, root):
        assert (root.tag == '{'+ns['pf']+'}DataTypeReferenceTable')
        self.typeID = root.find('pf:p.TypeReference', ns).get('TypeId')
        self.typetable = TypeTable(root.find('pf:p.TypeReference/', ns))

    def __len__(self):
        return self.typetable.__len__()

    def __iter__(self):
        return self.typetable.__iter__()

    def __str__(self):
        s = f'DataType ID : {self.typeID}\n'
        s += str(self.typetable)
        return s


class Int32(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = Int32
        DataType.__init__(self, value)

        self.data = int(value.text)


class String(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = String
        DataType.__init__(self, value)

        self.data = value.text


class Double(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = Double
        DataType.__init__(self, value)

        try:
            # Ensure hex_value contains only valid hexadecimal digits before unpacking
            assert (value.text[:2] == '0x')
            self.data = struct.unpack('!d', bytes.fromhex(value.text[2:]))[0]
        except ValueError:
            if value.text == '0x0':
                self.data = 0.0
            else:
                print(f"Non-hexadecimal data encountered: '{value.text}'")
                self.data = np.nan


class ComplexDouble(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = ComplexDouble
        DataType.__init__(self, value)

        try:
            real, imag = value.text.split(';')
            assert (real[:2] == '0x' and imag[:2] == '0x')
            try:
                self.real = struct.unpack('!d', bytes.fromhex(real[2:]))[0]
            except ValueError:
                if real == '0x0':
                    self.real = 0.0
                else:
                    print(f"Non-hexadecimal data encountered: '{real}'")
                    self.real = np.nan
            try:
                self.imag = struct.unpack('!d', bytes.fromhex(imag[2:]))[0]
            except ValueError:
                if imag == '0x0':
                    self.imag = 0.0
                else:
                    print(f"Non-hexadecimal data encountered: '{imag}'")
                    self.imag = np.nan
        except:
            print(f"Couldn't parse complex number correctly: {value.text}")
            self.real = np.nan
            self.imag = np.nan
        finally:
            self.data = complex(self.real, self.imag)


class Boolean(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = Boolean
        DataType.__init__(self, value)

        self.data = value.text == 'True'


class Error(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = Error
        DataType.__init__(self, value)

        self.data = {}
        for field, key, format, args in zip('123',
                                            ('error ?', 'code', 'description'),
                                            (str.__eq__, int, str.strip),
                                            (['True'], [], ['"'])):
            self.data[key] = format(value.find(
                f'.//lv:Field{field}', ns).text, *args)

        self.code = self.data['code']
        self.message = self.data['description']

    def is_error(self):
        return self.data['error ?']


class IntArray(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = IntArray
        DataType.__init__(self, value)

        if value.text == 'null':
            self.data = None
            return
        self.data = {}
        self.data['shape'] = tuple(
            [int(l) for l in value.find('.//lv:Array', ns).get('Lengths').split(',')])
        self.data['elements'] = np.zeros(
            self.data['shape'], dtype=int).flatten()

        if self.data['shape'] != (0,):
            for i, value in enumerate(value.find('.//lv:Array/lv:Elements', ns).text.split(',')):
                try:
                    self.data['elements'][i] = int(value)
                except ValueError:
                    print(
                        f"Invalid data encountered: '{value}'")
                    self.data['elements'][i] = 0
        self.data['elements'] = self.data['elements'].reshape(
            self.data['shape'])

        self.shape = self.data['shape']
        self.elements = self.data['elements']

    def __len__(self):
        return self.elements.__len__()

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, *key):
        return self.elements.__getitem__(*key)


class DoubleArray(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = DoubleArray
        DataType.__init__(self, value)

        if value.text == 'null':
            self.data = None
            return
        self.data = {}
        self.data['shape'] = tuple(
            [int(l) for l in value.find('.//lv:Array', ns).get('Lengths').split(',')])
        self.data['elements'] = np.zeros(self.data['shape']).flatten()

        if self.data['shape'] != (0,):
            for i, hex_value in enumerate(value.find('.//lv:Array/lv:Elements', ns).text.split(',')):
                try:
                    # Ensure hex_value contains only valid hexadecimal digits before unpacking
                    assert (hex_value[:2] == '0x')
                    self.data['elements'][i] = struct.unpack(
                        '!d', bytes.fromhex(hex_value[2:]))[0]
                except ValueError:
                    if hex_value == '0x0':
                        self.data['elements'][i] = 0.0
                    else:
                        print(
                            f"Non-hexadecimal data encountered: '{hex_value}'")
                        self.data['elements'][i] = np.nan
        self.data['elements'] = self.data['elements'].reshape(
            self.data['shape'])

        self.shape = self.data['shape']
        self.elements = self.data['elements']

    def __len__(self):
        return self.elements.__len__()

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, *key):
        return self.elements.__getitem__(*key)


class ComplexDoubleArray(DataType):

    def __init__(self, value: ET.Element, **kwargs):
        self.__class__ = ComplexDoubleArray
        DataType.__init__(self, value)

        if value.text == 'null':
            self.data = None
            return
        self.data = {}
        self.data['shape'] = tuple(
            [int(l) for l in value.find('.//lv:Array', ns).get('Lengths').split(',')])
        self.data['elements'] = np.zeros(
            self.data['shape'], dtype=complex).flatten()

        if self.data['shape'] != (0,):
            for i, hex_value in enumerate(value.find('.//lv:Array/lv:Elements', ns).text.split(',')):
                try:
                    hex_real, hex_imag = hex_value.split(';')
                    assert (hex_real[:2] == '0x' and hex_imag[:2] == '0x')
                    try:
                        real = struct.unpack(
                            '!d', bytes.fromhex(hex_real[2:]))[0]
                    except ValueError:
                        if hex_real == '0x0':
                            real = 0.0
                        else:
                            print(
                                f"Non-hexadecimal data encountered: '{hex_real}'")
                            real = np.nan
                    try:
                        imag = struct.unpack(
                            '!d', bytes.fromhex(hex_imag[2:]))[0]
                    except ValueError:
                        if hex_imag == '0x0':
                            imag = 0.0
                        else:
                            print(
                                f"Non-hexadecimal data encountered: '{hex_imag}'")
                            imag = np.nan
                except:
                    print(f"Couldn't parse complex number correctly: {
                          hex_value}")
                    real = np.nan
                    imag = np.nan
                finally:
                    self.data['elements'][i] = complex(real, imag)
        self.data['elements'] = self.data['elements'].reshape(
            self.data['shape'])

        self.shape = self.data['shape']
        self.elements = self.data['elements']

    def __len__(self):
        return self.elements.__len__()

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, *key):
        return self.elements.__getitem__(*key)


class WfmDouble(DoubleArray):

    def __init__(self, value: ET.Element, **kwargs):
        DoubleArray.__init__(self, value, **kwargs)
        self.__class__ = WfmDouble

        interval = value.find('.//lv:Interval', ns).text
        try:
            # Ensure interval_hex contains only valid hexadecimal digits before unpacking
            assert (interval[:2] == '0x')
            self.data['interval'] = struct.unpack(
                '!d', bytes.fromhex(interval[2:]))[0]
        except ValueError:
            print(
                f"Non-hexadecimal data encountered: '{interval}'")
            self.data['interval'] = np.nan

        self.interval = self.data['interval']


class Enumeration:

    def __init__(self, value: ET.Element, typetable: TypeTable = None, **kwargs):
        self.__class__ = Enumeration
        DataType.__init__(self, value)

        self.typetable = typetable
        self.names = self.typetable.enum

        self.data = self.names[value.text]


class Array(DataType):

    def __init__(self, value: ET.Element, typetable: TypeTable = None, **kwargs):
        self.__class__ = Array
        DataType.__init__(self, value)
        if self.tag != 'Array':
            value = value.find('lv:Array', ns)
            self.tag = get_tag(value)
        assert (self.tag == 'Array')
        self.typetable = typetable
        self.data = {}
        self.data['shape'] = tuple(
            [int(l) for l in value.get('Lengths').split(',')])
        for type in self.typetable:
            self.array = np.zeros(
                self.data['shape'], dtype=type.type.__class__).flatten()
            elements = value.findall('lv:Rank1/lv:Elem', ns)
            for i in range(np.prod(self.data['shape'])):
                self.array[i] = type.type(
                    elements[i], self.typetable.subtables[0])
            self.array.reshape(self.data['shape'])
            self.data['elements'] = np.array(
                [elem.data for elem in self.array]).reshape(self.data['shape'])
        self.shape = self.data['shape']
        self.elements = self.data['elements']

    def __len__(self):
        return self.elements.__len__()

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, *key):
        return self.array.__getitem__(*key)


class Cluster(DataType):

    def __init__(self, value: ET.Element, typetable: TypeTable = None, **kwargs):
        self.__class__ = Cluster
        DataType.__init__(self, value)
        self.typetable = typetable
        self.fields = {}
        self.names = self.typetable.names
        self.data = {}
        for i, type in enumerate(self.typetable):
            field = type.type(value.find(
                f'lv:Cluster/lv:Field{i+1}', ns), typetable=self.typetable.subtables[i])
            self.data[self.names[i]] = field.data
            self.fields[self.names[i]] = field
        self.__class__ = Cluster

    def __len__(self):
        return self.data.__len__()

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, *key):
        return self.fields.__getitem__(*key)


__all__ = [
    'ns',
    'get_tag',
    'DataType',
    'TypeTable',
    'RefTable',
    'Int32',
    'String',
    'Double',
    'ComplexDouble',
    'Boolean',
    'Error',
    'IntArray',
    'DoubleArray',
    'ComplexDoubleArray',
    'WfmDouble',
    'Enumeration',
    'Array',
    'Cluster'
]
