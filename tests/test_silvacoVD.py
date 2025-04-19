#%%
# Imports
from pathlib import Path
import pandas as pd

from ttlab.silvacoVD import (
    read_victory_log_to_dataframe,
    read_all_logs_in_directory
)

#%%
# Test reading a folder
test = read_all_logs_in_directory("test_data/silvacoVD")
