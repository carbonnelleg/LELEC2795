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
from matplotlib import collections as mplc
from typing import Any
from PIL import Image


sim_data: dict[str, dict[str, Any]]


def plot_constellation(data: dict[str, DataType], ax: plt.Axes) -> mplc.PathCollection:
    pc = ax.scatter(data['Received Constellation'][0]['Element 1'],
                    data['Received Constellation'][0]['Element 2'])
    return pc


def plot_eye_diagram(data: dict[str, DataType], ax: plt.Axes) -> list[mplc.LineCollection]:
    eye_data: DataType = data['Received Eye Diagram']
    lc_list: list[mplc.LineCollection] = []
    for single_data in eye_data.elements:
        lc_list.append(
            ax.plot(np.arange(single_data['Y']['shape'][0])*single_data['dt'],
                    single_data['Y']['elements'])
        )

    return lc_list


def plot_energy_function(data: dict[str, DataType], ax: plt.Axes) -> mplc.LineCollection:
    lc = ax.plot(np.arange(data['Probe Data'].shape[0]),
                 data['Probe Data'].elements/max(data['Probe Data'].elements))
    return lc


def plot_timing_vs_alpha(data: dict[str, DataType], ax: plt.Axes) -> mplc.LineCollection:
    t_start = data['alpha values']['First value'].data
    dt = data['alpha values']['Step'].data
    t_stop = data['alpha values']['Last value'].data + dt
    lc = ax.plot(np.arange(t_start, t_stop, dt),
                 data['Timing statistics'].elements)
    return lc


def plot_timing_vs_oversample_rx(data: dict[str, DataType], ax: plt.Axes) -> mplc.LineCollection:
    lc = ax.plot(data['Timing vs M']['Element 1'].elements,
                 data['Timing vs M']['Element 2'].elements)
    return lc


def plot_sync_err_constellation(sim_data: dict[str, dict[str, Any]]) -> None:

    image_paths = []
    for j in range(5):
        fig, ax = plt.subplots()
        for i, delay_ratio in enumerate(np.arange(1.-j*.25, 1.25, 0.25)[::-1]):
            data: dict[str, DataType] = sim_data[f'3.3 {
                str(delay_ratio)}']['data']
            pc: mplc.PathCollection = plot_constellation(data, ax)
            pc.set_label(f'$\\tau_d = {delay_ratio} * T$')
        ax.legend(loc='center')
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_xlabel('Constellation I Data')
        ax.set_ylabel('Constellation Q Data')
        fig.suptitle('Received Constellation')
        image_path = f'Lab_1/3.3 Constellation {j+1}.png'
        plt.savefig(image_path, dpi=300)
        image_paths.append(image_path)

    # Generate GIF
    images = [Image.open(path) for path in image_paths]
    gif_path = 'Lab_1/Constellation_Animation.gif'
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=500,  # Duration for each frame in milliseconds
        loop=0  # Loop forever
    )


def plot_sync_err_eye_diagram(sim_data: dict[str, dict[str, Any]]) -> None:

    for i, delay_ratio in enumerate(np.arange(5, dtype=float)*.25):
        fig, ax = plt.subplots()
        data: dict[str, DataType] = sim_data[f'3.3 {str(delay_ratio)}']['data']
        lc_list: list[mplc.LineCollection] = plot_eye_diagram(data, ax)

        ax.set_xticks(ax.get_xticks(),
                      labels=[f'{label:.1f}' for label in (
                          ax.get_xticks())*1e6]
                      )
        ax.set_xlabel('Time [$\\mu s$]')
        ax.set_ylabel('|Received Symbol|')
        T = data['TX Oversample Factor'].data/data['TX Sample Rate'].data*1e6
        ax.set_title(
            f'$T = {T:.1f}\\mu s\\;\\;\\;\\;\\tau_d = {
                delay_ratio*T:.2f}\\mu s$'
        )
        fig.suptitle(f'Eye Diagram for $\\tau_d = {delay_ratio}*T$')
        plt.savefig(f'Lab_1/3.3 Eye Diagram {i+1}.png', dpi=300)


def plot_energy_function_all_pulse_filters(sim_data: dict[str, dict[str, Any]]) -> None:

    for filter_type in ['rrc', 'rect', 'rc']:
        fig, ax = plt.subplots()
        if filter_type == 'rect':
            data_dict: dict[str, Any] = sim_data[f'3.4 {filter_type}']
            data: dict[str, DataType] = data_dict['data']
            lc: mplc.LineCollection = plot_energy_function(data, ax)
        else:
            lc_list: list[mplc.LineCollection] = []
            for alpha in np.linspace(0., 1., 11):
                data_dict = sim_data[f'3.4 {filter_type} {alpha:.1f}']
                data: dict[str, DataType] = data_dict['data']
                lc = plot_energy_function(data, ax)
                lc[0].set_label(f'$\\alpha = \
                    {sim_data[f"3.4 {filter_type} {alpha:.1f}"]["alpha"]}$')
            ax.legend()
        ax.set_ylim([-.05, 1.05])
        ax.set_xticks(np.arange(data['Probe Data'].shape[0]))
        ax.set_xlabel('k')
        ax.set_ylabel('$J_{approx}[k]$')
        ax.set_title(data_dict['filter'])
        fig.suptitle('Energy Function')
        plt.savefig(f'Lab_1/3.4 Energy Function {filter_type}.png', dpi=300)


def plot_energy_function_alpha_0(sim_data: dict[str, dict[str, Any]]) -> None:

    fig, ax = plt.subplots()
    for FL in [16, 32, 64, 128]:
        data_dict: dict[str, Any] = sim_data[f'Q9 {FL}']
        data: dict[str, DataType] = data_dict['data']
        lc = plot_energy_function(data, ax)
        lc[0].set_label(f'Filter Length = {data_dict["FL"]}')
    ax.legend()
    ax.set_xticks(np.arange(data['Probe Data'].shape[0]))
    ax.set_xlabel('k')
    ax.set_ylabel('$J_{approx}[k]$')
    ax.set_title('Root Raised Cosine Pulse $\\;\\;\\;\\;\\alpha = 0$')
    fig.suptitle('Energy Function')
    plt.savefig('Lab_1/Q9 Energy Function alpha 0.png', dpi=300)


def plot_energy_function_noise(sim_data: dict[str, dict[str, Any]]) -> None:
    for filter_type in ['rrc', 'rect', 'rc']:
        fig, ax = plt.subplots()
        elements: list = []
        for i in range(5):
            data_dict: dict[str, Any] = sim_data[f'3.5 {filter_type} {i}']
            elements.append(data_dict['data']['Probe Data'].elements)
        elements = np.array(elements)
        max_factor = elements.max()
        ax.plot(np.arange(elements.shape[1]),
                elements.mean(axis=0)/max_factor, color='blue')
        ax.fill_between(np.arange(elements.shape[1]), elements.min(axis=0)/max_factor,
                        elements.max(axis=0)/max_factor, color='lightblue')
        ax.set_xticks(np.arange(elements.shape[1]))
        ax.set_xlabel('k')
        ax.set_ylabel('$J_{approx}[k]$')
        ax.set_title(f'{data_dict["filter"]}''    $|N|_{dB} = -10dB$')
        fig.suptitle('Energy Function')
        plt.savefig(f'Lab_1/Energy Function Noise {filter_type}.png')


def plot_timing_stats(sim_data: dict[str, dict[str, Any]]) -> None:
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    for filter_type in ['rc', 'rrc', 'rect']:
        if filter_type == 'rect':
            for i in list(range(0, 10, 5))[::-1]:
                data_dict: dict[str, Any] = sim_data[f'3.6 {filter_type} {i}']
                data: dict[str, DataType] = data_dict['data']
                lc = plot_timing_vs_alpha(data, ax)
                lc[0].set_label(
                    f'{data_dict["filter"]}    ''$|N|_{dB}=$'f'{i}dB')
        else:
            for i in list(range(-5, 5, 5))[::-1]:
                data_dict = sim_data[f'3.6 {filter_type} {i}']
                data: dict[str, DataType] = data_dict['data']
                lc = plot_timing_vs_alpha(data, ax)
                lc[0].set_label(
                    f'{data_dict["filter"]}    ''$|N|_{dB}=$'f'{i}dB')
    ax.legend(fontsize='x-small')
    ax.set_xticks(np.arange(0., 1.1, .1))
    ax.set_ylim([1e-7, .2])
    ax.set_xlabel('$\\alpha$')
    ax.set_ylabel('Mean square timing error $\\epsilon$')

    T: float = data['TX Oversample Factor'].data / \
        data['TX Sample Rate'].data*1e6
    tau_d: float = data['TX Channel Model Parameters']['Delay (sec)'].data*1e6
    ax.set_title(f'$T = {T} \\mu s\\;\\;\\;\\;\\tau_d = {tau_d/T:.2f}T$')

    fig.suptitle('Timing Statistics')
    plt.savefig('Lab_1/Timing Statistics vs alpha.png')


def plot_oversample_rx_stats(sim_data: dict[str, dict[str, Any]]) -> None:
    fig, ax = plt.subplots()
    styles = ['-', ':']
    for i, delay_ratio in enumerate([0.35, 0.375]):
        data_dict: dict[str, Any] = sim_data[f'3.7 {delay_ratio}']
        data: dict[str, DataType] = data_dict['data']
        lc = plot_timing_vs_oversample_rx(data, ax)
        lc[0].set_linestyle(styles[i])

        T: float = data['TX Oversample Factor'].data / \
            data['TX Sample Rate'].data*1e6
        tau_d: float = data['TX Channel Model Parameters']['Delay (sec)'].data*1e6
        lc[0].set_label(
            f'$T = {T} \\mu s\\;\\;\\;\\;\\tau_d = {tau_d/T:.3f}T$')

    ax.set_xticks(list(set(np.arange(0, 128, 8)) | set(np.arange(0, 140, 20))))
    ax.tick_params('x', labelsize='xx-small')
    ax.set_xlabel('RX Oversample Factor M')
    ax.set_xlim([0, 120])
    ax.set_ylabel('Mean square timing error $\\epsilon$')
    ax.legend()
    ax.set_yscale('log')
    ax.set_ylim([1e-7, .05])
    fig.suptitle('Timing Statiscs')
    plt.savefig('Lab_1/Timing Statistics vs M.png')


def get_simulation_data() -> dict[str, dict[str, Any]]:

    simulation_data_dict = {
        '3.3 0.0': {'delay_ratio': 0/4,
                    'dirname': '2024-12-17 230713 001'},
        '3.3 0.25': {'delay_ratio': 1/4,
                     'dirname': '2024-12-17 230954 873'},
        '3.3 0.5': {'delay_ratio': 2/4,
                    'dirname': '2024-12-17 231022 157'},
        '3.3 0.75': {'delay_ratio': 3/4,
                     'dirname': '2024-12-17 231118 805'},
        '3.3 1.0': {'delay_ratio': 4/4,
                    'dirname': '2024-12-17 231216 393'},
        '3.4 rrc 0.0': {'alpha': 0., 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175300 505'},
        '3.4 rrc 0.1': {'alpha': 0.1, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175447 935'},
        '3.4 rrc 0.2': {'alpha': 0.2, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175513 104'},
        '3.4 rrc 0.3': {'alpha': 0.3, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175522 243'},
        '3.4 rrc 0.4': {'alpha': 0.4, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175615 719'},
        '3.4 rrc 0.5': {'alpha': 0.5, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175644 398'},
        '3.4 rrc 0.6': {'alpha': 0.6, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175656 637'},
        '3.4 rrc 0.7': {'alpha': 0.7, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175706 689'},
        '3.4 rrc 0.8': {'alpha': 0.8, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175733 834'},
        '3.4 rrc 0.9': {'alpha': 0.9, 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175743 690'},
        '3.4 rrc 1.0': {'alpha': 1., 'filter': 'Root Raised Cosine Pulse',
                        'dirname': '2024-12-17 175755 677'},
        '3.4 rect': {'filter': 'Rectangle Pulse',
                     'dirname': '2024-12-17 175809 564'},
        '3.4 rc 0.0': {'alpha': 0., 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180357 792'},
        '3.4 rc 0.1': {'alpha': 0.1, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180420 400'},
        '3.4 rc 0.2': {'alpha': 0.2, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180434 876'},
        '3.4 rc 0.3': {'alpha': 0.3, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180443 927'},
        '3.4 rc 0.4': {'alpha': 0.4, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180450 724'},
        '3.4 rc 0.5': {'alpha': 0.5, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180507 323'},
        '3.4 rc 0.6': {'alpha': 0.6, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180518 648'},
        '3.4 rc 0.7': {'alpha': 0.7, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180527 365'},
        '3.4 rc 0.8': {'alpha': 0.8, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180547 585'},
        '3.4 rc 0.9': {'alpha': 0.9, 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180555 488'},
        '3.4 rc 1.0': {'alpha': 1., 'filter': 'Raised Cosine Pulse',
                       'dirname': '2024-12-17 180602 953'},
        'Q9 64': {'FL': 64,
                  'dirname': '2024-12-17 175300 505'},
        'Q9 32': {'FL': 32,
                  'dirname': '2024-12-17 180758 221'},
        'Q9 128': {'FL': 128,
                   'dirname': '2024-12-17 180826 220'},
        'Q9 16': {'FL': 16,
                  'dirname': '2024-12-17 180837 269'},
        '3.5 rrc 0': {'filter': 'Root Raised Cosine Pulse',
                      'dirname': '2024-12-17 181139 197'},
        '3.5 rrc 1': {'filter': 'Root Raised Cosine Pulse',
                      'dirname': '2024-12-17 181146 130'},
        '3.5 rrc 2': {'filter': 'Root Raised Cosine Pulse',
                      'dirname': '2024-12-17 181152 694'},
        '3.5 rrc 3': {'filter': 'Root Raised Cosine Pulse',
                      'dirname': '2024-12-17 181159 411'},
        '3.5 rrc 4': {'filter': 'Root Raised Cosine Pulse',
                      'dirname': '2024-12-17 181207 987'},
        '3.5 rc 0': {'filter': 'Raised Cosine Pulse',
                     'dirname': '2024-12-17 181313 812'},
        '3.5 rc 1': {'filter': 'Raised Cosine Pulse',
                     'dirname': '2024-12-17 181421 234'},
        '3.5 rc 2': {'filter': 'Raised Cosine Pulse',
                     'dirname': '2024-12-17 181427 418'},
        '3.5 rc 3': {'filter': 'Raised Cosine Pulse',
                     'dirname': '2024-12-17 181432 219'},
        '3.5 rc 4': {'filter': 'Raised Cosine Pulse',
                     'dirname': '2024-12-17 181438 006'},
        '3.5 rect 0': {'filter': 'Rectangle Pulse',
                       'dirname': '2024-12-17 181452 421'},
        '3.5 rect 1': {'filter': 'Rectangle Pulse',
                       'dirname': '2024-12-17 181502 613'},
        '3.5 rect 2': {'filter': 'Rectangle Pulse',
                       'dirname': '2024-12-17 181508 104'},
        '3.5 rect 3': {'filter': 'Rectangle Pulse',
                       'dirname': '2024-12-17 181515 029'},
        '3.5 rect 4': {'filter': 'Rectangle Pulse',
                       'dirname': '2024-12-17 181520 028'},
        '3.6 rrc -5': {'filter': 'Root Raised Cosine Pulse', 'Noise Power': 0.0,
                       'dirname': '2024-12-17 182209 863'},
        '3.6 rrc 0': {'filter': 'Root Raised Cosine Pulse', 'Noise Power': -5.0,
                      'dirname': '2024-12-18 100936 565'},
        '3.6 rc -5': {'filter': 'Raised Cosine Pulse', 'Noise Power': -5.0,
                      'dirname': '2024-12-17 182801 761'},
        '3.6 rc 0': {'filter': 'Raised Cosine Pulse', 'Noise Power': 0.0,
                     'dirname': '2024-12-17 183351 086'},
        '3.6 rect -5': {'filter': 'Rectangle Pulse', 'Noise Power': -5.0,
                        'dirname': '2024-12-17 183445 331'},
        '3.6 rect 0': {'filter': 'Rectangle Pulse', 'Noise Power': 0.0,
                       'dirname': '2024-12-17 183528 491'},
        '3.6 rect 5': {'filter': 'Rectangle Pulse', 'Noise Power': 5.0,
                       'dirname': '2024-12-17 183610 977'},
        '3.7 0.35': {'delay_ratio': 7/20,
                     'dirname': '2024-12-17 184012 047'},
        '3.7 0.375': {'delay_ratio': 3/8,
                      'dirname': '2024-12-18 104740 750'}
    }

    return simulation_data_dict


def get_names() -> list[str]:

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
        'TX Sample Rate',
        'Probe Data'
    ]

    return names


def main() -> None:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # current directory path + relative path to the directory containing data
    # MODIFY NEXT LINE IF NEEDED
    data_dirname = os.path.abspath(
        current_dir + '/../Labos/Lab 1 - Symbol Timing/Data/') + '\\'
    names: list[str] = get_names()

    global sim_data
    sim_data = get_simulation_data()
    for key, value in sim_data.items():
        value['roots']: dict[str, Root] = get_roots(
            names, data_dirname + value['dirname'])
        value['data']: dict[str, DataType] = get_data(value['roots'])

    plot_sync_err_constellation(sim_data)
    plot_sync_err_eye_diagram(sim_data)
    plot_energy_function_all_pulse_filters(sim_data)
    plot_energy_function_alpha_0(sim_data)
    plot_energy_function_noise(sim_data)
    plot_timing_stats(sim_data)
    plot_oversample_rx_stats(sim_data)


if __name__ == '__main__':
    main()
