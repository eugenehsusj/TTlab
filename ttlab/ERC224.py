#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 09:36:42 2024

@author: eugenehsu
"""

import numpy as _np
import pandas as _pd
import os as _os
import matplotlib.pyplot as _plt

def read_mdm(filename):
    data = []
    headers = []
    start_reading = False
    with open(filename, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line == 'BEGIN_DB':
                # Begin looking for the data header marker '#'
                continue
            if stripped_line == "END_DB":
                # Stop reading
                break
            if stripped_line.startswith('#'):
                # Start recording data after this line
                headers = stripped_line[1:].split()
                start_reading = True
                continue
            if start_reading:
                parts = line.split()
                # Convert strings to appropriate types (float)
                float_parts = [float(x) for x in parts]
                data.append(float_parts)

    # Convert list to Numpy array
    return _pd.DataFrame(data, columns=headers)

def load_mdm_from_folder(folder_path):
    mdm_files = []
    data = {}

    for filename in _os.listdir(folder_path):
        if filename.endswith(".mdm"):
            full_path = _os.path.join(folder_path, filename)
            base_name = filename.split(".")[0]
            data[base_name] = read_mdm(full_path)
    return data



def plot_selected_data(data_dict, selected_keys, x_axis, y_axis,legend=None, Abs=False, xscal=1, yscal=1):
    # Plot only the selected datasets
    # Input dictionary,select keys, and xy axis DataFrame column name
    """
    selected_keys needs to be [list]
    x_axis, y_axis is DataFrame column name
    """
    fig, ax = _plt.subplots(figsize=(8, 5))
    valid_legend = []
    counter = 0
    for key in selected_keys:
        if key in data_dict:
            df = data_dict[key]
            # Check if the x_axis and y_axis are valid
            if x_axis not in df.columns or y_axis not in df.columns:
                print(f"Columns {x_axis} or {y_axis} not found in DataFrame associated with {key}.")
                continue  # Skip this key and move to the next
            if Abs:
                ax.plot(abs(df[x_axis])*xscal, abs(df[y_axis])*yscal, label=key)
            else:
                ax.plot(df[x_axis]*xscal, df[y_axis]*yscal, label=key)
            if legend != None:
                valid_legend.append(legend[counter])
        else:
            print(f"Key {key} not found in the dictionary.")
        counter+=1

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(f"Plot of {y_axis} vs {x_axis}")
    if legend==None:
        ax.legend()
    else:
        ax.legend(valid_legend)
    ax.grid(True)
    return fig, ax

def read_mdm_multiple(filename, var):
    #Input var is sweep order 2 variable - which is the word after ICCAP_VAR
    """
    Read .mdm file that may contain multiple sections with different Vgate values.
    Each section starts with 'BEGIN_DB' and ends with 'END_DB'.
    The function returns a dictionary with keys as Vgate values and values as DataFrames.
    """
    data_dict = {}
    current_vgate = None
    data = []
    headers = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('ICCAP_VAR '+ var):
                # Extract the Vgate value and use it as a key for the dictionary
                current_vgate = float(line.split()[-1])
                data = []  # Reset the data list for the new section
            elif line.startswith('#'):
                # Extract headers from this line
                headers = line[1:].split()
            elif line.startswith('BEGIN_DB') or line.startswith('END_HEADER'):
                # Ignore these lines, but indicate that we're in a data section
                continue
            elif line.startswith('END_DB'):
                # End of data block, convert to DataFrame and store in the dictionary
                if current_vgate is not None and data:
                    data_dict[current_vgate] = _pd.DataFrame(data, columns=headers)
            else:
                # Collect data if we are within a data block
                if line and current_vgate is not None:
                    if line.startswith("ICCAP"):
                        continue
                    parts = line.split()
                    data.append([float(p) for p in parts])

    return data_dict


def mdm2df(fpath):
    """
    Converts MDM formatted data to a pandas DataFrame.

    Parameters:
    fpath (str): The file path of the MDM file to be parsed.

    Returns:
    pandas.DataFrame: A DataFrame containing the structured data from the MDM file.
    """
    mode = None
    with open(fpath, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("BEGIN_HEADER"):
                Columns = []
                mode = "Header"
                continue
            elif line.startswith("END_HEADER"):
                data = _pd.DataFrame(columns=Columns)
                mode = None
                continue
            elif line.startswith("BEGIN_DB"):
                mode = "DB"
                ICCAP_var = []
                continue
            elif line.startswith("END_DB"):
                mode = None
                continue
            elif line.startswith("#"):
                ICCAP_var = _pd.DataFrame(ICCAP_var)
                ICCAP_var_columns = ICCAP_var.iloc[:, 0].values
                ICCAP_var_values = ICCAP_var.iloc[:, 1].values
                ICCAP_var = _pd.DataFrame([ICCAP_var_values], columns=ICCAP_var_columns)

                data_column_name = line[1:].split()
                mode = "Data"
                continue

            match mode:
                case "Header":
                    if "ICCAP" in line:
                        continue
                    Columns.append(line.split()[0])
                case "DB":
                    if line.startswith("ICCAP_VAR"):
                        ICCAP_var.append(line.split()[-2:])
                        continue
                case "Data":
                    temp = _pd.DataFrame([line.split()], columns=data_column_name)
                    for c_name in ICCAP_var_columns:
                        temp[c_name] = ICCAP_var[c_name]
                    data = _pd.concat([data, temp], ignore_index=True)
    return data