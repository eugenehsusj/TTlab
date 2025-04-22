# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 09:36:42 2025

@author: eugenehsu
"""

#Silvaco Victory output Support library

from pathlib import Path as _Path
import pandas as _pd
import re as _re
import os as _os
import shlex as _shlex
from typing import Tuple as _Tuple
from collections import defaultdict as _defaultdict

# Function that reads Silvaco Log
def read_victory_log_to_dataframe(file_path):
    data = []
    column_map = {}
    columns = []
    
    with open(file_path, 'r') as file:
        for line in file:
            # Extract the columns from 'p' line
            if line.startswith('p'):
                columns = line.split()[2:]
            
            # Extract the column names from 'Q' lines and map them
            if line.startswith('Q'):
                parts = line.split()
                col_index = parts[1]
                col_name = ' '.join(parts[3:]).strip('"')
                if col_index in columns:
                    column_map[col_index] = col_name
            
            # Extract the data from 'd' lines
            if line.startswith('d'):
                values = line.split()[1:]
                data.append([float(num) for num in values])
    
    # Map the columns using the column map
    column_names = [column_map.get(col, f"Column_{col}") for col in columns]

    # Create DataFrame with the mapped column names
    df = _pd.DataFrame(data, columns=column_names)
    
    return df

def read_all_logs_in_directory(directory):
    all_data = []  # List to store DataFrames from all log files
    log_dir = _Path(directory)
    skip_hidden = False
    
    pattern = r"_([a-zA-Z]+)([\d.eE+-]+)"
    # Iterate through all .log files in the directory
    for log_file in log_dir.glob("*.log"):
        if log_file.name.startswith("."):
            skip_hidden = True
            continue
        # Extract metadata from the file name
        try:
            df = read_victory_log_to_dataframe(log_file)
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
            continue
        filename = log_file.stem
        simulation_name = filename.split("_")[0]
        df["name"] = simulation_name
        matches = _re.findall(pattern, log_file.stem)
        if matches:
            for key, value in matches:
                df[key] = value
        all_data.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    final_df = _pd.concat(all_data, ignore_index=True)
    if skip_hidden:
        print("Skip hidden .log files")
    return final_df

def read_str_cutline(file_path: str, cutline: _Tuple[str, float]) -> _pd.DataFrame:
    """
    Parse a Silvaco .str file and return a DataFrame of values along a cutline.
    
    Args:
        file_path: path to the .str file
        cutline: ('x', position) or ('y', position)
    
    Returns:
        DataFrame where rows are mesh nodes closest to the cutline,
        columns are named by the data keys.
    """
    mesh = _defaultdict(lambda: {"x": set(), "y": set()})
    data_keys = []
    data_by_id = {}
    id_to_x = {}
    id_to_y = {}

    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('c '):
                _, pid, xs, ys, _ = line.split()
                pid = int(pid)
                x, y = float(xs), float(ys)
                id_to_x[pid] = x
                id_to_y[pid] = y
                mesh[x]['x'].add(pid)
                mesh[y]['y'].add(pid)

            elif line.startswith('s '):
                data_keys = line.split()[1:]

            elif line.startswith('n '):
                parts = line.split()
                pid = int(parts[1])+1
                data_by_id[pid] = list(map(float, parts[2:]))

            elif line.startswith('Q '):
                parts = _shlex.split(line)
                ind, name = parts[1], parts[3]
                for idx, key in enumerate(data_keys):
                    if key == ind:
                        data_keys[idx] = name

    if not data_keys:
        raise ValueError("No data header ('s') found in file.")
    if not data_by_id:
        raise ValueError("No node data ('n') found in file.")

    axis, pos = cutline
    if axis not in ('x', 'y'):
        raise ValueError("cutline axis must be 'x' or 'y'")

    # find all coords along the chosen axis
    coords = [k for k, v in mesh.items() if v[axis]]
    # pick the one closest to pos
    closest = min(coords, key=lambda c: abs(c - pos))
    cut_ids = sorted(mesh[closest][axis])

    # build DataFrame
    cut_dict = {
        key: [data_by_id[pid][i] for pid in cut_ids]
        for i, key in enumerate(data_keys)
    }
    df = _pd.DataFrame(cut_dict)
    # drop purely numeric columns
    df = df.drop(df.filter(regex=r'^\d+$').columns, axis=1)
    # Build perpendicular coords
    if axis == 'x':
        df['y'] = [id_to_y[pid] for pid in cut_ids]
        df.sort_values(by='y', inplace=True)
        df.reset_index(drop=True, inplace=True)
    else:
        df['x'] = [id_to_x[pid] for pid in cut_ids]
        df.sort_values(by='x', inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df