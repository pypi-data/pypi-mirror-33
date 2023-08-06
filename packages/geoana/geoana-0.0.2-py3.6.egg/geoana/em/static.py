from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import warnings

from .base import BaseEM, BaseMagneticDipole, BaseElectricDipole
from ..spatial import cartesian_2_cylindrical


class MagneticDipoleWholeSpace(BaseMagneticDipole, BaseEM):

    """
    Static magnetic dipole in a wholespace.
    """

    def vector_potential(self, xyz, coordinates="cartesian"):
        """Vector potential of a static magnetic dipole

            .. math::

                \\vec{A}(\\vec{r}) = \\frac{\\mu_0}{4\\pi}
                    \\frac{\\vec{m}\\times\\vec{r}}{r^3}

            :param numpy.ndarray xyz: Location of the receivers(s)
            :param str coordinates: coordinate system that the xyz is provided
                                    in and that the solution will be returned
                                    in (cartesian or cylindrical)
            :rtype: numpy.ndarray
            :return: The magnetic vector potential at each observation location
        """
        supported_coordinates = ["cartesian", "cylindrical"]
        assert coordinates.lower() in supported_coordinates, (
            "coordinates must be in {}, the coordinate system "
            "you provided, {}, is not yet supported".format(
                supported_coordinates, coordinates
            )
        )

        n_obs = xyz.shape[0]

        # orientation of the dipole
        orientation = self.orientation
        if coordinates == "cylindrical":
            orientation = cartesian_2_cylindrical(orientation)
            cylindrical_location = cartesian_2_cylindrical(self.location)
            dxyz = spatial.vector_distance(cylindrical_location)
        else:
            dxyz = self.vector_distance(xyz)
            r = spatial.repeat_scalar(self.distance(xyz))
        m = self.moment * np.atleast_2d(orientation).repeat(n_obs, axis=0)

        m_cross_r = np.cross(m, dxyz)
        return (self.mu / (4 * np.pi)) * m_cross_r / (r**3)

        # offset = self.offset_from_location(xyz)
        # dist = self.distance_from_location(xyz)
        # m_vec = (
        #     self.moment * np.atleast_2d(self.orientation).repeat(n_obs, axis=0)
        # )

        # # Repeat the scalars
        # dist = np.atleast_2d(dist).T.repeat(3, axis=1)

        # m_cross_r = np.cross(m_vec, offset)
        # A = (self.mu / (4 * np.pi)) * m_cross_r / (dist**3)

        # return A

    def magnetic_flux(self, xyz, coordinates="cartesian"):
        """Magnetic flux (:math:`\\vec{b}`) of a static magnetic dipole

            :param numpy.ndarray xyz: Location of the receivers(s)
            :rtype: numpy.ndarray
            :return: The magnetic vector potential at each observation location
        """

        n_obs = xyz.shape[0]

        offset = self.offset_from_location(xyz)
        dist = self.distance_from_location(xyz)
        m_vec = (
            self.moment * np.atleast_2d(self.orientation).repeat(n_obs, axis=0)
        )

        m_dot_r = (m_vec * offset).sum(axis=1)

        # Repeat the scalars
        m_dot_r = np.atleast_2d(m_dot_r).T.repeat(3, axis=1)
        dist = np.atleast_2d(dist).T.repeat(3, axis=1)

        b = (self.mu / (4 * np.pi)) * (
            (3.0 * offset * m_dot_r / (dist ** 5)) -
            m_vec / (dist ** 3)
        )
        return b

    def magnetic_field(self, xyz, coordinates="cartesian"):
        """Magnetic field (:math:`\\vec{h}`) of a static magnetic dipole

        """
        return self.magnetic_flux(xyz, **kwargs) / self.mu

