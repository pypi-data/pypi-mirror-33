import pytest
import numpy as np
from copy import deepcopy
from edrgp.gp_model.regression import GaussianProcessRegressor
from edrgp.gp_model.regression import SparseGaussianProcessRegressor
from edrgp.edr import EffectiveDimensionalityReduction
from edrgp.base import BlockEDR
from edrgp.datasets import (get_gaussian_inputs,
                            get_tanh_targets,
                            get_edr_target,
                            get_beta_inputs)
from sklearn.feature_selection import mutual_info_regression
from sklearn.decomposition import PCA, SparsePCA
from sklearn.preprocessing import StandardScaler
from edrgp.utils import SVDTransformer
from edrgp.utils import discrepancy
from scipy.sparse import random as random_sparse
import GPy


def get_2d_data(mean=None):
    '''Returns a simple 2D dataset'''
    if mean is None:
        mean = [0, 0]
    X = get_gaussian_inputs(
        eig_values=[1, 0.3], sample_size=500,
        eig_vectors=np.array([[1, 1], [-1, 1]]),
        mean=mean)
    y = get_tanh_targets(X, [0.5, 0.5])
    return X, y


def test_sparse_regression():
    np.random.seed(101)
    N = 50
    noise_var = 0.05

    X = np.linspace(0, 10, 50)[:, None]
    k = GPy.kern.RBF(1)
    y = np.random.multivariate_normal(
        np.zeros(N), k.K(X)+np.eye(N)*np.sqrt(noise_var)).reshape(-1, 1)

    gp = GaussianProcessRegressor()
    gp.fit(X, y)

    sgp = SparseGaussianProcessRegressor(num_inducing=12)
    sgp.fit(X, y)

    assert abs(gp.estimator_.log_likelihood() -
               sgp.estimator_.log_likelihood()[0][0]) < 0.5


@pytest.mark.parametrize("mean", [[0, 0], [10, -10]])
def test_mi(mean):
    X, y = get_2d_data(mean)
    edr = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                           SVDTransformer(), n_components=1,
                                           normalize=True)
    edr.fit(X, y)
    mi = mutual_info_regression(edr.transform(X), y)[0]
    assert mi > 1


@pytest.mark.parametrize("normalize", [True, False])
def test_translation(normalize):
    X, y = get_2d_data(mean=[10, -10])
    edr = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                           SVDTransformer(), n_components=1,
                                           normalize=normalize)
    edr.fit(X, y)
    components_shift = edr.components_

    X -= X.mean(0)
    edr2 = deepcopy(edr)
    edr2.fit(X, y)
    components_no_shift = edr2.components_
    assert np.allclose(components_shift, components_no_shift, rtol=1e-3)


@pytest.mark.parametrize("mean", [[0, 0, 0, 0], [10, -10, 100, -100]])
def test_preprocess(mean):
    X = get_gaussian_inputs(
        eig_values=[1, 0.3, 0.001, 0.001], sample_size=500, mean=mean)
    y = get_tanh_targets(X, [0.5, 0.5, 0, 0])

    edr = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                           SVDTransformer(), n_components=1,
                                           normalize=True,
                                           preprocessor=PCA(n_components=2))
    edr.fit(X, y)
    components_shift = edr.components_

    X -= X.mean(0)
    edr = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                           SVDTransformer(), n_components=1,
                                           normalize=True,
                                           preprocessor=PCA(n_components=2))
    edr.fit(X, y)
    components_no_shift = edr.components_
    assert np.allclose(components_shift, components_no_shift, rtol=1e-3)


@pytest.mark.parametrize("mean", [[0, 0], [10, -10]])
def test_scaling(mean):
    X, y = get_2d_data(mean)
    # EDR with scaling
    edr_sc = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                              SVDTransformer(), normalize=True)
    edr_sc.fit(X, y)
    x1 = edr_sc.transform(X-np.mean(X, axis=0))
    # EDR without scaling
    edr = EffectiveDimensionalityReduction(GaussianProcessRegressor(),
                                           SVDTransformer(), normalize=False)
    X_scaled = StandardScaler().fit_transform(X)
    x2 = edr.fit_transform(X_scaled, y)

    assert np.allclose(x1, x2)


# @pytest.mark.parametrize("n_components,step", [(3, 1), (None, 0.99)])
# def test_iterative(n_components, step):
#     X = get_beta_inputs(300, 10)
#     B = np.linalg.qr(random_sparse(10, 3, density=0.3, random_state=0).A)[0]
#     y = get_edr_target(X.dot(B), 0.1)

#     gp_model = GaussianProcessRegressor(['RBF'], [{'ARD': True}])
#     edr = EffectiveDimensionalityReduction(gp_model,
#                                            SVDTransformer(),
#                                            n_components=n_components,
#                                            step=step, normalize=False)
#     edr.fit(X, y)
#     assert discrepancy(B, edr.components_.T) < 1e-1
#     assert edr.components_.shape[0] == 3
#     assert np.all(edr.subspace_variance_ratio_ == np.sort(edr.subspace_variance_ratio_)[::-1])


# @pytest.mark.parametrize("normalize,preprocessor",
#                          [(False, None),
#                           (True, None),
#                           (True, PCA(n_components=5))])
# def test_get_gradients_and_transform(normalize, preprocessor):
#     X = get_beta_inputs(300, 10)
#     B = np.linalg.qr(random_sparse(10, 3, density=0.3, random_state=0).A)[0]
#     y = get_edr_target(X.dot(B), 0.1)

#     gp_model = GaussianProcessRegressor(['RBF'], [{'ARD': True}])
#     edr = EffectiveDimensionalityReduction(gp_model,
#                                            SVDTransformer(),
#                                            step=2,
#                                            n_components=3,
#                                            normalize=normalize,
#                                            preprocessor=preprocessor)
#     edr.fit(X, y)
#     X_transform = edr.transform(X)
#     grads = edr.get_estimator_gradients(X)
#     assert grads.shape == X.shape
#     assert X_transform.shape == (300, 3)


# @pytest.mark.parametrize("normalize,preprocessor",
#                          [(False, None),
#                           (True, None),
#                           (True, PCA(n_components=5))])
# def test_refit(normalize, preprocessor):
#     X = get_beta_inputs(300, 10)
#     B = np.linalg.qr(random_sparse(10, 3, density=0.3, random_state=0).A)[0]
#     y = get_edr_target(X.dot(B), 0.1)

#     gp_model = GaussianProcessRegressor(['RBF'], [{'ARD': True}])
#     edr = EffectiveDimensionalityReduction(gp_model,
#                                            SVDTransformer(),
#                                            step=0.99,
#                                            normalize=normalize,
#                                            preprocessor=preprocessor)
#     edr.fit(X, y)
#     edr.refit(SparsePCA(n_components=3))
#     X_transform_refited = edr.transform(X, refitted=True)
#     assert X_transform_refited.shape == (300, 3)

# def test_block():
#     X = get_beta_inputs(300, 10)
#     B = np.linalg.qr(random_sparse(10, 3, density=0.4, random_state=0).A)[0]
#     B[:5, :2] = 0
#     B[5:, 2:] = 0
#     y = get_edr_target(X.dot(B), 0.1)

#     gp_model = GaussianProcessRegressor(['RBF'], [{'ARD': True}])
#     edr = BlockEDR(gp_model,
#                    SVDTransformer(),
#                    n_components=[2, 2], blocks=[range(5), range(5, 10)])
#     edr.fit(X, y)
#     X_transform = edr.transform(X)
#     edr.refit(SparsePCA(n_components=3))
#     X_transform_refited = edr.transform(X, refitted=True)
#     assert X_transform_refited.shape == (300, 3)
#     assert X_transform.shape == (300, 4)
#     assert np.all(edr.components_.T[5:, :2] == 0)
#     assert np.all(edr.components_.T[:5, 2:4] == 0)

# @pytest.mark.parametrize("normalize,preprocessor",
#                          [(False, None),
#                           (True, None),
#                           (True, PCA(n_components=5))])
# def test_block_preprocessing(normalize, preprocessor):
#     X = get_beta_inputs(300, 10)
#     B = np.linalg.qr(random_sparse(10, 3, density=0.4, random_state=0).A)[0]
#     B[:5, :2] = 0
#     B[5:, 2:] = 0
#     y = get_edr_target(X.dot(B), 0.1)

#     gp_model = GaussianProcessRegressor(['RBF'], [{'ARD': True}])
#     edr = EffectiveDimensionalityReduction(gp_model,
#                                            SVDTransformer(),
#                                            blocks=None,
#                                            n_components=[2, 2],
#                                            normalize=normalize,
#                                            preprocessor=preprocessor)
#     edr.fit(X, y)
#     X_transform = edr.transform(X)
#     grads = edr.get_estimator_gradients(X)
#     assert grads.shape == X.shape
#     assert X_transform.shape == (300, 4)

