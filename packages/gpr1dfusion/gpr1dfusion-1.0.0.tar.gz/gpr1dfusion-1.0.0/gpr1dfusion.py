"""
Classes for Gaussian Process Regression fitting of 1D fusion profile data with errorbars.

Requires installation of the GPR1D package, now available on PyPI.

These classes were developed by Aaron Ho.
"""

import numpy as np
import GPR1D

__all__ = ['RationalQuadraticFGPR1D', 'GibbsInverseGaussianFGPR1D', 'Matern52FGPR1D']


class RationalQuadraticFGPR1D(GPR1D.SimplifiedGaussianProcessRegression1D):
    """
    Implements a GPR with a simple rational quadratic
    kernel, including heteroscedastic error fitting, ie.
    the error is allowed to vary in x. This is the most
    robust kernel, generally able to fit most profiles
    that do not have sudden dramatic changes in gradient,
    such as pedestals.

    Optimization of hyperparameters is only performed
    *once* using settings at the time of the *first*
    call! All subsequent calls use the results of the
    first optimization.
    """
    def __init__(self,x,y,ye,xe=None,length_scale=0.5,regularization_parameter=1.0,epsilon=1.0e-2,nrestarts=5):
        """
        Defines customized GaussianProcessRegression1D instance with
        a pre-defined rational quadratic kernel for both data fit and
        error fit. Input parameters reduced only to essentials and
        most crucial knobs for fine-tuning.

        :arg x: array. Vector of x-values corresponding to data to be fitted.

        :arg y: array. Vector of y-values corresponding to data to be fitted.

        :arg ye: array. Vector of y-errors corresponding to data to be fitted.

        :kwarg xe: array. Optional vector of x-errors corresponding to data to be fitted, setting to anything other than None toggles x-error considerations.

        :kwarg length_scale: float. Hyperparameter related to correlation length between points in profile, larger value makes profiles flatter.

        :kwarg regularization_parameter: float. Parameter adjusting penalty on kernel complexity, larger value makes profiles smoother.

        :kwarg epsilon: float. Convergence criterion on change in log-marginal-likelihood, relaxing this parameter speeds up optimization at cost of goodness-of-fit.

        :kwarg nrestarts: int. Number of kernel restarts, larger number improves robustness of algorithm at the cost of speed.

        :returns: none.
        """
        self._length_scale_initial = length_scale
        kernel = GPR1D.RQ_Kernel(1.0e0,self._length_scale_initial,3.0e1)
        kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,self._length_scale_initial * 0.1,1.0e1], \
                                              [1.0e1,self._length_scale_initial * 10.0,5.0e1]])
        optimizer_gain = 1.0e-1
        super(RationalQuadraticFGPR1D,self).__init__(kernel,x,y,ye,xe,kernel_hyppar_bounds,regularization_parameter,epsilon,nrestarts)

        # Overwrite the preset kernel optimizer settings
        self.set_search_parameters(epsilon=epsilon,method=5,spars=[optimizer_gain,0.4,0.8])

        # Define a zero derivative constraint at the magnetic axis
        self.set_raw_data(dxdata=[0.0],dydata=[0.0],dyerr=[0.0])

        # Overwrite the error kernel preset by the simplified GPR1D class
        error_kernel = GPR1D.RQ_Kernel(1.0e0,3.0e-1,2.0e1)
        error_kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,1.0e-1,1.0e1],[1.0e1,5.0e-1,3.0e1]])
        self.set_error_kernel(kernel=error_kernel,kbounds=error_kernel_hyppar_bounds,regpar=10.0,nrestarts=0)
        self.set_error_search_parameters(epsilon=1.0e-1,method=5,spars=[1.0e-1,0.4,0.8])


class GibbsInverseGaussianFGPR1D(GPR1D.SimplifiedGaussianProcessRegression1D):
    """
    Implements a GPR with a Gibbs kernel, augmented by
    an inverse Gaussian warping function, including
    heteroscedastic error fitting, ie. the error is
    allowed to vary in x. This kernel is best suited
    to density pedestal fitting, provided the peak
    location parameter is set approximately equal to
    the x-value of the sharpest gradient in the pedestal.

    Note that the peak location is NOT a hyperparameter,
    ie. the optimization routine does not change this
    value!

    Optimization of hyperparameters is only performed
    *once* using settings at the time of the *first*
    call! All subsequent calls use the results of the
    first optimization.
    """
    def __init__(self,x,y,ye,xe=None,length_scale=0.5,peak_width=0.1,peak_location=1.0,regularization_parameter=1.0,epsilon=1.0e-2,nrestarts=5):
        """
        Defines customized GaussianProcessRegression1D instance with
        a pre-defined Gibbs kernel with an inverse Gaussian warping
        function for the data fit and a simple rational quadratic
        kernel for the error fit. Input parameters reduced only to
        essentials and most crucial knobs for fine-tuning.

        :arg x: array. Vector of x-values corresponding to data to be fitted.

        :arg y: array. Vector of y-values corresponding to data to be fitted.

        :arg ye: array. Vector of y-errors corresponding to data to be fitted.

        :kwarg xe: array. Optional vector of x-errors corresponding to data to be fitted, setting to anything other than None toggles x-error considerations.

        :kwarg length_scale: float. Hyperparameter related to correlation length between points in profile, larger value makes profiles flatter.

        :kwarg peak_width: float. Hyperparameter related to minimum correlation length, smaller value captures pedestal better. A hard-coded limit of 0.8 * length_scale is present to provide stability.

        :kwarg peak_location: float. Parameter specifying the location of the minimum correlation length, recommended to set slightly outside the pedestal.

        :kwarg regularization_parameter: float. Parameter adjusting penalty on kernel complexity, larger value makes profiles smoother.

        :kwarg epsilon: float. Convergence criterion on change in log-marginal-likelihood, relaxing this parameter speeds up optimization at cost of goodness-of-fit.

        :kwarg nrestarts: int. Number of kernel restarts, larger number improves robustness of algorithm at the cost of speed.

        :returns: none.
        """
        self._length_scale_initial = length_scale
        self._peak_width_initial = peak_width
        self._peak_location = peak_location
        warpfunc = GPR1D.IG_WarpingFunction(self._length_scale_initial,self._length_scale_initial * 0.6,self._peak_width_initial,self._peak_location,0.8)
        kernel = GPR1D.Gibbs_Kernel(1.0e0,warpfunc)
        kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,self._length_scale_initial * 0.1,self._length_scale_initial * 0.6 * 0.8,self._peak_width_initial * 0.8], \
                                              [1.0e1,self._length_scale_initial * 10.0,self._length_scale_initial * 0.6 * 1.2,self._peak_width_initial * 1.2]])
        optimizer_gain = 1.0e-1
        super(GibbsInverseGaussianFGPR1D,self).__init__(kernel,x,y,ye,xe,kernel_hyppar_bounds,regularization_parameter,epsilon,nrestarts)

        # Overwrite the preset kernel optimizer settings
        self.set_search_parameters(epsilon=epsilon,method=5,spars=[optimizer_gain,0.4,0.8])

        # Define a zero derivative constraint at the magnetic axis
        self.set_raw_data(dxdata=[0.0],dydata=[0.0],dyerr=[0.0])

        # Overwrite the error kernel preset by the simplified GPR1D class
        error_kernel = GPR1D.RQ_Kernel(1.0e0,3.0e-1,2.0e1)
        error_kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,1.0e-1,1.0e1],[1.0e1,5.0e-1,3.0e1]])
        self.set_error_kernel(kernel=error_kernel,kbounds=error_kernel_hyppar_bounds,regpar=10.0,nrestarts=0)
        self.set_error_search_parameters(epsilon=1.0e-1,method=5,spars=[1.0e-1,0.4,0.8])


class Matern52FGPR1D(GPR1D.SimplifiedGaussianProcessRegression1D):
    """
    Implements a GPR with a Matern kernel with an order
    parameter of 5/2, including heteroscedastic error
    fitting, ie. the error is allowed to vary in x. This
    kernel retains the best feature resolution in
    general, and is best suited to temperature profiles.

    .. note:: This can suffer from extreme overfitting due
    to existence of many local minima in hyperparameter
    space. This means the selection of an appropriate
    initial length scale is more important with this
    kernel option.

    Optimization of hyperparameters is only performed
    *once* using settings at the time of the *first*
    call! All subsequent calls use the results of the
    first optimization.
    """
    def __init__(self,x,y,ye,xe=None,length_scale=1.0,regularization_parameter=1.0,epsilon=1.0e-2,nrestarts=5):
        """
        Defines customized GaussianProcessRegression1D instance with
        a pre-defined Matern half-integer kernel for the data fit
	and a simple rational quadratic kernel for the error fit.
	Input parameters reduced only to essentials and most crucial
        knobs for fine-tuning.

        :arg x: array. Vector of x-values corresponding to data to be fitted.

        :arg y: array. Vector of y-values corresponding to data to be fitted.

        :arg ye: array. Vector of y-errors corresponding to data to be fitted.

        :kwarg xe: array. Optional vector of x-errors corresponding to data to be fitted, setting to anything other than None toggles x-error considerations.

        :kwarg length_scale: float. Hyperparameter related to correlation length between points in profile, larger value makes profiles flatter.

        :kwarg regularization_parameter: float. Parameter adjusting penalty on kernel complexity, larger value makes profiles smoother.

        :kwarg epsilon: float. Convergence criterion on change in log-marginal-likelihood, relaxing this parameter speeds up optimization at cost of goodness-of-fit.

        :kwarg nrestarts: int. Number of kernel restarts, larger number improves robustness of algorithm at the cost of speed.

        :returns: none.
        """
        self._length_scale_initial = length_scale
        kernel = GPR1D.Matern_HI_Kernel(5.0e-1,self._length_scale_initial,2.5)
        kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,self._length_scale_initial * 0.8], \
                                              [1.0e0,self._length_scale_initial * 1.2]])
        optimizer_gain = 1.0e0
        super(Matern52FGPR1D,self).__init__(kernel,x,y,ye,xe,kernel_hyppar_bounds,regularization_parameter,epsilon,nrestarts)

        # Overwrite the preset kernel optimizer settings
        self.set_search_parameters(epsilon=epsilon,method=5,spars=[optimizer_gain,0.4,0.8])

        # Define a zero derivative constraint at the magnetic axis
        self.set_raw_data(dxdata=[0.0],dydata=[0.0],dyerr=[0.0])

        # Overwrite the error kernel preset by the simplified GPR1D class
        error_kernel = GPR1D.RQ_Kernel(1.0e0,3.0e-1,2.0e1)
        error_kernel_hyppar_bounds = np.atleast_2d([[1.0e-1,1.0e-1,1.0e1],[1.0e1,5.0e-1,3.0e1]])
        self.set_error_kernel(kernel=error_kernel,kbounds=error_kernel_hyppar_bounds,regpar=10.0,nrestarts=0)
        self.set_error_search_parameters(epsilon=1.0e-1,method=5,spars=[1.0e-1,0.4,0.8])
