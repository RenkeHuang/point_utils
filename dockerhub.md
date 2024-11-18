# point_utils

**point_utils** is a Python package for computing offset points to a 3-D point cloud.
The project is under active development and is hosted on [GitHub](https://github.com/RenkeHuang/point_utils).


## Usage
**IMPORTANT**: Before running the Docker container, ensure that you clone or copy the contents of [examples](https://github.com/RenkeHuang/point_utils/tree/main/examples) directory from the GitHub repository into your current working directory. This step is necessary to allow the entry script to execute properly when mounting volumes (`-v` option) and ensure that the output file can be written back to your host system.

**Note**: This requirement arises from the current configuration of the entry script, which relies on the files being accessible in the host's working directory. We plan to improve this setup in the future for greater flexibility and ease of use.

To run the point_utils container and retrieve the result, use the following Docker command:
```bash
docker run --rm --name point_utils_container -v $(PWD)/examples:/app/examples renkeh/point_utils:0.1.1
```
This command runs the container and saves the output file to the `examples` directory
on your local machine.
The Docker volume maps `examples` directory inside the container to the `examples`
directory on your local host.s

Alternatively, you can start the container with an interactive shell, and manually
execute the entry script in the shell:
```bash
docker run --rm -it --name point_utils_container point_utils:0.1.1 /bin/bash
RUN -config examples/config.yaml
```

You can also override the default CMD to run other scripts. For example:
```
docker run --rm -v $(PWD)/examples:/app/examples point_utils:0.1.1 python scripts/visualize.py examples/cdd.txt -o examples/fig.png
```
This command generates a plot from the specified data file (`examples/cdd.txt`) and saves the output (`examples/fig.png`) back to the `examples` directory on your local host.


## Docker Image
The Docker image is built using the following Dockerfile ([link](https://github.com/RenkeHuang/point_utils/blob/main/Dockerfile)):
```dockerfile
# Use an official Python image as the base
FROM python:3.9-slim

# Set environment variables
# Prevents the generation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is flushed immediately.
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy only files needed for installation to leverage Docker caching
COPY pyproject.toml README.md ./
COPY point_utils ./point_utils
COPY scripts ./scripts
COPY examples/cdd.txt     ./examples/cdd.txt
COPY examples/config.yaml ./examples/config.yaml

# Install pipenv and build dependencies
RUN pip install --no-cache-dir setuptools wheel

# Install the package in editable mode
RUN pip install -e .

# Default command (can be overridden in `docker run`)
CMD ["python", "scripts/main.py", "-config", "examples/config.yaml"]
```
## Version Log
**Version 0.1.1**
- Support two new methods, convex hull and radial expansion for offset vector computations

**Version 0.1.0**
- Support KDTree for offset vector computations

## License
This project is licensed under the MIT License.
