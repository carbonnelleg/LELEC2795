# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 15:01:47 2024

@author: carbonnelleg
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


def main() -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # current directory path + relative path to the directory containing data
    # MODIFY NEXT LINE IF NEEDED
    dir_name = os.path.abspath(
        current_dir + '/../Labos/Lab 3 - OFDM/Data/2024-12-09 140102 977')
    # DO NOT REMOVE NAMES, SIMPLY ADD NEW NAMES IF NEEDED
    names = [
        '# of Iterations',
        'Average Bit-Error Rate',
        'BER',
        'BER vs frequency offset',
        'Channel EstimationEqualization Parameters',
        'Control Information For Packet HeaderTail',
        'Equalize Channel',
        'error out',
        'Error Statistic',
        'Estimated Offset',
        'frequency values',
        'I Data',
        'Measured Channel Impairements',
        'Modulation Type',
        'OFDM Parameters',
        'Packet Length (bits)',
        'Power Delay Profile',
        'Progress',
        'Pulse Shaping Parameters',
        'Q Data',
        'Received Constellation',
        'Received Eye Diagram',
        'RX oversample factor',
        'RX Sample Rate',
        'Synchronization Options',
        'TX Channel Model Parameters',
        'TX Oversample Factor',
        'TX Sample Rate'
    ]

    roots: dict[str, Root] = get_roots(names, dir_name)
    global data
    data = get_data(roots)


if __name__ == '__main__':
    main()
