# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 09:36:42 2025

@author: eugenehsu
"""

#ECC 133 Support library

import numpy as _np
import pandas as _pd
import csv as _csv
import re as _re
from pathlib import Path as _Path

def check_type(fpath):
    setuptitle = None
    with open(fpath, mode="r") as file:
        reader = _csv.reader(file, delimiter=",")
        for row in reader:
            if row[0].strip() == "PrimitiveTest":
                setuptitle = row[1].strip()
                break
    if setuptitle is None:
        print("Error: 'PrimitiveTest' not found in the file.")
    return setuptitle

def find_var2(fpath):
    with open(fpath, mode="r") as file:
        for line in file.read().splitlines():
            if line.startswith("AnalysisSetup, Analysis.Setup.Vector.Graph.SetupInfo"):
                var2_name = _re.split(r'[\t,]', line)[2]         # Extract the name part
                var2_values = line.split("\t")[1].split(",")     # Extract and split values by commas
                return var2_name.strip(), var2_values
    print("Second Variable Not found!")
    return None, None  # If line not found

def find_freq(fpath):
    with open(fpath, mode="r") as file:
        for line in file.read().splitlines():
            if line.startswith("TestParameter, Measurement.Secondary.Frequency"):
                freqs = line.split(",")[2:]
                freqs = [int(freq) for freq in freqs]
                return freqs
    return None

def find_start_line(filename, keyword="DataValue"):
    cut = None
    with open(filename, 'r') as file:
        for i, line in enumerate(file):
            if line.startswith("Dimension1"):
                cut = line.split(",")[1]
            if keyword in line:
                return i-1, int(cut)
    print(f"No Data -- {filename}")
    return None, None

def read_ECC133_csv(fpath):
    measure_type = check_type(fpath)
    fname = _Path(fpath).stem

    match measure_type:
        case "Id-Vd sweep":
            start_index, cut = find_start_line(fpath)
            df = _pd.read_csv(fpath, skiprows=start_index)
            df.columns = df.columns.str.strip()
            var2_name, var2_val = find_var2(fpath)
            df[var2_name] = _np.repeat(var2_val, cut)
        case "C-V Sweep":
            start_index, cut = find_start_line(fpath)
            df = _pd.read_csv(fpath, skiprows=start_index)
            df.columns = df.columns.str.strip()
            if "Freq" not in df.columns.values:
                freq = find_freq(fpath)
                df["Freq"] = _np.repeat(freq, cut)
        case "2 term IV":
            start_index, cut = find_start_line(fpath)
            df = _pd.read_csv(fpath, skiprows=start_index)
            df = df.apply(lambda x: _pd.to_numeric(x, errors='coerce'))
            df.columns = df.columns.str.strip()
        case "I/V Sweep":
            start_index, cut = find_start_line(fpath)
            df = _pd.read_csv(fpath, skiprows=start_index)
            df = df.apply(lambda x: _pd.to_numeric(x, errors='coerce'))
            df.columns = df.columns.str.strip()
        case "Id-Vg sweep":
            start_index, cut = find_start_line(fpath)
            df = _pd.read_csv(fpath, skiprows=start_index)
            df.columns = df.columns.str.strip()
            var2_name, var2_val = find_var2(fpath)
            df[var2_name] = _np.repeat(var2_val, cut)
        case _:
            print(f"{fname}\tUnknown measure type")
            df = None
    return df

# Custom sorting function
def extract_key(fpath):
    # Split into prefix and numeric part
    filename = _Path(fpath).stem
    parts = filename.split('-')
    prefix = parts[0]  # Extract the prefix (e.g., "C1R8G10_transfer")
    
    # Extract numeric part if it exists, otherwise assign -1 for no number
    number_part = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else -1
    return (prefix, number_part)


# Custom sorting function
def ECC_sort_extract_key(fpath):
    # Split into prefix and numeric part
    filename = _Path(fpath).stem
    parts = filename.split('-')
    prefix = parts[0]  # Extract the prefix (e.g., "C1R8G10_transfer")
    
    # Extract numeric part if it exists, otherwise assign -1 for no number
    number_part = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else -1
    return (prefix, number_part)


def average_forward_backward(df):
    """
    Averages forward and backward IV data from a DataFrame, ignoring non-numeric columns.
    Assumes data length is double (forward + backward).
    
    Parameters:
        df (pd.DataFrame): Input DataFrame with IV data.
    
    Returns:
        pd.DataFrame: DataFrame of averaged numeric data.
    """
    numeric_df = df.select_dtypes(include='number')  # Keep only numeric columns
    half_length = len(numeric_df) // 2
    averaged_df = (numeric_df.iloc[:half_length].reset_index(drop=True) +
                   numeric_df.iloc[half_length:][::-1].reset_index(drop=True)) / 2
    return averaged_df