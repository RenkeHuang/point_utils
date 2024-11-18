# Point Utils

[![Docker Image Version](https://img.shields.io/docker/v/renkeh/point_utils?sort=semver)](https://hub.docker.com/r/renkeh/point_utils)
[![Docker Pulls](https://img.shields.io/docker/pulls/renkeh/point_utils)](https://hub.docker.com/r/renkeh/point_utils)

**point_utils** is a Python package for computing offset points to a 3-D point cloud.

## Installation
You can install the package directly from the source using **pip**. Clone the repository and run the installation command
```bash
# Clone the repository
git clone https://github.com/RenkeHuang/point_utils.git
cd point_utils

# Install the package
python -m pip install .
```
### Editable Installation (For Development)
If you plan to modify the package, you can install it in editable mode, or use
**Makefile**:
```bash
python -m pip install -e .
```
### Testing
```bash
python -m pip install -r requirements-dev.txt
# Alternatively, use pyproject.toml
python -m pip install .[test]

# Run pytest in the root of repository, with coverage reporting
python -m pytest --cov=point_utils
# Confirm all the test files and functions are found
python -m pytest --collect-only

# Cleanup using Makefile
make clean
```

### Verify Installation
```bash
python -m scripts.main --help
# Alternatively, use the provided script entry point
RUN --help
```

### Example Usage:
```bash
RUN -config examples/config.yaml
```
### Build and Run Docker image
```bash
# Build the Docker image: run in the root directory where the Dockerfile is located
docker build --no-cache -t point_utils:latest .

# Run the Container and persist the output with Docker volume (map examples directory inside the container to the examples directory on local host)
docker run --rm --name point_utils_container -v $(PWD)/examples:/app/examples point_utils:latest

# If starting the Container with an interactive shell, manually execute the entry script in the shell
# -i: keep STDIN open, -t: allocate a pseudo-TTY for the shell session.
# /bin/bash: open a bash shell inside the container.
docker run --rm -it --name point_utils_container point_utils:latest /bin/bash
RUN -config examples/config.yaml

# Override the default CMD:
# The following command generates a plot for the data, and copy back to local host
docker run --rm -v $(PWD)/examples:/app/examples point_utils:latest python scripts/visualize.py examples/cdd.txt -o examples/fig.png
```


## Background

