from pathlib import Path
import pytest

from point_utils import offset_factory, get_data_from_txt
from point_utils.offsetter import OFFSET_METHOD_TO_CLASS

@pytest.fixture
def data_dir():
    # Return the path to the data directory
    return Path(__file__).parent / "data"

@pytest.mark.parametrize("offset_method", ["KDTreeOffsets"])
def test_offset_factory(data_dir, offset_method):
    inp_file = data_dir / "cdd.txt"
    all_coordinates, labels = get_data_from_txt(inp_file)

    expected_num_new_points = len(labels[labels == "B"])

    settings = {
        "data_label_to_offset": 'B',
        "offset_magnitude": 2.0,
        "new_data_label": 'C',
    }

    # Calculate offset points for selected points
    offset_calculator = offset_factory(offset_method,
                                       all_coordinates=all_coordinates,
                                       labels=labels,
                                       **settings)
    # Set method-specific keyword arguments
    kwargs = {}
    offset_calculator.add_offset_points(**kwargs)

    # Check if the number of new points is as expected
    assert offset_calculator.all_coordinates.shape[0] == len(labels) + expected_num_new_points
    assert offset_calculator.labels.shape[0] == len(labels) + expected_num_new_points