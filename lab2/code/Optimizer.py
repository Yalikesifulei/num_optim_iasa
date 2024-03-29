import itertools
import numpy as np


class NewtonOptimizer:
    def __init__(self, beta=1, lmb=None, tol=1e-5, max_iter=100):
        """
        Parameteres
        -----------
        beta      : float
                    initial step (default 1)
        lmb       : float or None
                    step decay parameter
                    if None - classic Newton method is used instead
        max_iter  : int
                    maximum number of iterations,
                    default is 100
        tol       : tolerance for algorithm stopping
                    |f(x_prev) - f(x_new)| < tol
        """
        self.beta = beta
        self.tol = tol
        self.max_iter = int(max_iter)
        self.lmb = lmb

    def minimize(self, target_func, x0, h=0.005):
        """
        Parameteres
        -----------
        target_func : callable
                      function to minimize
        x0          : np.array of shape (n, )
                      initial point
        h           : step for computing gradients,
                      default is 0.005
        -----------
        Returns history - np.array with shape (n_iter, n+1),
                          n - number of variables;
                history[:, -1] - values of target functions
                history[-1, :-1] - solution
                history[-1, -1] - value of target function at solution point
        """
        def compute_grad(target_func, x, h):
            n = len(x)
            grad = np.zeros_like(x)
            for i in range(n):
                x_plus = np.copy(x)
                x_plus[i] += h
                x_minus = np.copy(x)
                x_minus[i] -= h
                grad[i] = (target_func(x_plus) - target_func(x_minus))/(2*h)
            return grad

        def compute_hessian(target_func, x, h):
            n = len(x)
            hessian = np.empty((n, n))
            for k in range(n):
                for m in range(k+1):
                    dx = np.zeros_like(x)
                    dx[k] = h/2
                    dy = np.zeros_like(x)
                    dy[m] = h/2
                    # k=m:  (f(x+2h) - 2f(x) + f(x-2h)) / 4h^2
                    # k!=m: (f(x+h,y+h) - f(x+h,y-h) - f(x-h,y+h) + f(x-h,y-h))
                    # / 4h^2
                    hessian[k, m] = sum([i*j * target_func(x + i*dx + j*dy)
                                        for i, j in itertools.product([1, -1],
                                                                      repeat=2)
                                         ]) / h**2
                    hessian[m, k] = hessian[k, m]
            return hessian

        history = []
        x = np.copy(x0)
        history.append([*x0, target_func(x0)])
        for k in range(self.max_iter):
            grad = compute_grad(target_func, x, h)
            hessian = compute_hessian(target_func, x, h)
            step = np.linalg.pinv(hessian) @ grad

            
            alpha = self.beta
            if self.lmb is not None:
                while target_func(x - alpha*step) > target_func(x):  # > !!!
                    alpha = alpha * self.lmb
                    
            x = x - alpha * step
            history.append([*x, target_func(x)])
            if k > 0 and np.abs(history[-1][1] - history[-2][1]) < self.tol:
                break
        return np.array(history)
