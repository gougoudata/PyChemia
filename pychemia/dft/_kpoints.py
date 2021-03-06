"""
Definition of the set of k-points in reciprocal space
"""

__author__ = "Guillermo Avendano-Franco"
__copyright__ = "Copyright 2014"
__version__ = "1.1"
__maintainer__ = "Guillermo Avendano-Franco"
__email__ = "gtux.gaf@gmail.com"
__status__ = "Development"
__date__ = "November 5, 2014"

import numpy as np
from math import sqrt, ceil

from pychemia.serializer import PyChemiaJsonable, generic_serializer


class KPoints(PyChemiaJsonable):
    """
    Defines an object that contains information about kpoints mesh
    There are two mutually exclusive options:

    Explicit array of kpoints with associated weights OR
    a specification of a grid with an optional set of shifts.

    The default is one single kpoint in gamma
    """

    def __init__(self, kmode='gamma',
                 kpoints_list=None, weights=None,
                 shifts=None, grid=None,
                 kvertices=None, intermediates=None):
        """
        The KPoints class is designed to  store the description of k-points in a code agnostic way.

        There are 5 possible kmodes to describe a set of k-points, currently those modes are not interchangable,
        but that could change in the future.

        The kmodes are 'cartesian', 'reciprocal', 'gamma', 'monkhorst-pack' and 'path'.

        Kmode 'cartesian' and 'reciprocal' uses explicit declaration of a grid of k-points.
        In the case of 'cartesian' the points are vectors in k-space.
        In the case of 'reciprocal' the points are the factors for the vectors defining the reciprocal lattice.
        The variable 'kpoints_list' is a numpy array with a shape of ('nkpt', 3)
        The variable 'weigths' is a numpy array with the weights associated to each point.
        by default all the weights are equal to  1.

        Kmode 'gamma' and 'monkhorst-pack' uses an uniform grid to describe the k-points mesh.
        The variable 'grid' describes the number of points on each dimension an it is a numpy array
        with 3 values.
        The variable 'shifts' describe the shift done to the grid according to the mode selected.
        The internal value 'nkpt' will be simply the product of the three values of the grid.
        Typically ab-initio packages will try to exclude from that grid equivalent k-points due to
        symmetry considerations.

        Kmode 'path' is specially useful for band-structure calculations, in this case the variable
        'kvertices' contains all the vertices, usually high symmetry points and the variable
        'intermediates' contains the number of k-points created between two consecutive vertices.

        When a Kpoints object is created without any arguments, the default will be a kmode='gamma',
        with a grid=[1, 1, 1] and shifts=[0, 0, 0]

        :param kmode: The options are 'cartesian', 'reciprocal', 'gamma', 'monkhorst-pack'
        :param kpoints_list: Explicit list of k-points (Only for 'cartesian' and 'reciprocal')
        :param weights: List of weights associated to each k-point (Only for 'cartesian' and 'reciprocal')
        :param grid: Number of kpoints on each direction (Only for 'gamma' and 'monkhorst-pack')
        :param shifts: Shift applied to the grid (Only for 'gamma' and 'monkhorst-pack')
        :param kvertices: List of vertices for a path of k-points (Only for 'path')
        :param intermediates: Number of intermediates between two vertices (Only for 'path')

        :rtype : Kpoints object
        """
        if kmode.lower() not in ['cartesian', 'reciprocal', 'gamma', 'monkhorst-pack', 'path']:
            raise ValueError("kmode must be 'cartesian', 'reciprocal', 'gamma', 'monkhorst-pack' or 'path'")

        self.kmode = kmode.lower()

        # All the variables initially None
        self.kpoints_list = None
        self.weights = None
        self.grid = None
        self.shifts = None
        self.kvertices = None
        self.intermediates = None

        # Explicit list of k-points
        if self.kmode in ['cartesian', 'reciprocal']:
            self.set_kpoints_list(kpoints_list, weights)
        # Grid specification
        elif self.kmode in ['gamma', 'monkhorst-pack']:
            self.set_grid(grid, shifts)
        # Path along the K-space
        elif self.kmode == 'path':
            if kvertices is None:
                self.kvertices = np.array([[0, 0, 0]])
            else:
                if np.array(kvertices).shape == (3,):
                    self.kvertices = np.array(kvertices).reshape((-1, 3))
                elif np.array(kvertices).shape[1] == 3:
                    self.kvertices = np.array(kvertices)
                else:
                    raise ValueError("Wrong value for kvertices, should be an array with shape (nkpt,3)")
            if intermediates is None:
                self.intermediates = 1
            else:
                self.intermediates = int(intermediates)

    def add_kpt(self, kpoint, weight=1):
        """
        Add one extra kpoint to the kpoints_list in the case of
        kmode 'cartesian' or 'reciprocal'

        :param kpoint: (list, numpy.array) The kpoint to be added
        :param weight: (int, float) the weight associated to that point
        """

        assert (self.kmode in ['cartesian', 'reciprocal'])
        self.kpoints_list = np.append(self.kpoints_list, kpoint).reshape([-1, 3])
        self.weights = np.append(self.weights, weight)

    def set_kpoints_list(self, kpoints_list, weights):
        """
        Set an explicit list of kpoints with a proper check of correct arguments

        :param kpoints_list: Explicit list of k-points (Only for 'cartesian' and 'reciprocal')
        :param weights: List of weights associated to each k-point (Only for 'cartesian' and 'reciprocal')
        """
        assert (self.kmode in ['cartesian', 'reciprocal'])
        if kpoints_list is None:
            self.kpoints_list = np.array([[0, 0, 0]])
        else:
            if np.array(kpoints_list).shape == (3,):
                self.kpoints_list = np.array(kpoints_list).reshape((-1, 3))
            elif np.array(kpoints_list).shape[1] == 3:
                self.kpoints_list = np.array(kpoints_list)
            else:
                raise ValueError("Wrong value for kpoints_list, should be an array with shape (nkpt,3)")
        nkpt = len(self.kpoints_list)
        if weights is None:
            self.weights = np.ones(nkpt)
        elif len(np.array(weights)) == nkpt:
            self.weights = np.array(weights)
        else:
            raise ValueError("Wrong value for weights, should be an array with shape (nkpt,)")

    def set_grid(self, grid, shifts=None):
        """
        Set a grid of kpoints with a proper check of correct arguments

        :param grid: Number of kpoints on each direction (Only for 'gamma' and 'monkhorst-pack')
        :param shifts: Shift applied to the grid (Only for 'gamma' and 'monkhorst-pack')
        """

        assert (self.kmode in ['gamma', 'monkhorst-pack'])
        if grid is None:
            self.grid = np.ones(3)
        elif np.array(grid).shape == (3,):
            self.grid = np.array(grid)
        else:
            raise ValueError("Wrong value for grid, should be an array with shape (3,)")
        if shifts is None:
            self.shifts = np.zeros(3)
        elif np.array(shifts).shape == (3,):
            self.shifts = np.array(shifts)
        else:
            raise ValueError("Wrong value for shifts, should be an array with shape (3,)")

    @property
    def nkpt(self):
        """
        Number of kpoints
        For a grid the value is the product of the number of kpoints
        on each direction.
        """
        if self.kmode in ['cartesian', 'reciprocal']:
            return len(self.kpoints_list)
        elif self.kmode in ['gamma', 'monkhorst-pack']:
            return np.prod(self.grid)
        elif self.kmode == 'path':
            return len(self.kvertices) * self.intermediates

    def __str__(self):
        """
        String representation of the KPoints object
        """
        kp = ' Mode  : ' + self.kmode + '\n'
        if self.kmode in ['cartesian', 'reciprocal']:
            kp += ' Number of k-points: ' + str(self.nkpt) + '\n\n'
            for i in range(self.nkpt):
                kp += (" %10.5f %10.5f %10.5f %15.5f\n"
                       % (self.kpoints_list[i, 0], self.kpoints_list[i, 1], self.kpoints_list[i, 2], self.weights[i]))
        elif self.kmode in ['gamma', 'monkhorst-pack']:
            kp += ' Grid  : ' + str(self.grid) + '\n'
            kp += ' Shift : ' + str(self.shifts) + '\n'
        elif self.kmode == 'path':
            kp += ' Number of intermediates: ' + str(self.intermediates) + '\n\n'
            for vertex in self.kvertices:
                kp += " %10.5f %10.5f %10.5f\n" % (vertex[0], vertex[1], vertex[2])
        return kp

    @property
    def to_dict(self):

        ret = {}
        for i in self.__dict__:
            ret[i] = generic_serializer(self.__dict__[i])
        return ret

    @classmethod
    def from_dict(cls, json_dict):
        if json_dict['kmode'] in ['cartesian', 'reciprocal']:
            return cls(kmode=json_dict['kmode'], kpoints_list=json_dict['kpoints_list'],
                       weights=json_dict['weights'])
        elif json_dict['kmode'] in ['gamma', 'monkhorst-pack']:
            return cls(kmode=json_dict['kmode'], grid=json_dict['grid'], shifts=json_dict['shifts'])
        elif json_dict['kmode'] == 'path':
            return cls(kmode=json_dict['kmode'], kvertices=json_dict['kvertices'],
                       intermediates=json_dict['intermediates'])

    @staticmethod
    def max_kpoints(structure, kpoints_per_atom=1000):
        """
        Returns the maximal grid of kpoints allowed during the
        kpoints convergence test. Based on the routine used in
        pymatgen.
        """

        lengths = [sqrt(sum(map(lambda y: y ** 2, structure.cell[i]))) for i in xrange(3)]
        ngrid = kpoints_per_atom / structure.natom
        mult = (ngrid * lengths[0] * lengths[1] * lengths[2]) ** (1.0 / 3.0)
        num_div = [int(ceil(1.0 / lengths[i] * mult)) for i in xrange(3)]
        num_div = [i if i > 0 else 1 for i in num_div]
        return num_div[0], num_div[1], num_div[2]

    def set_optimized_grid(self, lattice, density_of_kpoints=None, number_of_kpoints=None):
        """
        Returns a grid optimized for the given structure

        :param lattice: A PyChemia Lattice object
        :param number_of_kpoints: Aproximate number of kpoints to use
        """
        if number_of_kpoints is None and density_of_kpoints is None:
            raise ValueError("Provide density or number of kpoints")
        if number_of_kpoints is not None and density_of_kpoints is not None:
            raise ValueError("Provide density OR number of kpoints, not both")

        # Reciprocal lattice object
        rlattice = lattice.reciprocal()
        rcell = rlattice.cell

        if number_of_kpoints is not None:
            vol = 1.0 / lattice.volume
            density_of_kpoints = nkpt / vol

        # lets get the cell ratios
        a1 = sqrt(rcell[0][0] ** 2 + rcell[0][1] ** 2 + rcell[0][2] ** 2)
        a2 = sqrt(rcell[1][0] ** 2 + rcell[1][1] ** 2 + rcell[1][2] ** 2)
        a3 = sqrt(rcell[2][0] ** 2 + rcell[2][1] ** 2 + rcell[2][2] ** 2)

        factor = pow(density_of_kpoints, 1.0 / 3.0)
        self.grid = np.array([int(max(ceil(factor * a1), 1)),
                              int(max(ceil(factor * a2), 1)),
                              int(max(ceil(factor * a3), 1))])
