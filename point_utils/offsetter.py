"""
Module for calculating offset points for the selected points in a point cloud
using different methods.
"""
import logging
from abc import ABC, abstractmethod
import numpy as np
from scipy.spatial import KDTree
from scipy.spatial import ConvexHull

__all__ = ['offset_factory']

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create StreamHandler for console output
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(name)s] %(message)s'))
# Add the handler to the logger
logger.addHandler(handler)


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

    def __init__(self, all_coordinates: np.ndarray, labels: list[str],
                 data_label_to_offset: str, offset_magnitude: float,
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
        new_points_coords = self.all_coordinates[
            self.point_indices] + offset_vectors
        # Add coordinates of new points to the original point cloud
        self.all_coordinates = np.concatenate(
            (self.all_coordinates, new_points_coords))

        # Extend the labels list with the labels for new points
        self.labels = np.concatenate(
            (self.labels,
             [self.new_data_label for _ in range(len(new_points_coords))]))

        assert self.all_coordinates.shape[0] == len(self.labels), \
            "The number of labels and coordinates mismatch."

    @staticmethod
    def normalizer(vec: np.ndarray) -> np.ndarray:
        """
        Normalize the input vector. If the norm of the input vector is zero,
        a random unit vector is returned.

        :param direction_vec: Numpy array of shape (1, 3) representing a direction vector.

        :return: Normalized direction vector.
        """
        norm = np.linalg.norm(vec)

        if np.isclose(norm, 0., atol=1e-18):
            logger.warning(
                "The norm of the input vector is zero. Use a random unit vector."
            )
            vec = np.random.randn(3)
            norm = np.linalg.norm(vec)

        return vec / norm


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

        Note that this method is not suitable for highly symmetric point configurations
        where the neighboring points are uniformly distributed around each point
        since the mean displacement vector for each point is zero, e.g.
        an infinite regular cubic lattice in 3D space.

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

            norm = np.linalg.norm(avg_displacement)
            if np.isclose(norm, 0):
                logger.warning(
                    f"The mean displacement vector for {num_neighbors} nearest neighbors of point {idx} is zero. "
                    "Consider increasing the number of neighbors or using a different method."
                )

            # Flip the vector to point away from densely populated space,
            # normalize and scale by the input offset magnitude.
            offset_vector = -avg_displacement / norm * self.offset_magnitude

            offset_vectors.append(offset_vector)

        return np.array(offset_vectors)


class ConvexHullOffsets(OffsetsInterface):

    def __init__(self, **settings):
        super().__init__(**settings)

    def name(self):
        return self.__class__.__name__

    def get_offset_vecs(self, **kwargs):
        """
        Calculates offset vector for each selected point in the direction of the
        outward normal of the convex hull.

        """
        # Compute the convex hull of the point cloud
        hull = ConvexHull(self.all_coordinates)
        hull_points = self.all_coordinates[hull.vertices]
        tree = KDTree(hull_points)

        offset_vectors = []
        for idx in self.point_indices:
            point = self.all_coordinates[idx]

            # Find the closest facet (triangle) of the convex hull
            _, indices = tree.query(point.reshape(1, -1), k=1)
            print(idx, indices)

            # Approximate the outward normal vector of facet by the vector from
            # the target point to the nearest hull vertex
            nearest_vertex = hull_points[indices[0]]
            direction = point - nearest_vertex

            # Normalize and scale the direction vector by the offset magnitude
            offset_vectors.append(
                self.normalizer(direction) * self.offset_magnitude)

        return np.array(offset_vectors)


class CentroidOffsets(OffsetsInterface):

    def __init__(self, **settings):
        super().__init__(**settings)

    def name(self):
        return self.__class__.__name__

    def get_offset_vecs(self, **kwargs):
        """
        Calculates offset vectors for the specified points that point away from
        the centroid of the entire point cloud.
        """
        # Compute the centroid of the point cloud
        centroid = np.mean(self.all_coordinates, axis=0)

        offset_vectors = []

        for idx in self.point_indices:
            point = self.all_coordinates[idx]
            # Compute the direction vector from the centroid to the point
            direction = point - centroid

            # Normalize and scale the direction vector by the offset magnitude
            offset_vectors.append(
                self.normalizer(direction) * self.offset_magnitude)

        return np.array(offset_vectors)


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
