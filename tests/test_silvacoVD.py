#%%
# Imports
from pathlib import Path
import pandas as pd
import shlex as _shlex
import matplotlib.pyplot as plt

from ttlab.silvacoVD import (
    read_victory_log_to_dataframe,
    read_all_logs_in_directory
)

#%%
# Develop structure file reader (cutline)

# Funciton Inputs######
file_path = "/Users/eugenehsu/Documents/Github/TTlab/tests/test_data/silvacoVD/sample.str"
Print = False
cutline = ("x", 0.0)
#######################

mesh_points_by_x = {}
mesh_points_by_y = {}
data_order_meanings_keys = None
with open(file_path, 'r') as file:
    for i, line in enumerate(file):
        if line.startswith("c"):
            values = line.strip().split()
            point_id = int(values[1])
            x = float(values[2])
            y = float(values[3])
            z = float(values[4])
            if x not in mesh_points_by_x:
                mesh_points_by_x[x] = set()
                mesh_points_by_x[x].add(point_id)
            else:
                mesh_points_by_x[x].add(point_id)
            if y not in mesh_points_by_y:
                mesh_points_by_y[y] = set()
                mesh_points_by_y[y].add(point_id)
            else:
                mesh_points_by_y[y].add(point_id)
        if line.startswith("s"):
            data_order_meanings_keys = line.strip().split()[1:]
            start_line = i+1
            break

#%%
x_values = list(mesh_points_by_x.keys())
y_values = list(mesh_points_by_y.keys())
cutline_position = 0.0
cloest_x = min(x_values, key=lambda x: abs(x - cutline_position))
cutline_x = mesh_points_by_x[cloest_x]
#%%

data_by_id = {}
with open(file_path, 'r') as file:
    lines = file.readlines()[start_line:]
    for line in lines:
        if line.startswith("n"):
            values = line.strip().split()
            point_id = int(values[1])
            data_by_id[point_id] = [float(value) for value in values[2:]]
        else:
            break

#%%
# Construct cutline dataframe
datasize = len(data_by_id[0])
temp_datadict = {}
for column_i in range(datasize):
    column_name = data_order_meanings_keys[column_i]
    temp_data = []
    for point_id in cutline_x:
        temp_data.append(data_by_id[point_id][column_i])
    temp_datadict[column_name] = temp_data

cutline_dataframe = pd.DataFrame(temp_datadict)

# Adjust column names to match physical meaning and drop unnecessary columns
with open(file_path, 'r') as file:
    for line in file:
        if not line.startswith("Q "):
            continue
        parts = _shlex.split(line)
        indicator = parts[1]
        column_name = parts[3].strip()
        if indicator in cutline_dataframe.columns:
            cutline_dataframe.rename(columns={indicator: column_name}, inplace=True)
        else:
            if Print:
                print(f"Column {indicator} not found in DataFrame.")
            continue
cutline_dataframe.drop(columns=[col for col in cutline_dataframe.columns if col.isdigit()], inplace=True)

#Function Outputs######
# cutline_dataframe, y_values or x_values (depends on cutline)
#######################

#%%
# Testing

from collections import defaultdict as _defaultdict

cutline = ("x", 1.5)

mesh_by_x = _defaultdict(set)
mesh_by_y = _defaultdict(set)
data_keys = []
data_by_id = {}

with open(file_path, 'r') as f:
    # first pass: collect mesh points and header
    for line in f:
        if line.startswith('c'):
            _, pid, xs, ys, zs = line.split()
            pid, x, y = int(pid), float(xs), float(ys)
            mesh_by_x[x].add(pid)
            mesh_by_y[y].add(pid)
        elif line.startswith('s'):
            data_keys = line.split()[1:]
            break

    # second pass: read node data
    for line in f:
        if not line.startswith('n'):
            break
        parts = line.split()
        pid = int(parts[1])+1
        data_by_id[pid] = list(map(float, parts[2:]))
    
    # third pass: read data (Columns name)
    for line in f:
        if not line.startswith('Q '):
            continue
        parts = _shlex.split(line)
        ind, name = parts[1], parts[3].strip()
        if ind in data_keys:
            data_keys[data_keys.index(ind)] = name

# chose the cutline
if cutline[0] == 'x':
    cut_position = cutline[1]
    closest = min(mesh_by_x, key=lambda xx: abs(xx - cut_position))
    cut_ids = mesh_by_x[closest]
elif cutline[0] == 'y':
    cut_position = cutline[1]
    closest = min(mesh_by_y, key=lambda yy: abs(yy - cut_position))
    cut_ids = mesh_by_y[closest]
else:
    raise ValueError("cutline must be either 'x' or 'y'")

# build DataFrame
cut_dict = {
    key: [data_by_id[pid][i] for pid in cut_ids]
    for i, key in enumerate(data_keys)
}
df = pd.DataFrame(cut_dict)
df = df.loc[:, ~df.columns.str.fullmatch(r'\d+')]

#Returns

#%%
# Test funciton
from collections import defaultdict
import shlex
import pandas as pd
from typing import Tuple

def read_cutline(file_path: str, cutline: Tuple[str, float]) -> pd.DataFrame:
    """
    Parse a Silvaco .str file and return a DataFrame of values along a cutline.
    
    Args:
        file_path: path to the .str file
        cutline: ('x', position) or ('y', position)
    
    Returns:
        DataFrame where rows are mesh nodes closest to the cutline,
        columns are named by the data keys.
    """
    mesh = defaultdict(lambda: {"x": set(), "y": set()})
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
                parts = shlex.split(line)
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
    df = pd.DataFrame(cut_dict)
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