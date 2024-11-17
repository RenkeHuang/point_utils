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
