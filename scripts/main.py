import yaml
import pprint
import argparse
from pathlib import Path
import numpy as np

from point_utils import DEFAULT_OUT_TXT
from point_utils.utils import get_data_from_txt, save_to_txt, visualize
from point_utils.offsetter import offset_factory

LABLE_B = "B"
LABLE_C = "C"


def main():
    parser = argparse.ArgumentParser(description="Run offset point calculation")
    parser.add_argument(
        "-config", type=str, required=True, help="Path to the YAML configuration file"
    )
    args = parser.parse_args()

    config_path = args.config
    assert Path(config_path).exists(), f"Configuration file not found: {config_path}"
    print(f"Using configuration file: {config_path}")
    with open(config_path, 'r') as fhandle:
        settings = yaml.safe_load(fhandle)
    print(f"Settings:")
    pprint.pprint(settings)

    all_coordinates, labels = get_data_from_txt(settings['input_file'])

    # Calculate offset points for selected points
    offset_calculator = offset_factory('KDTreeOffsets',
                                       all_coordinates=all_coordinates,
                                       labels=labels,
                                       # LABLE_B is used to indicate points to offset.
                                       data_label_to_offset=LABLE_B,
                                       offset_magnitude=settings['offset_magnitude'],
                                       new_data_label=LABLE_C)
    # Set method-specific keyword arguments
    kwargs = {}
    offset_calculator.add_offset_points(**kwargs)

    out_file = Path(settings.get('output_file', DEFAULT_OUT_TXT))
    out_path = out_file.resolve()
    save_to_txt(out_path, offset_calculator.all_coordinates, offset_calculator.labels)
    print(f"Save data to {out_path}")

    if settings.get('visualize', True):
        print(f"Visualizing the data in {out_path}")
        visualize(out_file)


if __name__ == "__main__":
    main()

