import pytest
import csr_utils

def test_csr_utils_import():
    x = csr_utils.csr_matrix(csr_utils.np.array([[1, 0], [3, 0], [2, 2]], dtype=float))
    assert len(x.shape) == 2
    assert x.shape == (3,2)

def test_csr_utils_normed_single_observation():
    x = csr_utils.csr_matrix(csr_utils.np.array([[1, 0], [3, 0], [2, 2]], dtype=float))
    xnorm, xmean, xstd, xixnormed = csr_utils.normalize_csr_matrix(x)
    assert csr_utils.np.all(xmean == csr_utils.np.array([2., 2.]))
    assert csr_utils.np.all(csr_utils.np.isclose(xstd, csr_utils.np.array([0.81649,  1. ]), 1e-4))
    assert len(xixnormed) == 1

def test_csr_utils_normed_mult_observation_1():
    x = csr_utils.csr_matrix(csr_utils.np.array([[1, 0], [3, 4], [2, 2]], dtype=float))
    xnorm, xmean, xstd, xixnormed = csr_utils.normalize_csr_matrix(x)
    assert csr_utils.np.all(xmean == csr_utils.np.array([2., 3.]))
    assert csr_utils.np.all(csr_utils.np.isclose(xstd, csr_utils.np.array([0.81649,  1. ]), 1e-4))
    assert len(xixnormed) == 2

def test_csr_utils_normed_mult_observation_2():
    x = csr_utils.csr_matrix(csr_utils.np.array([[1, 0], [3, 4], [2, 8]], dtype=float))
    xnorm, xmean, xstd, xixnormed = csr_utils.normalize_csr_matrix(x)
    assert csr_utils.np.all(xmean == csr_utils.np.array([ 2.,  6.]))
    assert csr_utils.np.all(csr_utils.np.isclose(xstd, csr_utils.np.array([0.81649,  2. ]), 1e-4))
    assert len(xixnormed) == 2


