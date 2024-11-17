"""
Schema for the configuration settings, function to load and validate the settings.
"""
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

class ConfigSettings(BaseModel):
    """
    Schema for the configuration settings.
    """
    # Required settings
    input_file: str = Field(description="Path to the input text file.")
    offset_magnitude: float = Field(description="Magnitude of the offset.")

    # Optional settings
    offset_method: str = Field(
        default="KDTreeOffsets", description="Method used for offset calculation.")
    output_file: str = Field(
        default="output.txt", description="Path to the output text file.")
    visualize: bool = Field(
        default=False, description="Plot the final output point cloud.")

    @field_validator("input_file")
    def check_input_file(cls, input_file):
        if Path(input_file).suffix != ".txt":
            raise ValueError("Input file must be a text file.")
        return input_file


def load_and_validate_config(yaml_file_path: str) -> ConfigSettings:
    """
    Read the YAML configuration file and validate the settings.
    """
    with open(yaml_file_path, "r") as file:
        yaml_data = yaml.safe_load(file)

    # Validate and parse using the Pydantic model
    config = ConfigSettings(**yaml_data)
    return config
