#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Function to define and proccess robot end-effector paths.

"""

import numpy as np
from matplotlib.patches import Wedge
from .cpp.graph import Graph
from .halton import HaltonSampler

#=============================================================================
# Classes
#=============================================================================

class TolerancedNumber:
    """ A range on the numner line used to define path constraints
    
    It also has a nominal value in the range which can be used in cost
    functions of some sort in the future. For example, if it is preffered
    that the robot end-effector stays close to an optimal pose, but can
    deviate if needed to avoid collision.
    
    Attributes
    ----------
    n : float
        Nominal / preffered value for this number
    u : float
        Upper limit.
    l : float
        lower limit
    s : int
        Number of samples used to produce descrete version of this number.
    range : numpy.ndarray of float
        A sampled version of the range on the number line, including limits.
        The nominal value is not necessary included.
    
    Notes
    -----
    Sampling for orientation is done uniformly at the moment.
    In 3D this is no good and special sampling techniques for angles should be
    used.
    The sampled range is now an attribute, but memory wise it would be better
    if it is a method. Then it is only descritized when needed.
    But it the number of path points will probably be limited so I preffer this
    simpler implementation for now.
    """
    def __init__(self, nominal, lower_bound, upper_bound, samples=10):
        """ Create a toleranced number
        
        Nominal does not have to be in the middle,
        it is the preffered value when we ever calculate some kind of cost.
        
        Parameters
        ----------
        nominal : float
            Nominal / preffered value for this number
        lower_bound : float
        upper_bound : float
        samples : int
            The number of samples taken when a sampled version of the number
            is returned in the range attribute. (default = 10)
        
        Examples
        --------
        >>> a = TolerancedNumber(0.7, 0.0, 1.0, samples = 6)
        >>> a.range
        array([ 0. ,  0.2,  0.4,  0.6,  0.8,  1. ])
        """
        if nominal < lower_bound or nominal > upper_bound:
            raise ValueError("nominal value must respect the bounds")
        self.n = nominal
        self.u = upper_bound
        self.l = lower_bound
        self.s = samples
        self.range = np.linspace(self.l, self.u, self.s)
    
    def set_samples(self, samples):
        self.s = samples
        self.range = np.linspace(self.l, self.u, self.s)

class TrajectoryPt:
    """ Trajectory point for a desired end-effector pose in cartesian space
    
    This object bundles the constraints on the end-effector for one point
    of a path.
    
    Attributes
    ----------
    dim : int
        Pose dimensions, 3 for 2D planning, 6 for 3D planning.
    p : list of numpy.ndarray of float or ppr.path.TolerancedNumber
        Pose constraints for the end-effector (x, y, orientation).
        Can be a fixed number (a float) or a TolerancedNumber
    hasTolerance : list of bool
        Indicates which elements of the pose are toleranced (True) and
        fixed (False).
    p_nominal : list of float
        Same as p for fixed poses, the nominal value for a TolerancedNumber.
    timing : float
        Time in seconds it should be executed relative to the previous path
        point. Not used in current version.
    
    Examples
    --------
    Create a trajectory point at position (1.5, 3.1) with a symmetric
    tolerance of 0.4 on the x position.
    The robot orientation should be between 0 and pi / 4.
    (No preffered orientation, so assumed in the middle, pi / 8)

    >>> x = TolerancedNumber(1.5, 1.0, 2.0)
    >>> y = 3.1
    >>> angle = TolerancedNumber(np.pi / 8, 0.0, np.pi / 4)
    >>> tp = TrajectoryPt([x, y, angle])
    >>> tp.p_nominal
    array([ 1.5       ,  3.1       ,  0.39269908])
    
    A path is created by putting several trajectory points in a list.
    For example a vertical path with tolerance along the x-axis:
    
    >>> path = []
    >>> path.append(TrajectoryPt([TolerancedNumber(1.5, 1.0, 2.0), 0.0, 0]))
    >>> path.append(TrajectoryPt([TolerancedNumber(1.5, 1.0, 2.0), 0.5, 0]))
    >>> path.append(TrajectoryPt([TolerancedNumber(1.5, 1.0, 2.0), 1.0, 0]))
    >>> for p in path: print(p)
    [ 1.5  0.   0. ]
    [ 1.5  0.5  0. ]
    [ 1.5  1.   0. ]
    """
    def __init__(self, pee):
        """ Create a trajectory point from a given pose
        
        [x_position, y_position, angle last joint with x axis]
        
        Parameters
        ----------
        pee : list or numpy.ndarray of float or ppr.path.TolerancedNumber
            Desired pose of the end-effector for this path point,
            every value can be either a float or a TolerancedNumber
        """
        self.dim = len(pee)
        self.p = pee
        self.hasTolerance = [isinstance(pee[i], TolerancedNumber) for i in range(self.dim)]
        p_nominal = []
        for i in range(self.dim):
            if self.hasTolerance[i]:
                p_nominal.append(self.p[i].n)
            else:
                p_nominal.append(self.p[i])
        self.p_nominal = np.array(p_nominal)
        self.timing = 0.1 # with respect to previous point
        
        # for use of halton sampling
        # dimension is the number of toleranced numbers
        self.hs = HaltonSampler(sum(self.hasTolerance))
    
    def __str__(self):
        """ Returns string representation for printing
        
        Returns
        -------
        string
            List with nominal values for x, y and orientation.
        """
        return str(self.p_nominal)
    
    def discretise(self):
        """ Returns a discrete version of the range of a trajectory point
        
        Based on the sampled range in the Toleranced Numbers, a 3 dimensional grid
        representing end-effector poses that obey the trajectory point constraints.
        
        Parameters
        ----------
        pt : ppr.path.TrajectoryPt
        
        Returns
        -------
        numpy.ndarray
            Array with shape (M, 3) containing M possible poses for the robot
            end-effector that  obey the trajectory point constraints.
        
        Examples
        --------
        >>> x = TolerancedNumber(1, 0.5, 1.5, samples=3)
        >>> y = TolerancedNumber(0, -1, 1, samples=2)
        >>> pt = TrajectoryPt([x, y, 0])
        >>> pt.discretise()
        array([[ 0.5, -1. ,  0. ],
               [ 1. , -1. ,  0. ],
               [ 1.5, -1. ,  0. ],
               [ 0.5,  1. ,  0. ],
               [ 1. ,  1. ,  0. ],
               [ 1.5,  1. ,  0. ]])
        """
        r = []
        for i in range(self.dim):
            if self.hasTolerance[i]:
                r.append(self.p[i].range)
            else:
                r.append(self.p[i])
        grid = create_grid(r)
        return grid
    
    def get_samples(self, n, method='random'):
        """ Return sampled trajectory point based on values between 0 and 1
        """
        # check input
        sample_dim = sum(self.hasTolerance) # count the number of toleranced numbers
        
        if method == 'random':
            r = np.random.rand(n, sample_dim)
        elif method == 'halton':
            r = self.hs.get_samples(n)
        else:
            raise ValueError("Method not implemented.")
            
        # arrange in array and rescale the samples
        samples = []
        cnt = 0
        for i, val in enumerate(self.p):
            if self.hasTolerance[i]:
                samples.append(r[:, cnt] * (val.u - val.l) + val.l)
                cnt += 1
            else:
                samples.append(np.ones(n) * val)
        
        return np.vstack(samples).T

    def plot(self, axes_handle, show_tolerance=True):
        """ Visualize the path on given axes
        
        Parameters
        ----------
        axes_handle : matplotlib.axes.Axes
        show_tolerance : bool
            If True, the range for a TolerancedNumber is showed.
            A bar for x or y position, A wedge for orientation tolerance.
            (default True)
        """
        pn = self.p_nominal
        axes_handle.plot(pn[0], pn[1], 'k*')
        if show_tolerance:
            if self.hasTolerance[0]:
                do = -self.p[0].l + pn[0]
                du =  self.p[0].u - pn[0]
                axes_handle.errorbar(pn[0], pn[1], xerr=[[do], [du]], color=(0.5, 0.5, 0.5))
            if self.hasTolerance[1]:
                do = -self.p[1].l + pn[1]
                du =  self.p[1].u - pn[1]
                axes_handle.errorbar(pn[0], pn[1], yerr=[[do], [du]], color=(0.5, 0.5, 0.5))
            if self.hasTolerance[2]:
                # scale radius relative to trajectory point position
                radius = (pn[0] + pn[1]) / 20
                do = self.p[2].l * 180 / np.pi
                du = self.p[2].u * 180 / np.pi
                arc = Wedge((pn[0], pn[1]), radius, do, du, facecolor=(0.5, 0.5, 0.5, 0.5))
                axes_handle.add_patch(arc)

class TrajectoryPtLineTol():
    """ Modified TrajectoryPt, where the tolerance is given
    along a line with a specific angle with the x-asis.
    This way, instead of specifying the x and y tolerance, the discrete points
    lie on a straigh line (not a box). It can be used to specify a tolerance
    perpendicular to a path.

    Important: the orientation of the end-effector p[2]
    is also specified relative to the path.

    Attributs
    ---------
    p : list or numpy.ndarray of float
        Desired pose of the end-effector for this path point.
    tn : ppr.path.TolerancedNumber
         The tolerance along the line making ang angle with the x-axis.
    a : float
        Angle of the line along which the tolerance is applied, given
        relative to x-axis, in radians.
    """
    def __init__(self, pee, tolerance, angle):
        """ Create a trajectory point from a given pose
        
        [x_position, y_position, angle last joint with x axis]
        
        Parameters
        ----------
        pee : list or numpy.ndarray of float
            Desired pose of the end-effector for this path point.
        tolerance : ppr.path.TolerancedNumber
            The tolerance along the line making ang angle with the x-axis.
        angle : float
            Angle of the line along which the tolerance is applied, given
            relative to x-axis, in radians.
        """
        self.dim = len(pee)
        self.p = pee
        # only the last index can have tolerance, so this can be simplified
        self.hasTolerance = [False, False, isinstance(pee[2], TolerancedNumber)]
        p_nominal = [self.p[0], self.p[1]]
        if self.hasTolerance[2]:
            p_nominal.append(self.p[2].n)
        else:
            p_nominal.append(self.p[2])
        self.p_nominal = np.array(p_nominal)
        self.tn = tolerance
        self.a = angle
        self.timing = 0.1 # with respect to previous point
    
    def __str__(self):
        """ Returns string representation for printing
        
        Returns
        -------
        string
            List with nominal values for x, y and orientation.
        """
        return str(self.p)
    
    def discretise(self):
        """ Returns a discrete version of the range of a trajectory point
        
        Based on the sampled range along the slanted line, different
        end-effector poses are created.
        
        Parameters
        ----------
        pt : ppr.path.TrajectoryPt
        
        Returns
        -------
        numpy.ndarray
            Array with shape (M, 3) containing M possible poses for the robot
            end-effector that  obey the trajectory point constraints.
        
        Examples
        --------
        >>> v = TolerancedNumber(0, -1, 2, samples=4)
        >>> v.range
        array([-1.,  0.,  1.,  2.])
        >>> pt = TrajectoryPtLineTol([4, 3, 0], v, np.pi/2)
        >>> pt.discretise()
        array([[ 4.        ,  2.        ,  1.57079633],
               [ 4.        ,  3.        ,  1.57079633],
               [ 4.        ,  4.        ,  1.57079633],
               [ 4.        ,  5.        ,  1.57079633]])
        
        >>> angle = TolerancedNumber(0, -0.2, 0.2, samples=3)
        >>> pt2 = TrajectoryPtLineTol([4, 3, angle], v, np.pi/2)
        >>> pt2.discretise()
        array([[ 4.        ,  2.        ,  1.37079633],
               [ 4.        ,  3.        ,  1.37079633],
               [ 4.        ,  4.        ,  1.37079633],
               [ 4.        ,  5.        ,  1.37079633],
               [ 4.        ,  2.        ,  1.57079633],
               [ 4.        ,  3.        ,  1.57079633],
               [ 4.        ,  4.        ,  1.57079633],
               [ 4.        ,  5.        ,  1.57079633],
               [ 4.        ,  2.        ,  1.77079633],
               [ 4.        ,  3.        ,  1.77079633],
               [ 4.        ,  4.        ,  1.77079633],
               [ 4.        ,  5.        ,  1.77079633]])
        """
        if self.hasTolerance[2]:
            p_final = []
            for rel_o_i in self.p[2].range:
                pi = get_points_on_line(self.p[0], self.p[1], rel_o_i, self.a, self.tn.range)
                p_final.append(pi)
            p_final = np.vstack(p_final)

            return p_final
        else:
            return get_points_on_line(self.p[0], self.p[1], self.p[2], self.a, self.tn.range)
    
    def plot(self, axes_handle, show_tolerance=True, wedge_radius=None):
        """ Visualize the path on given axes
        
        Parameters
        ----------
        axes_handle : matplotlib.axes.Axes
        show_tolerance : bool
            If True, the range for a TolerancedNumber is showed.
            A bar for x or y position, A wedge for orientation tolerance.
            (default True)
        """
        pn = self.p_nominal
        axes_handle.plot(pn[0], pn[1], 'k*')
        if show_tolerance:
            R =np.array([[np.cos(self.a),  -np.sin(self.a)],
                         [np.sin(self.a),   np.cos(self.a)]])
            p1 = np.dot( R, np.array([self.tn.l, 0])[:, None] )
            p2 = np.dot( R, np.array([self.tn.u, 0])[:, None] )
            p1 = p1 + pn[:2][:, None]
            p2 = p2 + pn[:2][:, None]
            axes_handle.plot([p1[0], p2[0]], [p1[1], p2[1]], '*-', color=(0.5, 0.5, 0.5))
            if self.hasTolerance[2]:
                # scale radius relative to trajectory point position
                if wedge_radius == None:
                    radius = (pn[0] + pn[1]) / 20
                else:
                    radius = wedge_radius
                do = (self.p[2].l + self.a) * 180 / np.pi
                du = (self.p[2].u + self.a) * 180 / np.pi
                arc = Wedge((pn[0], pn[1]), radius, do, du, facecolor=(0.5, 0.5, 0.5, 0.5))
                axes_handle.add_patch(arc)

#=============================================================================
# Utile functions
#=============================================================================

def get_points_on_line(x, y, rel_o, a, r):
    """ Get points on line segment

    A line segment going trough (x, y) making an angle a with the x-axis.
    r constaints the ticks, for example on the line from on unit before (x, y)
    to 2 units after (x, y) => r = [-1, 0, 1, 2]

    Parameters
    ----------
    x : float
        x-coordinate
    y : float
        y-coordinate
    a : float
        Angle of line segment with x-axis
    r : numpy.ndarray of float
        Vector indicating how long the line segment is and which points
        should be sampled.
    rel_o : float
        Orientation of end-effector relative to path
    
    Returns
    -------
    numpy.ndarray of float
        Array with shape (Np, dim), every row represents a pose
        of the robot end-effector.
    """
    R =np.array([[np.cos(a),  -np.sin(a)],
                 [np.sin(a),   np.cos(a)]])
    Np = len(r)
    r = np.vstack(( r, np.zeros(Np) )) # project range along x-axis
    r = np.dot(R, r)                   # rotate range with angle a
    p_xy = np.array([[x], [y]])        # shape (2, 1)
    p_xy = p_xy + r                    # use broadcasting to add range, get shape (2, Np)
    abs_o = rel_o + a
    p_angle = abs_o * np.ones(Np)          # constant angle a for all poses
    return np.vstack((p_xy, p_angle)).T # add angle and transpose to get shape (Np, 3)

def create_grid(r):
    """ Create an N dimensional grid from N arrays
    
    Based on N lists of numbers we create an N dimensional grid containing
    all possible combinations of the numbers in the different lists.
    An array can also be a single float if their is now tolerance range.
    
    Parameters
    ----------
    r : list of numpy.ndarray of float
        A list containing numpy vectors (1D arrays) representing a sampled
        version of a range along an axis.
    
    Returns
    -------
    numpy.ndarray
        Array with shape (M, N) where N is the number of input arrays and
        M the number of different combinations of the data in the input arrays.
    
    Examples
    --------
    >>> a = [np.array([0, 1]), np.array([1, 2, 3]), 99]
    >>> create_grid(a)
    array([[ 0,  1, 99],
           [ 1,  1, 99],
           [ 0,  2, 99],
           [ 1,  2, 99],
           [ 0,  3, 99],
           [ 1,  3, 99]])
    """
    grid = np.meshgrid(*r)
    grid = [ grid[i].flatten() for i in range(len(r)) ]
    grid = np.array(grid).T
    return grid