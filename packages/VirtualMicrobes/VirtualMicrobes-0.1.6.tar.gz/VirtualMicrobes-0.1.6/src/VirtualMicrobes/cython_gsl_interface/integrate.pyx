# # cython: profile=True
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True

import cython
import sys
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.math cimport isnan, isinf, round, ceil
from cython cimport parallel
from collections import OrderedDict 

cdef const gsl_odeiv2_step_type * rk2 = gsl_odeiv2_step_rk2
cdef const gsl_odeiv2_step_type * rk4 = gsl_odeiv2_step_rk4
cdef const gsl_odeiv2_step_type * rkf45 = gsl_odeiv2_step_rkf45
cdef const gsl_odeiv2_step_type * rkck = gsl_odeiv2_step_rkck
cdef const gsl_odeiv2_step_type * rk8pd = gsl_odeiv2_step_rk8pd
# cdef const gsl_odeiv2_step_type * rk2imp = gsl_odeiv2_step_rk2imp
# cdef const gsl_odeiv2_step_type * rk4imp = gsl_odeiv2_step_rk4imp
# cdef const gsl_odeiv2_step_type * bsimp = gsl_odeiv2_step_bsimp
# cdef const gsl_odeiv2_step_type * rk1imp = gsl_odeiv2_step_rk1imp
cdef const gsl_odeiv2_step_type * msadams = gsl_odeiv2_step_msadams
cdef const gsl_odeiv2_step_type * msbdf = gsl_odeiv2_step_msbdf


cdef void calc_grid_diffusion_force(integrator_str * int_s) nogil:
    ''' 
    Calculate the diffusion forces from neighbouring grid points
    
    INSPIRATION for diffusion *cash2.cpp*
    void DiffusionDB(double **a,double diff_rate,struct point**nei[])
    {
      static double **influx=NULL;
      int i, j, nc, nr;
    
      nr = nrow;
      nc = ncol;
    
      /* initialize */
      if(influx==NULL)
        influx = NewDB();
    
      for (i=1; i <= nr; i++)
        /*$dir force_vector*/
        for (j=1; j <= nc; j++){
          influx[i][j] = a[nei[1][i][j].row][nei[1][i][j].col]
                  +a[nei[2][i][j].row][nei[2][i][j].col]
                  +a[nei[3][i][j].row][nei[3][i][j].col]
                  +a[nei[4][i][j].row][nei[4][i][j].col];
        }
    
      for (i=1; i <= nr; i++)
        /*$dir force_vector*/
        for (j=1; j <= nc; j++){
          a[i][j] = a[i][j] + diff_rate*influx[i][j] - 4*diff_rate*a[i][j];
        }
    }
    
    Parameters
    ----------
    int_s : integrator_str
        integrator structure at a single grid point
    '''
    cdef int i, j  
    cdef mol_str * small_mol
    cdef mol_str * small_mol_nei
    cdef env_str * env
    cdef env_str * nei_env
    cdef integrator_str * nei_int
    env = int_s.sys_s.environment
    for i in range(env.nr_small_mols):
        small_mol = env.small_mols[i]
        small_mol.grid_diffusion_force = 0
        for j in range(int_s.nr_neighbors):
            nei_int = int_s.neighboring_ints_s[j]
            nei_env = nei_int.sys_s.environment
            small_mol_nei = nei_env.small_mols[i]
            nei_conc = nei_int.sys_s.vars[small_mol_nei.variable] 
            small_mol.grid_diffusion_force += nei_int.sys_s.vars[small_mol_nei.variable] 

cdef void calc_grid_diffusion_forces_nogil(spatial_integrator_str * spat_int_s, int num_threads) nogil:
    '''
    Calculates diffusion forces for all grid points
    
    Parameters
    ----------
    spat_int_s : spatial_integrator_str
        spatial integrator structure for whole grid
    num_threads : int
        number of parallel threads
    '''
    cdef int i
    for i in parallel.prange(spat_int_s.nr_integrators, schedule='static', num_threads=num_threads):
        calc_grid_diffusion_force(spat_int_s.integrators_s[i])

cdef void diffuse_mols_to_neighbors(integrator_str * int_s, double diff_const) nogil:
    '''
    Diffuse molecules between the focal grid point and neighbouring grid points.
    
    Updates the focal grid point by adding net diffusion from neighbours to 
    the current concentration for all external molecules in the grid point.
    
    Diffusion forces have been calculated in a separate calculation step by 
    `calc_grid_diffusion_forces_nogil`. The rate of diffusion is scaled by 
    the `diff_const`.
    
    Parameters
    ----------
    int_s : integrator_str
        integrator structure of singel grid point
    diff_const : double
        diffusion constant
    '''
    cdef int i, j  
    cdef mol_str * small_mol 
    cdef mol_str * small_mol_nei 
    cdef env_str * env  
    cdef env_str * nei_env 
    cdef integrator_str * nei_int 
    cdef double prev_conc
    env = int_s.sys_s.environment
    for i in range(env.nr_small_mols):
        small_mol = env.small_mols[i]
        for j in range(int_s.nr_neighbors):
            nei_int = int_s.neighboring_ints_s[j]
            nei_env = nei_int.sys_s.environment
            small_mol_nei = nei_env.small_mols[i]
            prev_conc = int_s.sys_s.vars[small_mol.variable]
            int_s.sys_s.vars[small_mol.variable] = (prev_conc + diff_const * small_mol.grid_diffusion_force -
                                            int_s.nr_neighbors * diff_const * prev_conc) 

cdef void diffuse_mols_on_grid_nogil(spatial_integrator_str * spat_int_s, 
                                     double diff_const, int num_threads) nogil:
    '''
    Diffuse external molecules between neighbouring grid points.
    
    Parameters
    ----------
    spat_int_s : spatial_integrator_str
        spatial integrator structure for whole grid
    diff_const : double
        diffusion constant
    num_threads : int
        number of parallel threads
    '''
    cdef int i 
    for i in parallel.prange(spat_int_s.nr_integrators, schedule='static', num_threads=num_threads):
        diffuse_mols_to_neighbors(spat_int_s.integrators_s[i], diff_const)
                
cdef void print_sys_vars(integrator_str * int_s) nogil:
    '''
    Print all variables in local grid point.
    
    Parameters
    ----------
    int_s : integrator_str
        integrator structure for single grid point
    '''
    cdef int i 
    for i in range(int_s.sys_s.dimension):
        printf(">var%d: %1.30f, ",i, int_s.sys_s.vars[i])
    printf('\n')

cdef bint check_inf_nan_negative(system_str * sys) nogil:
    '''
    Check that no infinite or nan values exist in the ODE systems variables.
    
    Parameters
    ----------
    sys : system_str
        system structure at local grid point
    
    Returns
    -------
    bool : error flag
    '''
    cdef int i 
    cdef bint error = False
    cdef double val
    for i in range(sys.dimension):
        val = sys.vars[i]
        if isnan(val) or isinf(val) or (val < 0.):
            error = True
            break
    return error

cdef int run_system_nogil(integrator_str * int_s, double delta_t, double report_step) nogil:
    '''
    Run integrator on local system ODEs for a specified number of steps.
    
    Run the integrator between every report step and store the sytem state at
    the report time. A check on the success state as well as a sanity check for
    finite and non-nan values is done and reported back.
    
    Parameters
    ----------
    int_s : integrator_str
        integrator structure for single grid point
    delta_t: double
        time delta between diffusion steps
    report_step : double
        time delta of the report step
        
    Returns
    -------
    bool : error flag
    '''
    cdef:
        int i, steps, status
        double ti, t_next_report, t_next, t_end
        bint error = False
        bint report
        double EPSILON = 1e-06 # used for comparing diffusion and report step lengths
    t_end = int_s.time + delta_t
    ti = int_s.time 
    t_last_report = int_s.t_last_report
    gsl_odeiv2_driver_reset(int_s.driver)
    while ti < t_end:
        report = False
        t_next = t_end
        if report_step > 0:
            t_next_report = int_s.t_last_report + report_step
            if t_next_report < (t_next - EPSILON):
                report = True
                t_next = t_next_report
                int_s.t_last_report = t_next
            elif t_next_report < t_next + EPSILON:
                report = True
                int_s.t_last_report = t_next
        ti = t_next
        status = gsl_odeiv2_driver_apply (int_s.driver, & int_s.time, ti, int_s.sys_s.vars)
        if (status != GSL_SUCCESS):
            printf("error (%d) in integration. Step should be recomputed\n" , status)
            print_sys_vars(int_s) 
            printf('\n')           
            error = True
        elif check_inf_nan_negative(int_s.sys_s):
            printf("found nan or inf or negative val after integration. Step should be recomputed\n")
            print_sys_vars(int_s) 
            printf('\n')
            error = True
        if error:
            break
        if report:
            store_state_nogil(int_s.sys_s, int_s.time)
    return error
        
cdef int run_spatial_system_nogil(spatial_integrator_str * spat_int_s, double delta_t_between_diff,
                                  int nr_diffusion_steps, double diff_const, int report_freq,
                                  int num_threads) nogil:
    '''
    Run integrator for a specified number of steps on the spatial grid.
    
    Iterative steps in the routine:
    * calculate diffusion force
    * diffuse molecules on grid
    * run local system ODEs for all grid points
    
    The number of report steps is calculate as [total_simulation_time]/[report frequency]
    
    Parameters
    ----------
    spat_int_s : spatial_integrator_str
        spatial integrator structure for whole grid
    delta_t_between_diff : double
        time delta between diffusion steps
    nr_diffusion_steps : int
        number of diffusion steps to run
    diff_const : double
        diffusion constant
    report_freq : double
        frequency of storing variable state in time point vector
    num_threads : int
        number of parallel threads
        
    Returns
    -------
    bool : error flag
    '''
        
    cdef:
        int i, j
        bint error = False
        double report_step
        double t_tot
    t_tot = nr_diffusion_steps * delta_t_between_diff
    if report_freq > 0:
        report_step = t_tot  / <double>report_freq
    else:
        report_step = t_tot
    for i in range(nr_diffusion_steps):
        calc_grid_diffusion_forces_nogil(spat_int_s, num_threads)
        diffuse_mols_on_grid_nogil(spat_int_s, diff_const*delta_t_between_diff, num_threads)
        for j in parallel.prange(spat_int_s.nr_integrators, schedule='guided', num_threads=num_threads):
            error = run_system_nogil(spat_int_s.integrators_s[j], delta_t_between_diff, report_step )
            if error:
                break
        if error:
            break
    return error

cdef class SpatialIntegrator:
    '''
    A class to integrate the system of ODEs representing the cellular and
    environmental dynamics on the whole grid.
    
    Initializes Integrator objects for single grid point integration.
    
    Parameters
    ----------
    grid : : class:`VirtualMicrobes.environment.Grid.Grid`
        python spatial grid object
    step_function : str
        name of gsl_odeiv2_step_type integration step function
    hstart : double
        hstart initial step size param of stepper
    epsabs : double
        epsabs max absolute error parameter of stepper
    epsrel : double
        epsrel max relative error parameter of stepper
    time : double
        initial time point for integrator run
    product_scaling : double
        scaling parameter for production rate
    per_integrator_threads : int
        number of parallel threads per single grid point integrator
    '''
    def __cinit__(self, grid,
                  step_function="rkf45",
                  double hstart=1e-6, double epsabs=1e-6, double epsrel=0.0, 
                  double time=0, double product_scaling=1., int per_integrator_threads=1):
        self.grid = grid
        self.step_function = step_function
        self.hstart = hstart
        self.epsabs = epsabs
        self.epsrel = epsrel
        self.per_integrator_threads = per_integrator_threads
        self.product_scaling = product_scaling
        self.init_spatial_integrators(self.grid, self.per_integrator_threads,
                              self.step_function, self.hstart, self.epsabs, self.epsrel,
                              time, self.product_scaling) 
        
    def update_diffusion_stepping(self, double delta_t_between_diff):
        self.delta_t_between_diff = delta_t_between_diff
                
    cdef void init_spatial_integrators(self, grid,
                         int per_integrator_threads,
                         char* step_function, double hstart, 
                         double epsabs, double epsrel, double time, double product_scaling): 
        if per_integrator_threads is None:
            per_integrator_threads = self.per_integrator_threads
        if step_function is None:
            step_function = self.step_function
        if hstart is None:
            hstart = self.hstart
        if epsabs is None:
            epsabs = self.epsabs
        if epsrel is None:
            epsrel = self.epsrel
        self.gp_to_integrators_c_dict = OrderedDict()
        cdef Integrator int_c        
        cdef int nr_neighbors
        for i,gp in enumerate(list(grid.gp_iter)):
            nr_neighbors = len(gp.neighborhoods['diffusion'])
            locality = gp.content
            int_c = Integrator.__new__(Integrator, locality, 
                                       nr_neighbors, per_integrator_threads, 
                                       step_function, hstart, epsabs, epsrel, 
                                       product_scaling, time) 
            if not int_c.sys_c.check_sane_vals(): 
                print_sys_vars(&int_c.int_s)
                printf('\n')
                #raise Exception('values not sane')

            self.gp_to_integrators_c_dict[gp] = int_c
        self.add_neighbors()
        self.spat_int_s.nr_integrators = len(self.gp_to_integrators_c_dict)
        self.add_integrator_structs()

    def update_drivers(self, step_function=None, hstart=None, epsabs=None, epsrel=None):
        if step_function is None:
            step_function = self.step_function
        if hstart is None:
            hstart = self.hstart
        if epsabs is None:
            epsabs = self.epsabs
        if epsrel is None:
            epsrel = self.epsrel
        cdef Integrator int_c
        for _gp, int_c in self.gp_to_integrators_c_dict.items():
            int_c.set_params(step_function, hstart, epsabs, epsrel)
            int_c.init_driver()
        print 'Drivers updated with params step_function:{} hstart:{} epsabs:{} epsrel:{}'.format(step_function, hstart, epsabs, epsrel)

    def update_integrators(self, product_scaling, double time, bint reset):
        cdef Integrator int_c
        for gp, int_c in self.gp_to_integrators_c_dict.items():
            if gp.updated:
                int_c.init_sys(gp.content, time, product_scaling,
                               self.per_integrator_threads
                               )
                int_c.init_driver()
            else:
                # update the states of variables 
                int_c.update_sys(time, product_scaling, reset)
        
    cdef void add_neighbors(self):
        cdef Integrator int_c
        for gp, int_c in self.gp_to_integrators_c_dict.items():
            neighbor_gps = gp.neighbor_gps('diffusion')
            neighboring_int_c = [ self.gp_to_integrators_c_dict[gp] for gp in neighbor_gps ]
            int_c.add_neighboring_integrators(neighboring_int_c)
    
    cdef void add_integrator_structs(self):
        cdef int nr_integrators = len(self.gp_to_integrators_c_dict)
        self.spat_int_s.integrators_s = < integrator_str **> PyMem_Malloc(nr_integrators * 
                                                                    sizeof(integrator_str *))
        cdef Integrator int_c 
        cdef int i 
        for i, integrator in enumerate(self.gp_to_integrators_c_dict.values()):
            int_c = integrator
            self.spat_int_s.integrators_s[i] = & int_c.int_s
                       
    def store_nr_time_points_py(self):
        cdef Integrator int_c 
        for int_c in self.gp_to_integrators_c_dict.values():
            int_c.store_nr_time_points_py()

    def run_spatial_system(self, int diffusion_steps, double delta_t_between_diff, 
                           double diffusion_constant,
                           int report_freq,
                           int num_threads): 
        print 'Running system with', num_threads, 'threads', 
        print 'for', diffusion_steps, 'steps of length', delta_t_between_diff,
        print 'at diffusion constant', diffusion_constant,
        print 'and saving', report_freq, 'time points per step.'
        with nogil:
            errors = run_spatial_system_nogil(&self.spat_int_s, delta_t_between_diff,
                                      diffusion_steps, diffusion_constant,
                                      report_freq,
                                      num_threads)
        return errors
    
    def print_spatial_sys_vars(self):
        cdef Integrator int_c 
        for int_c in self.gp_to_integrators_c_dict.values():
            int_c.print_sys_vars()
            print
        
    def __dealloc__(self):
        PyMem_Free(self.spat_int_s.integrators_s)
        
    def diffusion_step(self):
        pass
             
cdef class Integrator:
    '''
    A class to integrate the system of ODEs representing the cellular and
    environmental dynamics at a single grid point.
    
    Parameters
    ----------
    locality : : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    nr_neighbors : int
        number of neighbouring grid points
    num_threads : int
        number of parallel threads
    step_function : str
        name of gsl_odeiv2_step_type integration step function
    hstart : double
        hstart initial step size param of stepper
    epsabs : double
        epsabs max absolute error parameter of stepper
    epsrel : double
        epsrel max relative error parameter of stepper
    init_time : double
        initial time point for integrator run
    product_scaling : double
        scaling parameter for production rate
    '''
  
    def __cinit__(self, locality, int nr_neighbors=0, int num_threads=1, 
                  step_function="rkf45", double hstart=1e-6, double epsabs=1e-6, double epsrel=0.0,
                  double init_time=0., product_scaling=1.):
        '''
        Constructor 
        '''
        self.int_s.nr_neighbors = nr_neighbors
        self.int_s.driver = NULL
        self.int_s.neighboring_ints_s = <integrator_str**>PyMem_Malloc(nr_neighbors * sizeof(integrator_str*))
        self.init_sys(locality, init_time, product_scaling, num_threads)
        self.set_params(step_function, hstart, epsabs, epsrel)
        self.init_driver()
        
    cdef const gsl_odeiv2_step_type * select_step_function(self, char * name="rkf45"):
        cdef const gsl_odeiv2_step_type * stepper = rkf45
        if name == b"rk8pd":
            stepper = rk8pd
        elif name == b"rk2":
            stepper = rk2
        elif name == b"rk4":
            stepper = rk4
        elif name == b"rkf45":
            stepper = rkf45
        elif name == b"rkck":
            stepper = rkck
        elif name == b"msadams":
            stepper = msadams
        else:
            print "unknown driver type:", name 
            print "using rkf45"
        return stepper
        
    cdef void set_params(self, char * step_function, double hstart, double epsabs, double epsrel):
        self.stepper = self.select_step_function(step_function)
        self.hstart = hstart
        self.epsabs = epsabs
        self.epsrel = epsrel
                    
    cdef void init_sys(self, locality, double time, double product_scaling, int num_threads):
        cdef SYSTEM sys = SYSTEM.__new__(SYSTEM, locality, product_scaling, num_threads)             
        self.sys_c = sys
        self.int_s.sys_s = & self.sys_c.sys_s
        self.int_s.vars = & self.sys_c.sys_s.vars
        self.int_s.gsl_sys.function = self.sys_c.sys_s.master_eq
        self.int_s.gsl_sys.dimension = self.sys_c.sys_s.dimension
        self.int_s.gsl_sys.params = self.int_s.sys_s
        self.int_s.time = time
        self.int_s.t_last_report = time
    
    cdef void init_driver(self):
        if self.int_s.driver is not NULL:
            gsl_odeiv2_driver_free(self.int_s.driver)
        self.int_s.driver = gsl_odeiv2_driver_alloc_y_new(
            & self.int_s.gsl_sys, self.stepper, self.hstart, self.epsabs, self.epsrel)

    cdef void update_sys(self, double time, double product_scaling, bint reset):
        self.int_s.time = time
        self.int_s.t_last_report = time
        self.sys_c.update_sys(product_scaling, reset)
        self.int_s.vars = & self.sys_c.sys_s.vars
        
    cdef void add_neighboring_int(self, integrator_str * nei_int_s, int index):
        self.int_s.neighboring_ints_s[index] = nei_int_s
    
    cdef void add_neighboring_integrators(self, integrators_c):
        cdef Integrator nei_int_c
        cdef int i 
        for i, nei_int_c in enumerate(integrators_c):
            self.add_neighboring_int(&nei_int_c.int_s, i)
  
    def run_system(self, double delta_t, int nr_reports):
        errors = run_system_nogil(&self.int_s, delta_t, nr_reports)
        return errors
    
    cdef void print_sys_vars(self):
        cdef int i 
        for i in range(self.int_s.sys_s.dimension):
            print "&var%d: %.30f, " % (i, self.int_s.sys_s.vars[i]),
    
    cdef store_nr_time_points_py(self): 
        cdef SYSTEM sys_c = self.sys_c
        sys_c.store_nr_time_points_py()

    cdef void add_jacobian(self, JAC jac):
        self.int_s.gsl_sys.jacobian = jac
        
    def __dealloc__(self): 
        if self.int_s.driver is not NULL:
            gsl_odeiv2_driver_free(self.int_s.driver)
        PyMem_Free(self.int_s.neighboring_ints_s)
