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
# or
make install
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

### Build Docker image
```bash
# Run in the root directory where the Dockerfile is located
docker build --no-cache -t point_utils:latest .
```
**Pull the latest image from the dockerhub**:
```bash
docker pull renkeh/point_utils:0.1.1
```

### Run Docker image
Check out the DockerHub [repository overview page](https://hub.docker.com/repository/docker/renkeh/point_utils/general) for more details.
```bash
# Run the Container and persist the output with Docker volume (map examples directory inside the container to the examples directory on local host)
docker run --rm --name point_utils_container -v $(PWD)/examples:/app/examples point_utils:0.1.1

# If starting the Container with an interactive shell, manually execute the entry script in the shell
# -i: keep STDIN open, -t: allocate a pseudo-TTY for the shell session.
# /bin/bash: open a bash shell inside the container.
docker run --rm -it --name point_utils_container point_utils:0.1.1 /bin/bash
RUN -config examples/config.yaml

# Override the default CMD:
# The following command generates a plot for the data, and copy back to local host
docker run --rm -v $(PWD)/examples:/app/examples point_utils:0.1.1 python scripts/visualize.py examples/cdd.txt -o examples/fig.png
```

## Testing
```bash
python -m pip install -r requirements-dev.txt
# Alternatively, use pyproject.toml
python -m pip install .[test]

# Run pytest in the root of repository, with coverage reporting
python -m pytest --cov=point_utils
# Confirm all the test files and functions are found
python -m pytest --collect-only

# Cleanup using Makefile, useful during development
make clean
```

## Background
The primary functionality of this package is implemented in the [offsetter](https://github.com/RenkeHuang/point_utils/blob/main/point_utils/offsetter.py) module.
Its main objective is to augment a three-dimensional point cloud dataset by adding offset points corresponding to a selected subset of existing points.

For example, suppose we select a subset of points labeled "B" (this selection can be performed using data processing techniques such as SQL queries and tagging).
Each "B" point will have an associated offset point, which we will label "C" later.
The "C" points are positioned at a fixed distance $D$ from their corresponding "B" points, maintaining a one-to-one correspondence in the current implementation (this can be easily extended to more general cases).
The offset vectors have a constant magnitude $D$, and their directions are oriented to point away from the existing point cloud as much as possible.
This method effectively expands the dataset in a controlled manner, preventing the oversaturation of existing regions.

> **Note**: The task described above is analogous to and serves as a simplified abstraction of the challenges encountered in generative machine learning models and chemoinformatics, particularly in exploring chemical space and enumerating molecular libraries.
In these fields, generating new data points (e.g., molecular structures) that are meaningful and diverse, while avoiding overcrowding existing data regions, is a common objective.
For example, in chemoinformatics, scientists often seek to generate new molecular structures by adding atoms or functional groups to existing molecules. This process must consider spatial configurations to prevent unfavorable interactions, such as atomic clashes when two atoms are positioned within their van der Waals radii, and to ensure that the new structures are chemically valid.

Several numerical methods can be used to determine directions of these offset vectors.
While all methods implemented are tecnically functioning out-of-the-box, **the "optimality" of
the computed offset vectors are impacted by the specific dataset, method-dependent parameters, etc,
so further scientific validations are required to check this**.
Here we give a brief overview of these methods:

#### Local Information Methods
Methods focus on local data characteristics, and rely on the immediate surroundings of the target point to determine the direction of the offset vectors.

- **Nearest-Neighbor via K-D Tree**: Calculate the average displacement vectors from each "B" point to its nearest neighbors and use the opposite direction of this mean vector as the direction of the offset vector for the "B" point.

- **Surface Normals via Local Surface Fitting**: Fit a local surface around each "B" point using techniques such as least squares fitting. Compute the surface normal from this fitted surface and use it as the direction for the offset vector.

- **Density Gradient**: Use Kernel Density Estimation (KDE) to model the density of points around each B point. Compute the gradient of the density function to identify the direction of decreasing density, and use this direction for the offset vector.


####  Global Information Methods
Methods consider the global structure or properties of the entire dataset.
- **Surface Normals via Convex Hull Method**: Construct a Convex Hull for the entire point cloud to determine the global geometric boundaries. Compute the normals of the convex hull to define the direction of the offset vectors.

- **Radial Expansion**: Calculate the centroid of the entire point cloud. For each B point, computes the vector pointing from the centroid to the point and uses this direction for the offset vector.

- **Principal Component Analysis (PCA)**: Perform PCA on the entire point cloud to identify the principal directions of variance. For each B point, the direction corresponding to the smallest eigenvalue (least variance) can be considered as pointing “away” from the densest part of the data.

- **Voronoi Diagram**:  Construct a 3D Voronoi diagram of the entire point cloud. For each "B" point, identify its Voronoi cell and determine the direction towards its farthest vertex, which likely points away from neighboring points.

#### Currently the following three methods are supported:
- Nearest-Neighbor via K-D Tree, implemented in **[KDTreeOffsets](https://github.com/RenkeHuang/point_utils/blob/c5e63ef8e1f9814d2f763a5323391dddd09fdba2/point_utils/offsetter.py#L98-L99) class**
- Convex Hull, implemented in **[ConvexHullOffsets](https://github.com/RenkeHuang/point_utils/blob/c5e63ef8e1f9814d2f763a5323391dddd09fdba2/point_utils/offsetter.py#L153-L154) class**
- Radial Expansion, implemented in **[CentroidOffsets](https://github.com/RenkeHuang/point_utils/blob/c5e63ef8e1f9814d2f763a5323391dddd09fdba2/point_utils/offsetter.py#L201-L202) class**

## Version Log
**Version 0.1.1**
- Support two new methods, convex hull and radial expansion for offset vector computations

**Version 0.1.0**
- Support KDTree for offset vector computations
