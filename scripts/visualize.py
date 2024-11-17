"""
Script to visualize 3D data points with labels for data from a text file, and save the plot to disk.

Usage:
    python visualize.py <input_file> [-o <output_file>]
"""
import argparse
from point_utils.utils import visualize, DEFAULT_FIG_NAME

def parse_args(cmd=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=__doc__)

    parser.add_argument(
        "input_file",
        help=
        "Text file containing the 3D coordinates of points and their labels.")

    parser.add_argument(
        "-o",
        dest="out_file",
        default=DEFAULT_FIG_NAME,
        help=
        f"Filename of the output figure. Default is '{DEFAULT_FIG_NAME}' if not provided"
    )
    return parser.parse_args(cmd)


def main(cmd=None):
    args = parse_args(cmd)
    visualize(args.input_file, args.out_file)


if __name__ == "__main__":
    main()
