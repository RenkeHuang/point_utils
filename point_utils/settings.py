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
    data_label_to_offset: float = Field(
        description="Label of the points to offset.")
    new_data_label: float = Field(
        description="Label for the new offset points.")

    # Optional settings
    offset_method: str = Field(
        default="KDTreeOffsets",
        description="Method used for offset calculation.")
    output_file: str = Field(default="output.txt",
                             description="Path to the output text file.")
    visualize: bool = Field(default=False,
                            description="Plot the final output point cloud.")

    @field_validator("input_file")
    def check_input_file(cls, input_file):
        if Path(input_file).suffix != ".txt":
            raise ValueError("Input file must be a text file.")
        return input_file

    @classmethod
    def write_default_config_to_yaml(cls, yaml_path: str):
        """
        Write the default config YAML file.
        """
        with open(yaml_path, "w") as file:
            file.write(cls._get_default_settings_yaml_string())

    @classmethod
    def _get_default_settings_yaml_string(cls):
        """
        Get the default settings to a YAML string.
        """
        schema = cls.schema()
        default_strings = []
        for key, val_dict in schema["properties"].items():
            default_value = val_dict.get("default", ' ')
            default_strings.append(f"{key}: {default_value}")

        return "\n".join(default_strings)


def load_and_validate_config(yaml_path: str) -> ConfigSettings:
    """
    Read the YAML configuration file and validate the settings.
    """
    with open(yaml_path, "r") as file:
        yaml_data = yaml.safe_load(file)

    # Validate and parse using the Pydantic model
    config = ConfigSettings(**yaml_data)
    return config
