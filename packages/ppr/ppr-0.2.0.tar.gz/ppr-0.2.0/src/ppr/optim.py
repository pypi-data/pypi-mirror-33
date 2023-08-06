#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes and function related to solving optimisation problems related
to robot path following.
"""

import numpy as np
from scipy.optimize import fmin_slsqp, minimize

#=============================================================================
# Use general minimize interface and implement object oriented
#=============================================================================

class Solver():
    """ Setup and solve an optimal robot motion planning problem
    
    No dual variables implemented at the moment. Look in branch old-master
    optimize.py to see how this can be added.
    """
    def __init__(self, robot, path, scene, w=None):
        self.robot = robot
        self.path = path
        self.scene = scene
        
        # set default weights
        if w == None:
            self.w = {'joint_motion': 1.0,'path_error': 0.0, 'torque': 0.0}
        else:
            self.w = w
            
        self.bnds = []
        self.cons = []
    
    def create_objective(self):
        ndof = self.robot.ndof
            
        # put weights in list
        wb = [self.w[key] for key in self.w]
        
        # if torque objectives, check dynamics
        if wb[2] > 0:
          if not hasattr(self.robot, 'c'):
            msg = "Specify robot dynamic parameter s"
            msg += "using the Robot.set_link_inertia() method"
            raise ValueError(msg)
        
        # setup the desired objective
        if wb[0] > 0 and wb[1] == 0 and wb[2] == 0:
            def obj(x):
                n_path, qp = reshape_path_vector(x, n_dof=ndof)
                return joint_motion_obj(qp)
        elif wb[1] > 0 and wb[2] == 0:
            def obj(x):
                n_path, qp = reshape_path_vector(x, n_dof=ndof)
                return path_error_obj(qp, robot, self.path)
        elif wb[2] > 0:
            def obj(x):
                n_path, qp = reshape_path_vector(x, n_dof=ndof)
                return torque_obj(qp, robot)
        elif wb[0] > 0 and wb[1] > 0 and wb[2] == 0:
            def obj(x):
                n_path, qp = reshape_path_vector(x, n_dof=ndof)
                res =  wb[0] * joint_motion_obj(qp)
                res += wb[1] * path_error_obj(qp, self.robot, self.path)
                return res
        else:
            raise ValueError("This type of objective is not implemented yet.")
        
        return obj
    
    def add_path_constraints(self):
        def path_con(x):
            n_path, qp = reshape_path_vector(x, n_dof=self.robot.ndof)
            return path_ieq_con(qp, self.robot, self.path)
        self.cons.append({'type': 'ineq', 'fun': path_con})
    
    def add_tube_constraints(self):
        def ineq_con(x):
            n_path, qp = reshape_path_vector(x, n_dof=self.robot.ndof)
            return tube_ieq_eq_con(qp, self.robot, self.path)
        #def eq_con(x):
        #    n_path, qp = reshape_path_vector(x, n_dof=self.robot.ndof)
        #    return tube_eq_con(qp, self.robot, self.path)
        self.cons.append({'type': 'ineq', 'fun': ineq_con})
        #self.cons.append({'type': 'eq', 'fun': eq_con})
    
    def add_collision_constaints(self):
        def cc_con(x):
            n_path, qp = reshape_path_vector(x, n_dof=self.robot.ndof)
            return collision_ieq_con(qp, self.robot, self.scene)
        self.cons.append({'type': 'ineq', 'fun': cc_con})
    
    def run(self, q_init):
        obj  = self.create_objective()
        return minimize(obj, q_init, method='SLSQP', 
                        constraints=self.cons,
                        bounds = self.bnds)


#=============================================================================
# Main functions to run the problem
#=============================================================================
def get_optimal_trajectory(robot, path, q_path_init,
                           check_collision=False, scene=None,
                           w={'joint_motion': 1.0,
                               'path_error'  : 0.0,
                               'torque'      : 0.0}):
    """ Formulate and solve optimal path following problem
    
    Parameters
    ----------
    robot : ppr.robot.Robot
    path : list of ppr.path.TrajectoryPt
    q_path_init : list of numpy.ndarray
    w : dict
    
    Returns
    -------
    tuple of numpy.ndarray
        Joint position, velocity and acceleration
    """
    # input validation
    if check_collision:
        if scene == None:
            raise ValueError("scene is needed for collision checking")
    
    n_path = len(path)
    q_init = np.array(q_path_init).flatten()

    # setup the correct objective
    wb = [w[key] for key in w]
    # if torque objectives, check dynamics
    if wb[2] > 0:
      if not hasattr(robot, 'c'):
        msg = "Specify robot dynamic parameter s"
        msg += "using the Robot.set_link_inertia() method"
        raise ValueError(msg)
    if wb[0] > 0 and wb[1] == 0 and wb[2] == 0:
        def obj(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            return joint_motion_obj(qp)
    elif wb[1] > 0 and wb[2] == 0:
        def obj(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            return path_error_obj(qp, robot, path)
    elif wb[2] > 0:
        def obj(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            return torque_obj(qp, robot)
    elif wb[0] > 0 and wb[1] > 0 and wb[2] == 0:
        def obj(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            res =  wb[0] * joint_motion_obj(qp)
            res += wb[1] * path_error_obj(qp, robot, path)
            return res
    else:
        raise ValueError("This type of objective is not implemented yet.")

    # setup inequality constraints
    if check_collision:
        def ieq_con(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            pc = path_ieq_con(qp, robot, path)
            cc = collision_ieq_con(qp, robot, scene)
            return np.hstack((pc, cc))
    else:
        def ieq_con(x):
            n_path, qp = reshape_path_vector(x, n_dof=robot.ndof)
            return path_ieq_con(qp, robot, path)

    # Solve problem
    sol = fmin_slsqp(obj,
                     q_init,
                     f_ieqcons=ieq_con)

    n_path, qp_sol = reshape_path_vector(sol, n_dof=robot.ndof)
    dqs, ddqs = q_derivatives(qp_sol)
    return qp_sol, dqs, ddqs

#=============================================================================
# Objectives
# function structure : xxxx_obj(opt_var, params ...)
    # xxxxx   : name, the thing that is minimized
    # opt_var : the optimizationsv variables
    # parmas  : parameters, such as robot, path, coefficients, ....
# returns
    # a a scalar that has to be minimized
#=============================================================================

def path_error_obj(q_path, robot, path):
    con = []
    for i, tp in enumerate(path):
        pp = tp.p_nominal
        pfk = robot.fk(q_path[i])
        con.append(np.sum((pp - pfk)**2))
    con = np.array(con).flatten()
    return np.sum(con**2)

def joint_motion_obj(q_path):
    dqp = np.diff(q_path, axis=0)

    return np.sum(np.abs(dqp))

def torque_obj(q_path, robot):
    n_path, ndof = q_path.shape
    dqp, ddqp = q_derivatives(q_path)
    tau = np.zeros((n_path, robot.ndof))
    for i in range(n_path):
        tau[i, :] = robot.euler_newton(q_path[i], dqp[i], ddqp[i])
    return np.sum(tau**2)

#=============================================================================
# Constraints
    # function structure : xxxx_eq_con(opt_var, params ...)
    #                    : xxxx_ieq_con(opt, var, params ...)
    # xxxxx   : name, the thing that causes the constraints
    # opt_var : the optimizationsv variables
    # parmas  : parameters, such as robot, path, coefficients, ....
# returns
    # equality constraints: a numpy array, each element has to be zero
    # inequality constraints: a numpy array, each elment is positive when
    # the constraints is satisfied
#=============================================================================

def path_ieq_con(q_path, robot, path, tol=1e-6):
    con = []
    for i, tp in enumerate(path):
        has_tol = tp.hasTolerance
        pfk = robot.fk(q_path[i])
        for i in range(tp.dim):
            if has_tol[i]:
                con.append(-pfk[i] + tp.p[i].u)
                con.append( pfk[i] - tp.p[i].l)
            else:
                con.append(-pfk[i] + tp.p[i] + tol)
                con.append( pfk[i] - tp.p[i] - tol)
    return np.array(con)

def collision_ieq_con(q_path, robot, scene):
    con = []
    for qi in q_path:
        robot_shapes = robot.get_shapes(qi)
        for s1 in robot_shapes:
            for s2 in scene:
                con.append(s1.distance(s2))
    
    return np.array(con)

def tube_ieq_con(q_path, robot, path, tol=1e-6):
    """ Tube inequality constraints

    For explanation see notebook "example_different_trajectory_points.py"
    """
     # lower and upper bound along the tolerance line
    l = [tp.tn.l for tp in path]
    u = [tp.tn.u for tp in path]

    phi = np.array([tp.a for tp in path])
    pose_a = np.vstack([robot.fk(q) for q in q_path])
    pose_d = np.vstack([tp.p_nominal for tp in path])
    pose_e = pose_a - pose_d
    e_x = pose_e[:, 0]
    e_y = pose_e[:, 1]
    e_a = pose_e[:, 2]

    con = []
    con.append( l * np.cos(phi) + e_x )
    con.append( u * np.cos(phi) - e_x )
    con.append( l * np.sin(phi) + e_y )
    con.append( u * np.sin(phi) - e_y )

    # check for tolerance on orientation
    # if tolerance, add inequality constraint
    orientation_con = []
    a_has_tolerance = [tp.hasTolerance[2] for tp in path]
    for i, ht in enumerate(a_has_tolerance):
        if ht:
            orientation_con.append( -e_a[i] + path[i].p[2].u)
            orientation_con.append(  e_a[i] + path[i].p[2].l)
    con.append(np.array(orientation_con))

    return np.hstack(con)

def tube_ieq_eq_con(q_path, robot, path, tol=1e-6):
    """ Add equalities as a pair of inequalities using the tol

    """
     # lower and upper bound along the tolerance line
    l = [tp.tn.l for tp in path]
    u = [tp.tn.u for tp in path]

    phi = np.array([tp.a for tp in path])
    pose_a = np.vstack([robot.fk(q) for q in q_path])
    pose_d = np.vstack([tp.p_nominal for tp in path])
    pose_e = pose_a - pose_d
    e_x = pose_e[:, 0]
    e_y = pose_e[:, 1]
    e_a = pose_e[:, 2]

    con = []
    con.append( l * np.cos(phi) + e_x )
    con.append( u * np.cos(phi) - e_x )
    con.append( l * np.sin(phi) + e_y )
    con.append( u * np.sin(phi) - e_y )

    # check for tolerance on orientation
    # if tolerance, add inequality constraint

    # add equality constraints as 2 inequality constraints
    con.append( e_x * np.sin(phi) + e_y * np.cos(phi) + tol)
    con.append( e_x * np.sin(phi) + e_y * np.cos(phi) - tol)

    orientation_con = []
    a_has_tolerance = [tp.hasTolerance[2] for tp in path]
    for i, ht in enumerate(a_has_tolerance):
        if ht:
            orientation_con.append( -e_a[i] + path[i].p[2].u)
            orientation_con.append(  e_a[i] + path[i].p[2].l)
        else:
            orientation_con.append( e_a[i] + tol)
            orientation_con.append( e_a[i] - tol)
    con.append(np.array(orientation_con))

    return np.hstack(con)

def tube_eq_con(q_path, robot, path, tol=1e-6):
    """ Tube equality constraint

    For explanation see notebook "example_different_trajectory_points.py"
    """
    phi = np.array([tp.a for tp in path])
    pose_a = np.vstack([robot.fk(q) for q in q_path])
    pose_d = np.vstack([tp.p_nominal for tp in path])
    pose_e = pose_a - pose_d
    e_x = pose_e[:, 0]
    e_y = pose_e[:, 1]
    e_a = pose_e[:, 2]

    con = []
    con.append( e_x * np.sin(phi) + e_y * np.cos(phi) )

    # check for tolerance on the orientation
    # if no tolerance allowed, add equality constraint
    orientation_con = []
    a_has_tolerance = [tp.hasTolerance[2] for tp in path]
    for i, ht in enumerate(a_has_tolerance):
        if not ht:
            orientation_con.append( e_a[i] )
    con.append(np.array(orientation_con))

    return np.hstack(con)

#=============================================================================
# Utility functions
#=============================================================================

def reshape_path_vector(v_flat, n_dof=3):
    """ Convert flat vector to n_path x n_dof path array

    n_path is the number of discrete path points.
    This reshaping if often needed to formulate optimization problems.
    The standard optimization variable shape in scipy.optimize is a
    1D vector.

    Parameters
    ----------
    v_flat : ndarray
        Vector of length n_path*ndof containing the joint position vector for
        every path point [q1, q2, ...] with q1 of length ndof.
    ndof : int
        Degrees of freedom of robot.

    Returns
    -------
    tuple of int and numpy.ndarray
        Tuple with first element the number of path poitns and the second
        element an array of shape (n_path, ndof) every row containt the joint
        positions for a single path point.
    
    Examples
    --------
    >>> a = np.array([1, 2, 3, 4, 5, 6])
    >>> N, a_new = reshape_path_vector(a)
    >>> N
    2
    >>> a_new
    array([[1, 2, 3],
           [4, 5, 6]])
    """
    n_path = int(len(v_flat) / n_dof)
    return n_path, v_flat.reshape(n_path, n_dof)

def q_derivatives(q, dt=0.1):
    """ Calculate joint speed and acceleration

    Based on a given path, caculate speed and acceleration using the
    numpy.gradient function. A constant sample time dt is assumed.

    Parameters
    ----------
    q : ndarray
        Array of shape (n_path, ndof) every row containt the joint positions for
        a single path point.
    dt : float
        Sample time for joint position path

    Returns
    -------
    tuple
        (dq, ddq) the joint speed and acceleration along the path.
        Arrays with the same shape as the input path array q.
    """
    dq = np.gradient(q, dt, axis=0)
    ddq = np.gradient(dq, dt, axis=0)
    return dq, ddq

