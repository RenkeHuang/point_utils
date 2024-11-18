import yaml
import pprint
import argparse
from pathlib import Path

from point_utils import DEFAULT_OUT_TXT
from point_utils import ConfigSettings
from point_utils.utils import get_data_from_txt, save_to_txt, visualize
from point_utils.offsetter import offset_factory


def _parse_args():
    """
    Define command-line interface
    """
    parser = argparse.ArgumentParser(
        description="Run offset points calculation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-config",
                       type=str,
                       help="Path to the YAML configuration file")
    group.add_argument('-write-default-config',
                       type=str,
                       help="Write the default configuration file")
    return parser.parse_args()


def run(config_path: str):
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load settings from the configuration file
    print(f"Using configuration file: {config_path}")
    with open(config_path, 'r') as fhandle:
        settings = yaml.safe_load(fhandle)
    print(f"Settings:")
    pprint.pprint(settings)

    all_coordinates, labels = get_data_from_txt(settings['input_file'])

    # Setup the offset calculator based on settings
    offset_calculator = offset_factory(
        offset_method=settings['offset_method'],
        all_coordinates=all_coordinates,
        labels=labels,
        data_label_to_offset=settings['data_label_to_offset'],
        offset_magnitude=settings['offset_magnitude'],
        new_data_label=settings['new_data_label'])

    # Set method-specific keyword arguments (if any)
    kwargs = {}

    # Calculate offset points for selected points
    offset_calculator.add_offset_points(**kwargs)

    out_file = Path(settings.get('output_file', DEFAULT_OUT_TXT))
    out_path = out_file.resolve()
    save_to_txt(out_path, offset_calculator.all_coordinates,
                offset_calculator.labels)
    print(f"Save data to {out_path}.")

    if settings.get('visualize', True):
        print("Visualizing the data.")
        visualize(out_file, output_file=out_file.with_suffix(".png"))


def main():
    args = _parse_args()
    if args.write_default_config:
        ConfigSettings.write_default_config_to_yaml(args.write_default_config)
        return

    run(args.config)


if __name__ == "__main__":
    main()
