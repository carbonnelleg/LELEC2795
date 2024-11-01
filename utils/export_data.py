# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 19:10:43 2024

@author: carbonnelleg
"""

import xml.etree.ElementTree as ET
import pandas as pd
import struct
import numpy as np
from datetime import datetime, timedelta
import datatypes

# Define namespaces
ns = {
    'lv': 'http://www.ni.com/LabVIEW.VI',
    'pf': 'http://www.ni.com/PlatformFramework',
    'ctrl': 'http://www.ni.com/Controls.LabVIEW.Design'
}


def getroot(filepath: str) -> ET.Element:
    # Load the XML file
    tree = ET.parse(filepath)
    root = tree.getroot()
    return root


root = getroot(
    '../Labos/Lab 1 - Symbol Timing/Data/2024-09-19 134619 420/Q Data (1282).data')

# Extracting relevant DataItems, e.g., waveform data
data_items = []
for item in root.findall('.//lv:DataItem', ns):
    name = item.get('Name')
    data_type = item.get('DataType')
    default_value = item.find('lv:p.DefaultValue', ns)

    if name == 'Timestamp' and default_value is not None:
        timestamp_seconds = int(default_value.text.split(';')[0])
        timestamp = datetime(1, 1, 1) + timedelta(seconds=timestamp_seconds)

        data_items.append({
            'Name': name,
            'DataType': data_type,
            'Timestamp': timestamp.strftime('%d-%m-%Y %H:%M:%S')
        })

    # Only process waveform data
    if name == 'Data' and default_value is not None:
        interval_hex = default_value.find('.//lv:Interval', ns).text
        data_hex = default_value.find('.//lv:Elements', ns).text

        if interval_hex:
            try:
                # Ensure interval_hex contains only valid hexadecimal digits before unpacking
                assert (interval_hex[:2] == '0x')
                time_interval = struct.unpack(
                    '!d', bytes.fromhex(interval_hex[2:]))[0]
            except ValueError:
                print(f"Non-hexadecimal data encountered: '{interval_hex}'")
                time_interval = np.nan

        # Decode hexadecimal data into float values
        if data_hex:
            data_hex = np.array(data_hex.split(','))
            data_values = np.zeros_like(data_hex, dtype=float)
            # 16 hex chars represent one double
            for i, hex_value in enumerate(data_hex):
                try:
                    # Ensure hex_value contains only valid hexadecimal digits before unpacking
                    assert (hex_value[:2] == '0x')
                    data_value = struct.unpack(
                        '!d', bytes.fromhex(hex_value[2:]))[0]
                except ValueError:
                    if hex_value == '0x0':
                        data_value = 0.0
                    else:
                        print(
                            f"Non-hexadecimal data encountered: '{hex_value}'")
                        continue
                finally:
                    data_values[i] = data_value
        else:
            data_values = []

        # Add to list
        data_items.append({
            'Name': name,
            'DataType': data_type,
            'Time Interval': time_interval,
            'DataValues': data_values
        })

# Create DataFrame
df = pd.DataFrame(data_items)

# Optional: Expand data values into separate rows for analysis
df_expanded = df.explode('DataValues').reset_index(drop=True)
print(df_expanded)
