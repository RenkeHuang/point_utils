#!/bin/bash

# Exit script on any error
set -e

# Clone the repository
if [ ! -d "point_utils" ]; then
  git clone https://github.com/RenkeHuang/point_utils.git
fi

# Navigate to the repository directory
cd point_utils

# Install the package
pip install .