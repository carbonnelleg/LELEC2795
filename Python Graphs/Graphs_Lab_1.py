# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 15:34:20 2024

@author: gauti
"""

import os
import sys
# _________________________Import custom module utils__________________________
try:
    import utils
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    utils_path = os.path.abspath(current_dir + '../..')
    sys.path.append(utils_path)
    import utils
    del current_dir, utils_path
finally:
    from utils import (Root, DataType,
                       get_roots, get_data)
# _________________________________End import__________________________________
import numpy as np
from matplotlib import pyplot as plt


data: dict[str, DataType]


def plot_constellation(data: dict[str, DataType]) -> None:
    plt.scatter(data['Received Constellation'][0]['Element 1'],
                data['Received Constellation'][0]['Element 2'])
    plt.show()


def plot_Q_Data(data: dict[str, DataType]) -> None:
    Q_Data = data['Q Data']
    plt.plot(Q_Data.interval*np.arange(0, Q_Data.shape[0]), Q_Data.elements)
    plt.show()


def main() -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # current directory path + relative path to the directory containing data
    # MODIFY NEXT LINE IF NEEDED
    dir_name = os.path.abspath(
        current_dir + '/../Labos/Lab 1 - Symbol Timing/Data/2024-12-08 165753 273')
    # DO NOT REMOVE NAMES, SIMPLY ADD NEW NAMES IF NEEDED
    names = [
        '# of Iterations',
        'alpha values',
        'Channel EstimationEqualization Parameters',
        'Control Information for Packet HeaderTail',
        'error out',
        'I Data',
        'M values',
        'Measured Channel Impairements',
        'Modulation Type',
        'Output metrics',
        'Packet Length (Bits)',
        'Power Delay Profile',
        'Progress',
        'Pulse Shaping Parameters',
        'Q Data',
        'Received Constellation',
        'Received Eye Diagram',
        'RX Oversample Factor',
        'RX Sample Rate',
        'Synchronization Options',
        'Timing statistics',
        'Timing vs alpha',
        'Timing vs M',
        'TX Channel Model Parameters',
        'TX Oversample Factor',
        'TX Sample Rate'
    ]

    roots: dict[str, Root] = get_roots(names, dir_name)
    global data
    data = get_data(roots)
    plot_constellation(data)
    plot_Q_Data(data)


if __name__ == '__main__':
    main()
