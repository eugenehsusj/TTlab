import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from tqdm import tqdm
import os
import matplotlib as mpl

def animate_plot(df, x_col, y_col, group_col='fname', output_file='animation.mp4',
                 x_label=None, y_label=None, title=None, 
                 xlim=None, ylim=None, figsize=(12,6), 
                 frame_skip=20, fps=20, legend_title="Files"):
    """
    Creates an animated plot from a DataFrame and saves it as an .mp4 video file.

    Parameters:
    - df: pandas DataFrame containing the data.
    - x_col: name of the column to use for x-axis.
    - y_col: name of the column to use for y-axis.
    - group_col: name of the column to group the data (default 'fname').
    - output_file: filename for the output animation (default 'animation.mp4').
    - x_label: label for the x-axis.
    - y_label: label for the y-axis.
    - title: title of the plot.
    - xlim: tuple specifying x-axis limits.
    - ylim: tuple specifying y-axis limits.
    - figsize: tuple specifying figure size (width, height).
    - frame_skip: number of frames to skip in animation.
    - fps: frames per second for the animation.
    - legend_title: title for the legend.
    """
    mpl.rcParams['animation.ffmpeg_path']
    # Precompute x and y data for each group
    unique_group_names = df[group_col].unique()
    group_to_xy = {}
    group_lengths = []
    for group_name in unique_group_names:
        group = df[df[group_col] == group_name]
        x = group[x_col].values
        y = group[y_col].values
        group_to_xy[group_name] = (x, y)
        group_lengths.append((group_name, len(group)))

    cum_lengths = np.cumsum([length for group_name, length in group_lengths])

    # Initialize figure
    fig, ax = plt.subplots(figsize=figsize)

    # Adjust the subplot to make room on the right side for the legend
    plt.subplots_adjust(right=0.75)

    # Customize the plot
    plt.rcParams.update({'font.size': 20})
    if x_label:
        ax.set_xlabel(x_label, fontsize=12)
    else:
        ax.set_xlabel(x_col, fontsize=12)
    if y_label:
        ax.set_ylabel(y_label, fontsize=12)
    else:
        ax.set_ylabel(y_col, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)
    ax.grid(alpha=0.5)
    if xlim:
        ax.set_xlim(xlim)
    else:
        ax.set_xlim(df[x_col].min(), df[x_col].max())
    if ylim:
        ax.set_ylim(ylim)
    else:
        ax.set_ylim(df[y_col].min(), df[y_col].max())

    # Initialize lines for each group
    lines = []
    num_data = len(group_lengths)
    for _ in range(num_data):
        line, = ax.plot([], [], lw=2)
        lines.append(line)

    labels = np.array([group_name for group_name, _ in group_lengths])

    # Initialization function
    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    # Function to get group_name and index from frame
    def get_group_and_index(frame):
        group_index = np.searchsorted(cum_lengths, frame, side='right')
        group_name, length = group_lengths[group_index]
        frame_start = 0 if group_index == 0 else cum_lengths[group_index - 1]
        index_within_group = frame - frame_start
        return group_index, group_name, index_within_group

    # Update function for animation
    def update(frame):
        group_index, now_group, index_within_group = get_group_and_index(frame)
        
        # Draw previous lines fully
        for i in range(group_index):
            group_name = group_lengths[i][0]
            x, y = group_to_xy[group_name]
            lines[i].set_data(x, y)
        
        # Draw current line progressively
        x, y = group_to_xy[now_group]
        lines[group_index].set_data(x[:index_within_group + 1], y[:index_within_group + 1])
        
        # Clear future lines
        for i in range(group_index + 1, num_data):
            lines[i].set_data([], [])
        
        # Update the legend outside the plot area
        visible_labels = labels[:group_index + 1]
        ax.legend(lines[:group_index + 1], visible_labels, loc='center left', bbox_to_anchor=(1, 0.5),
                  fontsize=10, title=legend_title)
        return lines

    # Prepare frames
    total_frames = len(df)
    frames = list(range(0, total_frames, frame_skip))

    # Create the animation using FuncAnimation
    ani = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True)

    # Use FFMpegWriter to save the animation as an .mp4 file
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=1800)

    # Save the animation
    ani.save(output_file, writer=writer)
    plt.close(fig)