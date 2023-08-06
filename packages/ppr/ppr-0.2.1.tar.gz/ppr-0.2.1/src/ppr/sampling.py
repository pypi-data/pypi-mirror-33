#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for sampling based motion planning for path following.
"""
import time
import numpy as np
from .cpp.graph import Graph
from .path import TolerancedNumber, TrajectoryPt
from .halton import HaltonSampler
from .util import print_debug

#=============================================================================
# Sampling stuff
#=============================================================================
class SolutionPoint:
    """ class to save intermediate solution info for trajectory point
    """
    def __init__(self, tp):
        self.tp_init = tp
        self.tp_current = tp
        self.q_best = []
        self.jl = []
        
        self.samples = None
        self.joint_solutions = np.array([])
        self.num_js = 0
        self.q_fixed_samples = None
        self.is_redundant = False
    
    def setup_halton_sampler(self, dim):
        self.hs = HaltonSampler(dim)
    
    def add_redundant_joint_samples(self, robot, n=10, method='random'):
        if method == 'random':
            qsn = np.random.rand(n, robot.ndof-3)
            new_samples = robot.scale_input(qsn)
            if self.q_fixed_samples is None:
                print_debug("Using 'random' sampling for redundant kinematics")
                self.q_fixed_samples = new_samples
            else:
                self.q_fixed_samples = np.vstack((self.q_fixed_samples,
                                                  new_samples))
        elif method == 'halton':
            if self.q_fixed_samples is None:
                print_debug("Using 'halton' sampling for redundant kinematics")
                self.setup_halton_sampler(robot.ndof-3)
                qsn = self.hs.get_samples(n)
                new_samples = robot.scale_input(qsn)
                self.q_fixed_samples = new_samples
            else:
                qsn = self.hs.get_samples(n)
                new_samples = robot.scale_input(qsn)
                self.q_fixed_samples = np.vstack((self.q_fixed_samples,
                                                  new_samples))
        elif method == 'normal':
            qsn = np.random.randn(n, robot.ndof-3) / 3 + 0.5
            qsn[qsn < 0] = 0
            qsn[qsn > 1] = 1
            if self.q_fixed_samples is None:
                print_debug("Using 'normal' sampling for redundant kinematics")
                new_samples = robot.scale_input(qsn)
                self.q_fixed_samples = new_samples
            else:
                new_samples = robot.scale_input(qsn)
                self.q_fixed_samples = np.vstack((self.q_fixed_samples,
                                                  new_samples))
        else:
            raise ValueError("Unkown method: " + method)
    
    def calc_joint_solutions(self, robot, tp_discrete, check_collision = False, scene=None):
        """ Convert a cartesian trajectory point to joint space """
        # input validation
        if check_collision:
            if scene == None:
                raise ValueError("scene is needed for collision checking")
        
        # use different joint limits for redundant joints
        if robot.ndof > 3:
            # save origanal joint limits
            orig_jl = robot.jl
            robot.jl = self.jl
        
        #tp_discrete = self.tp_current.discretise()
        joint_solutions = []
        for cart_pt in tp_discrete:
            if self.is_redundant:
                sol = robot.ik(cart_pt, q_fixed_samples=self.q_fixed_samples)
            else:
                sol = robot.ik(cart_pt)
            if sol['success']:
                for qsol in sol['q']:
                    if check_collision:
                        if not robot.check_collision(qsol, scene):
                            joint_solutions.append(qsol)
                    else:
                        joint_solutions.append(qsol)
        
        if robot.ndof > 3:
            # reset original joint_limits
            robot.jl = orig_jl 
        
        return np.array(joint_solutions)
    
    def add_joint_solutions(self, robot, N, N_red, method, *arg, **kwarg):
        # get joint solutions for task space points
        if method == 'grid':
            tp = self.tp_current.discretise()
        else:
            tp = self.tp_current.get_samples(N, method=method)
        
        # sample redundant joints if needed
        if self.is_redundant:
            self.add_redundant_joint_samples(robot, n=N_red, method=method)
        
        js = self.calc_joint_solutions(robot, tp, *arg, **kwarg)
        
        # cache al calculated information so far
        self.num_js += len(js)
        if self.samples is None:
            self.samples = tp
            self.joint_solutions = js
        elif len(self.joint_solutions) == 0:
            self.samples = np.vstack((self.samples, tp))
            self.joint_solutions = js
        else:
            self.samples = np.vstack((self.samples, tp))
            if len(js) > 0:
                self.joint_solutions = np.vstack((self.joint_solutions, js))
    
    def add_joint_solutions_grid_sampling(self, robot, check_collision = False, scene=None):
        """ Convert a cartesian trajectory point to joint space """

        # input validation
        if check_collision:
            if scene == None:
                raise ValueError("scene is needed for collision checking")

        # use different joint limits for redundant joints
        if self.is_redundant:
            # save origanal joint limits
            orig_jl = robot.jl
            robot.jl = self.jl

        tp_discrete = self.tp_current.discretise()
        joint_solutions = []
        for cart_pt in tp_discrete:
            sol = robot.ik(cart_pt)
            if sol['success']:
                for qsol in sol['q']:
                    if check_collision:
                        if not robot.check_collision(qsol, scene):
                            joint_solutions.append(qsol)
                    else:
                        joint_solutions.append(qsol)

        if self.is_redundant:
            # reset original joint_limits
            robot.jl = orig_jl 
        
        # overwrite existing joint solutions
        self.joint_solutions = np.array(joint_solutions)
    
    def get_joint_solutions(self):
        return self.joint_solutions
        
    
    def get_new_bounds(self, l, u, m, red=4):
        """ create new interval smaller than the old one (l, u)
        reduced in length by a factor red.
        m is the value around wich the new interval should be centered
        the new interval may not go outside the old bounds
        """
        delta = abs(u - l) / red
        l_new = max(m - delta, l)
        u_new = min(m + delta, u)
        return l_new, u_new
    
    def resample_trajectory_point(self, robot, *arg, **kwarg):
        """ create a new trajectory point with smaller bounds,
        but the same number of samples
        use the value from the forward kinematics pfk as the center
        of the new interval
        """
        pfk = robot.fk(self.q_best)
        p_new = []
        for i, val in enumerate(self.tp_current.p):
            if self.tp_current.hasTolerance[i]:
                # check for rounding errors on pfk
                if pfk[i] < val.l:
                    pfk[i] = val.l
                if pfk[i] > val.u:
                    pfk[i] = val.u
                # now calculate new bounds with corrected pkf
                l, u = self.get_new_bounds(val.l, val.u, pfk[i], *arg, **kwarg)
                val_new = TolerancedNumber(pfk[i], l, u, samples=val.s)
            else:
                val_new = val
            p_new.append(val_new)
        self.tp_current = TrajectoryPt(p_new)
    
    def add_samples_to_trajectory_pt(self):
        pass
            
        
def iterative_bfs(robot, path, scene, tol=0.001, red=10, max_iter=10):
    """ Iterative graph construction and search """
    sol_pts = [SolutionPoint(tp) for tp in path]
    if robot.ndof > 3:
        for i in range(len(sol_pts)):
            sol_pts[i].is_redundant = True
            sol_pts[i].jl = robot.jl
    costs = []
    times = []
    start_time = time.time()
    prev_cost = np.inf
    success = False
    for i in range(max_iter):
        # calculate joint solutions
        for sp in sol_pts:
            sp.add_joint_solutions_grid_sampling(robot, check_collision=True, scene=scene)
        # save the calculated joint solutions in a list
        path_js = [sp.get_joint_solutions() for sp in sol_pts]
        sol = get_shortest_path(path_js)
        if sol['success']:
            costs.append(sol['length'])
            times.append(time.time() - start_time)
            if abs(prev_cost - sol['length']) < tol:
                success = True
                break
            else:
                prev_cost = sol['length']
            for i in range(len(sol_pts)):
                sol_pts[i].q_best = sol['path'][i]
                sol_pts[i].resample_trajectory_point(robot, red=red)
                # if redundant robot, update joint limits
                # TODO hard coded that the first joints are the redundant ones
                if robot.ndof > 3:
                    old_joint_limits = sol_pts[i].jl
                    new_joint_limits = []
                    for j in range(len(robot.ik_samples)):
                        jl = old_joint_limits[j]
                        qj = sol['path'][i][j]
                        # check for rounding errors on qj
                        if qj < jl[0]:
                            qj = jl[0]
                        if qj > jl[1]:
                            qj = jl[1]
                        l, u = sol_pts[i].get_new_bounds(jl[0], jl[1], qj, red=red)
                        new_joint_limits.append((l, u ))
                    sol_pts[i].jl = new_joint_limits
                        
        else:
            return {'success': False, 'info': 'stuck when looking for path'}
    
    if success:
        return {'success': True,
                'path': sol['path'],
                'length': sol['length'],
                'length_all_iterations': costs,
                'time': times}
    else:
        return {'success': False,
                'path': sol['path'],
                'length': sol['length'],
                'length_all_iterations': costs,
                'info': 'max_iterations_reached',
                'time': times}

def cart_to_joint(robot, traj_points, method='grid',
                  check_collision = False,
                  scene=None,
                  N_cart=None,
                  N_red_joints=None,
                  return_cc_counter=False):
    """ Convert a path to joint space by descretising and ik.
    
    Every trajectory point in the path is descretised, then for all these
    poses the inverse kinematics are solved.
    
    Parameters
    ----------
    robot : ppr.robot.Robot
    traj_points : list of ppr.path.TrajectoryPt
    check_collision : bool
        If True, a joint solution is only accepted if it does not collide
        with the objects in the scene. (default false)
        Self collision is not checked but assumed to be ensured by the joint
        limits.
    scene : list of ppr.geometry.Rectangle
        A list of objects with which the robot could collide.
    
    Returns
    -------
    list of numpy.ndarray of floats
        A list of arrays with shape (M, ndof) representing possible joint
        positions for every trajectory point.
        The arrays in this list could be very big!
    """
    # counters to log performance
    cc_counter = 0 # check collision counter
    
    if method == 'grid':
        pass
    elif method == 'random':
        q_fixed_samples = np.random.rand(N_red_joints, robot.ndof-3)
    elif method == 'halton':
        hs = HaltonSampler(robot.ndof-3)
        q_fixed_samples = hs.get_samples(N_red_joints)
    else:
        raise ValueError("Method not implemented.")
    
    # input validation
    if check_collision:
        if scene == None:
            raise ValueError("scene is needed for collision checking")
    
    # get discrete version of trajectory points
    if method == 'grid':
        cart_traj = []
        for pt in traj_points:
            cart_traj.append(pt.discretise())
    else:
        cart_traj = []
        for pt in traj_points:
            cart_traj.append(pt.get_samples(N_cart, method=method))

    # solve inverse kinematics for every samples traj point
    # I could add some print statements to have info on unreachable points
    joint_traj = []
    for cart_vec in cart_traj:
        qi = []
        for cart_pt in cart_vec:
            if method == 'grid':
                sol = robot.ik(cart_pt)
            else:
                sol = robot.ik(cart_pt,
                               q_fixed_samples=q_fixed_samples,
                               scale_samples=True)
            if sol['success']:
                for qsol in sol['q']:
                    if check_collision:
                        cc_counter += 1
                        if not robot.check_collision(qsol, scene):
                            qi.append(qsol)
                    else:
                        qi.append(qsol)
        joint_traj.append(np.array(qi))
    
    if return_cc_counter:
        return joint_traj, cc_counter
    else:
        print("Collision checks: " + str(cc_counter))
        return joint_traj

def cart_to_joint_dynamic(robot, traj_points, check_collision = False, scene=None,
                          parameters = {'max_iters': 50, 'min_js': 100, 'js_inc': 10,
                                        'red_js_inc': 10,
                                        'ik_sampling_method': 'random'},
                          return_sample_info=False):
    """ Convert a path to joint space by descretising and ik.
    
    Try to find a minimum number of joint solutions for every trajectory point
    """
    if robot.ndof > 3:
        is_redundant = True
    else:
        is_redundant = False
    
    sol_pts = [SolutionPoint(tp) for tp in traj_points]
    
    # inital joint limits for redundant robots
    if is_redundant:
        for sp in sol_pts:
            sp.jl = robot.jl
            sp.is_redundant = True
    
    for sp  in sol_pts:
        max_iters = 0 + parameters['max_iters'] # +0 to get copy not reference
        print_debug("Processing trajectory point" + str(sp.tp_init))
        while (sp.num_js < parameters['min_js'] and max_iters > 0):
            sp.add_joint_solutions(robot,
                                   parameters['js_inc'],
                                   parameters['red_js_inc'],
                                   parameters['ik_sampling_method'],
                                   check_collision=check_collision,
                                   scene=scene)
            max_iters -= 1
        
        print_debug("Found " + str(len(sp.joint_solutions)) + " joint solutions")
        used_iters = parameters['max_iters'] - (max_iters + 1)
        print_debug("After " + str(used_iters) + " iterations")
    
    if return_sample_info:
        # Debug info
        print_debug("=== Total number of samples ===")
        t_samples = np.array([len(sp.samples) for sp in sol_pts])
        c_samples = np.array([len(sp.q_fixed_samples) for sp in sol_pts])
        print_debug("T-space: " + str(t_samples))
        print_debug("C-space: " + str(c_samples))
        n_total = np.sum(t_samples * c_samples)
        print_debug("TOTAL: " + str(n_total))

        return [sp.get_joint_solutions() for sp in sol_pts], [t_samples, c_samples, n_total]
    else:
        return [sp.get_joint_solutions() for sp in sol_pts]

#def get_shortest_path(Q, method='bfs', path = None, scene = None):
#    """ Wrapper function to select the shortest path method
#    """
#    if method == 'bfs':
#        return _get_shortest_path_bfs(Q)
#    else:
#        raise NotImplementedError("The method " + method + " is not implented yet.")
    
def get_shortest_path(Q, method='bfs'):
    """ Calculate the shortest path from joint space data
    
    When the path with trajectory points is converted to joint space,
    this data can be used to construct a graph and look for the shortest path.
    The current distance metrix is the l1-norm of joint position difference
    between two points.
    
    I still have to implement maximum joint movement and acceleration limits.
    So technically this will always find a shortest path for now.
    
    Parameters
    ----------
    Q : list of nympy.ndarrays of float
        A list with the possible joint positions for every trajectory point
        along a path.
    
    Returns
    -------
    dict
        A dictionary with a key 'success' to indicate whether a path was found.
        If success is True, then the key 'path' contains a list with the joint
        position for every trajectory point that gives the shortest path.
    
    Notes
    -----
    I have a problem with swig type conversions. Therefore the type of the
    input data is checked and changed from float64 to float32.
    """
    Q = _check_dtype(Q)

    n_path = len(Q)
    # initialize graph
    g = Graph()
    for c in Q:
        if len(c) == 0:
            # one of the trajectory points is not reachable
            return {'success': False}
        g.add_data_column(c)
    g.init()

    # run shortest path algorithm
    if method == 'bfs':
        g.run_bfs()
    elif method == 'dijkstra':
        g.run_dijkstra()
    else:
        raise NotImplementedError("The method " + method + " is not implented yet.")

    # print result
    # g.print_graph()
    g.print_path()

    # get joint values for the shortest path
    p_i = g.get_path(n_path)
    cost = g.get_path_cost()

    if p_i[0] == -1:
        return {'success': False}
    else:
        res = []
        for k, i in zip(range(n_path), p_i):
            # TODO ugly all the "unsave" typecasting
            qki = Q[k][i].astype('float64')
            res.append(qki)
        
        return {'success': True, 'path': res, 'length': cost}

def _check_dtype(Q):
    """ Change type if necessary to float32
    
    Due to an unresolved issue with swig and numpy, I have to convert the type.
    
    Parameters
    ----------
    Q : list of nympy.ndarrays of float
        A list with the possible joint positions for every trajectory point
        along a path.
    
    Returns
    -------
    list of nympy.ndarrays of float32
    """
    if Q[0].dtype != 'float32':
        print("converting type of Q")
        for i in range(len(Q)):
            Q[i] = Q[i].astype('float32')
    
    return Q