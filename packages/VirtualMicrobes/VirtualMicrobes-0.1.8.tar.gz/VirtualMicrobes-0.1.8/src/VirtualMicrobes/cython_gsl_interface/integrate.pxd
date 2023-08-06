##@PydevCodeAnalysisIgnore

from cython_gsl cimport *  ##@IgnoreException 
from odes cimport *

ctypedef int (* FUNC) (double t, double y[], double dydt[], void * params) nogil
ctypedef int (* JAC) (double t, double y[], double * dfdy, double dfdt[], void * params) nogil

cdef struct integrator_str:
    gsl_odeiv2_system gsl_sys
    gsl_odeiv2_driver * driver
    double time
    double t_last_report
    double ** vars
    system_str * sys_s
    int nr_neighbors
    integrator_str ** neighboring_ints_s

cdef struct spatial_integrator_str:
    int nr_integrators
    integrator_str ** integrators_s
    
cdef class SpatialIntegrator:
    cdef public gp_to_integrators_c_dict
    cdef public grid
    cdef spatial_integrator_str spat_int_s
    cdef void init_spatial_integrators(self, object, int,
                                       char*, double ,double , 
                                       double, double, double )
    cdef void add_neighbors(self)
    cdef void add_integrator_structs(self)
    cdef int per_integrator_threads
    cdef double delta_t_between_diff, hstart, epsabs, epsrel, product_scaling
    cdef double diffusion_constant
    cdef step_function
    #cdef void store_nr_time_points_py(self)
    
    
cdef class Integrator:
    cdef integrator_str int_s
    cdef const gsl_odeiv2_step_type * stepper
    cdef double time, hstart, epsabs, epsrel
    cdef public SYSTEM sys_c

    cdef const gsl_odeiv2_step_type * select_step_function(self, char * name = ?)
    cdef void init_sys(self, object, double, double, int)
    cdef void init_driver(self)
    cdef void update_sys(self, double, double, bint)
    cdef void set_params(self, char *, double, double, double)
    cdef void add_neighboring_int(self, integrator_str *, int)
    cdef void add_neighboring_integrators(self, object)
    cdef void print_sys_vars(self)
    cdef store_nr_time_points_py(self)
    cdef void add_jacobian(self, JAC)
