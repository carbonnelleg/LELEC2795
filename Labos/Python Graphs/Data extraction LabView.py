# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 15:34:20 2024

@author: gauti
"""

import pandas as pd
import numpy as np
import re
import csv

import re
import csv

def extract_data_from_raw(input_file):
    """Extract the constellation data from the raw file."""
    with open(input_file, 'r') as file:
        raw_data = file.read()

    # Regular expression to find elements between curly braces { }
    pattern = re.compile(r'\{([^}]*)\}')
    matches = pattern.findall(raw_data)

    if not matches:
        raise ValueError("No data found in the provided file format.")

    # Split the elements inside the braces by commas and convert to float
    data = np.array([map(float, item.split(',')) for item in matches])
    return data

def save_to_csv(output_file, data):
    """Save extracted data to CSV."""
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(["Element 1", "Element 2"])
        
        # Write data rows
        for row in zip(*data):  # Transpose data to have (Element 1, Element 2) format
            writer.writerow(row)

def transform_file(input_file, output_file):
    """Extracts data from the input file and saves it as CSV in output_file."""
    try:
        data = extract_data_from_raw(input_file)
        save_to_csv(output_file, data)
        print(f"Data successfully written to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
input_file = 'Data/Received Constellation.csv'  # Replace with your input file path
output_file = 'Data/transformed_data.csv'  # Replace with your desired output file path
transform_file(input_file, output_file)
