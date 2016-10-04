from ..generic import Generic, Base_Generic
from ...utils import se_covariance, sma_covariance
from ... import verify
import numpy as np

class Base_SMASE(Base_Generic):
    def __init__(self, Y, X, W, M, Delta,
                 n_samples=1000, n_jobs=1,
                 extra_traced_params = None,
                 priors=None,
                 starting_values=None):
        super(Base_SMASE, self).__init__(Y, X, W, M, Delta,
                                        n_samples=0, n_jobs=n_jobs,
                                        extra_traced_params=extra_traced_params,
                                        priors=priors,
                                        starting_values=starting_values)
        st = self.state
        self.state.Psi_1 = sma_covariance
        self.state.Psi_2 = se_covariance

        st.Rho_min, st.Rho_max = -st.Rho_max, -st.Rho_min
        try:
            self.sample(n_samples, n_jobs=n_jobs)
        except (np.linalg.LinAlgError, ValueError) as e:
            warn('Encountered the following LinAlgError. '
                 'Model will return for debugging purposes. \n {}'.format(e))

class SMASE(Base_SMASE):
    def __init__(self, Y, X, W, M, Z=None, Delta=None, membership=None,
                 #data options
                 transform ='r', verbose=False,
                 n_samples=1000, n_jobs=1,
                 extra_traced_params = None,
                 priors=None,
                 starting_values=None):
        W,M = verify.weights(W, M, transform=transform)
        self.M = M
        
        Y,X = verify.center_and_scale(Y,X)

        N,_ = X.shape
        J = M.n
        Mmat = M.sparse
        Wmat = W.sparse

        Delta, membership = verify.Delta_members(Delta, membership, N, J)

        X = verify.covariates(X)

        self._verbose = verbose
        if Z is not None:
            Z, = verify.center_and_scale(Z)
            Z = Delta.dot(Z)
            X = np.hstack((X,Z))
        super(SMASE, self).__init__(Y, X, Wmat, Mmat, Delta,
                                   n_samples=n_samples,
                                   n_jobs = n_jobs,
                                   extra_traced_params=extra_traced_params,
                                   priors=priors,
                                   starting_values=starting_values)
