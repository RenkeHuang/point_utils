"""
Module for calculating offset vectors for points in a point cloud using different methods.
"""

from abc import ABC, abstractmethod
import numpy as np
from scipy.spatial import KDTree
from scipy.spatial import ConvexHull

__all__ = ['offset_factory']


class OffsetsInterface(ABC):
    """
    Abstract class for adding offset points at a fixed magnitude for selected
    points in a point cloud.

    :ivar all_coordinates: Numpy array of shape (N, 3) representing cartesian
                           coordinates of all points.
    :ivar labels: List of labels for all points.
    :ivar data_label_to_offset: Label of the points to offset, these points are
                                used to calculate offset directions.
    :ivar point_indices: List of indices into the point cloud for which to calculate
                         offset directions.
    :ivar offset_magnitude: Fixed magnitude of all offset vectors.
    :ivar new_data_label: Label for the new offset points.
    """

    def __init__(self,
                 all_coordinates: np.ndarray,
                 labels: list[str],
                 data_label_to_offset: str,
                 offset_magnitude: float,
                 new_data_label: str):
        self.all_coordinates = all_coordinates
        self.labels = np.array(labels)
        self.offset_magnitude = offset_magnitude
        self.new_data_label = new_data_label

        # Collect indices of the points to offset
        self.point_indices = np.where(self.labels == data_label_to_offset)[0]

    @abstractmethod
    def get_offset_vecs(self, **kwargs) -> np.ndarray:
        """
        All subclasses must implement this method. It should calculate offset
        vectors for specified points in a point cloud.
        """
        pass

    def add_offset_points(self, **kwargs):
        """
        Add new offset points to the original point cloud.
        """
        offset_vectors = self.get_offset_vecs(**kwargs)
        new_points_coords = self.all_coordinates[self.point_indices] + offset_vectors
        # Add coordinates of new points to the original point cloud
        self.all_coordinates = np.concatenate((self.all_coordinates, new_points_coords))

        # Extend the labels list with the labels for new points
        self.labels = np.concatenate((
            self.labels, [self.new_data_label for _ in range(len(new_points_coords))]))

        assert self.all_coordinates.shape[0] == len(self.labels), \
            "The number of labels and coordinates mismatch."


class KDTreeOffsets(OffsetsInterface):

    def __init__(self, **settings):
        super().__init__(**settings)

    def name(self):
        return self.__class__.__name__

    def get_offset_vecs(self, num_neighbors: int = 10) -> np.ndarray:
        """
        Compute offset vectors for specified points using K-D Tree. To move away
        from the point cloud, for each point whose index is in point_indices, we
        use the mean of displacement vectors from this point to its nearest neighbors
        (computed by a K-D Tree) to determine the direction offset vector.

        :param num_neighbors: The number of nearest neighbors to include when calculating
                              displacement vectors. Small values will have a localized offset
                              direction.

        :return: numpy array of shape (len(point_indices), 3) containing offset vectors.
        """
        tree = KDTree(self.all_coordinates)

        offset_vectors = []
        for idx in self.point_indices:
            point = self.all_coordinates[idx]

            # Find nearest neighbors to the current point
            _, nearest_neighbor_indices = tree.query(point, k=num_neighbors)

            # Calculate mean displacement vector from the point to its nearest neighbors
            avg_displacement = np.mean(
                self.all_coordinates[nearest_neighbor_indices] - point, axis=0)

            # Flip the vector to point away from densely populated space,
            # normalize and scale by the input offset magnitude.
            offset_vector = -avg_displacement / np.linalg.norm(
                avg_displacement) * self.offset_magnitude

            offset_vectors.append(offset_vector)

        return np.array(offset_vectors)


class ConvexHullOffsets(OffsetsInterface):

    def __init__(self, all_coordinates: np.ndarray, point_indices: list[int],
                 offset_magnitude: float):
        super().__init__(all_coordinates, point_indices, offset_magnitude)

    def get_offset_vecs(self, **kwargs):
        """
        Calculates offset vectors for the input points using convex hulls
        """
        pass


class CentroidOffsets(OffsetsInterface):

    def __init__(self, all_coordinates: np.ndarray, point_indices: list[int],
                 offset_magnitude: float):
        super().__init__(all_coordinates, point_indices, offset_magnitude)

    def get_offset_vecs(self, **kwargs):
        """
        Calculates offset vectors for the input points using centroids
        """
        pass


OFFSET_METHOD_TO_CLASS = {
    'KDTreeOffsets': KDTreeOffsets,
    'ConvexHullOffsets': ConvexHullOffsets,
    'CentroidOffsets': CentroidOffsets
}


def offset_factory(offset_method: str, **kwargs) -> OffsetsInterface:
    if offset_method in OFFSET_METHOD_TO_CLASS:
        return OFFSET_METHOD_TO_CLASS[offset_method](**kwargs)
    else:
        raise TypeError(f'Method type {offset_method} is not supported.')
