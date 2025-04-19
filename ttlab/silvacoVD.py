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