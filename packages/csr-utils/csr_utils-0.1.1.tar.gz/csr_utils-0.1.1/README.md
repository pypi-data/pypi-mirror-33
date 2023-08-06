# csr_utils

Scalable Operations for CSR matrices.

[![Build Status](https://travis-ci.org/narges-rzv/csr_utils.svg?branch=master)](https://travis-ci.org/narges-rzv/csr_utils)

Installation 
------------
For general users and if using conda etc.:

`pip install csr_utils` 


Without root access:

`pip install --user csr_utils`

Usage
-----

```
>>> import numpy as np
>>> from scipy.sparse import csr_matrix
>>> xcsr = csr_matrix(np.array([[1, 0], [3, 4], [2, 2]], dtype=float))

>>> import csr_utils
>>> xnorm, xmean, xstd, xixnormed = normalize_csr_matrix(xcsr)

```


Overview
--------
This package currently only has a fast and memory efficient implementation for normalizing nonzero values of a CSR array without un-sparsifying the function. This is useful step for machine learning on large matrices. Most algorithms work better with normalized input, in particular the commonly used [linear classification models in sklearn](http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). 

There will be more functions added as the need arises, including turning a csr array into cuda sparse array directly. Stay tuned. 

normalize_csr_matrix:
---------------------
- Normalizes a CSR matrix only based on non-zero values, without turning it into dense array. 
   - In the CSR matrix, rows correspond to samples, and columns correspond to features.
   - Normalization will be such that each column (feature)'s non-zero values will have mean of 0.0 and standard deviation of 1.0.
- Will return the scalable equivalent of x = x.toarray(); x[(x==0)] = np.nan; (x - np.nanmean(x, axis=0)) / np.nanstd(x, axis=0)
- We compute a faster and equivalent definition of standard deviation:
   - ```sigma = SquareRoot(ExpectedValue(|X - mean|^2)) # slow```
   - ```sigma = SquareRoot(ExpectedValue(X^2) - ExpectedValue(X)^2) # fast```
   - [For more info see the math](https://en.wikipedia.org/wiki/Standard_deviation#Definition_of_population_values)
- This function makes the following assumptions:
   - If we don't have any observations in a column i, mean_array[i] be set to 0.0, and std_array[i] will be set to 1.0.
   - If we have a single observation, or if standard deviation is 0.0 for a column, we only subtract the mean for that column.

- (Useful for normalizing test sets:) The function allows the normalization to be based on pre-specified mean and standard deviation arrays. 

- The function also allows only a given subset of features to be normalized.
        
Example
-------
```
>>> import numpy as np
>>> from scipy.sparse import csr_matrix
>>> x = csr_matrix(np.array([[1, 0], [3, 4], [2, 2]], dtype=float))
>>> x
<3x2 sparse matrix of type '<class 'numpy.float64'>'
    with 5 stored elements in Compressed Sparse Row format>
>>> print(x.toarray())
[[ 1.  0.]
 [ 3.  4.]
 [ 2.  2.]]
>>> xnorm, xmean, xstd, xixnormed = normalize_csr_matrix(x)
>>> a, amean, astd, aixnormed = csr_utils.normalize_csr_matrix(a)
print(xnorm.todense())
[[-1.22474487  0.        ]
 [ 1.22474487  1.        ]
 [ 0.         -1.        ]]
>>> xmean
array([ 2.,  3.])
>>> xstd
array([ 0.81649658,  1.        ])
>>> xixnormed
array([0, 1])
```
