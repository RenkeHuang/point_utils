import os
import sys
import yaml
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from point_utils import ConfigSettings, load_and_validate_config


def test_imported():
    """Test if the package can be imported."""
    assert "point_utils" in sys.modules


@pytest.fixture(autouse=True)
def tmp_cwd():
    """
    Change to a temporary directory for the duration of the test
    """
    old_cwd = os.getcwd()
    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)
    yield
    os.chdir(old_cwd)


def test_config_missing_required_setting():
    with pytest.raises(
            ValidationError,
            match="4 validation errors for ConfigSettings") as exc_info:
        config = ConfigSettings()
    assert "input_file" in str(exc_info.value)
    assert "offset_magnitude" in str(exc_info.value)


def test_config_invalid_input_ext(tmp_cwd):
    setting = {
        "input_file": "data.json",
        "offset_magnitude": 2.0,
        "data_label_to_offset": "B",
        "new_data_label": "C",
    }
    Path("config.yaml").write_text(yaml.dump(setting))
    with pytest.raises(ValidationError,
                       match="Value error, Input file must be a text file."):
        config = load_and_validate_config("config.yaml")
