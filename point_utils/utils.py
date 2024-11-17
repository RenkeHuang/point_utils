"""
Utility functions/class for:
    - loading and validating configuration settings.
    - read and write text data.
    - visualize 3D data points with labels.
"""
import numpy as np
import matplotlib.pyplot as plt

DEFAULT_OUT_TXT = "output.txt"

DEFAULT_FIG_NAME = "output.png"
DEFAULT_FIG_TITLE = "3D Point Distribution"


def get_data_from_txt(filename: str) -> tuple[np.ndarray, list[str]]:
    """
    Read data from a text file and return the cartesian coordinates and labels
    as a tuple.
    """
    try:
        data = np.genfromtxt(filename, dtype=None, encoding="utf-8", delimiter=" ")
        data = np.column_stack([data['f0'], data['f1'], data['f2'], data['f3']])
        labels = data[:, 0]
        all_coordinates = data[:, 1:].astype(float)
    except Exception as e:
        raise ValueError(f"Error reading data from file: {e}")

    return all_coordinates, labels


def save_to_txt(filename: str, all_coordinates: np.ndarray, labels: list[str]):
    """
    Save the cartesian coordinates and labels to a text file.
    """
    data = np.column_stack([labels, all_coordinates])
    np.savetxt(filename, data, fmt='%s', delimiter=' ')


def visualize(input_file: str, output_file: str = DEFAULT_FIG_NAME,
              fig_title: str = DEFAULT_FIG_TITLE):
    coordinates, labels = get_data_from_txt(input_file)

    # Map labels to different colors
    unique_labels = np.unique(labels)
    color_map = {label: f'C{i}' for i, label in enumerate(unique_labels)}

    # Create a 3D plot and use add_subplot with projection
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot each point with its corresponding color
    for label, coord in zip(labels, coordinates):
        ax.scatter(coord[0],
                   coord[1],
                   coord[2],
                   c=color_map[label],
                   label=label)

    # Add labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title(fig_title)

    # Show the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.savefig(output_file)
    plt.show()
    print(f'Saved plot to {output_file}.')