import numpy as np
from scipy.sparse import csr_matrix

def normalize_csr_matrix(x, meanarr=None, stdarr=None, ixnormed=None, threshold_to_clip=2000, verbose=True):
    """ Normalizes a CSR matrix only based on non-zero values, without turning it into dense array.
        In the CSR matrix, rows correspond to samples, and columns correspond to features.
        Normalization will be such that each column (feature)'s non-zero values will have mean of 0.0 and standard deviation of 1.0.

        Tips: Useful for machine learning - most algorithms need normalized input
        Will return the scalable equivalent of x = x.toarray(); x[(x==0)] = np.nan; (x - np.nanmean(x, axis=0)) / np.nanstd(x, axis=0)

        We compute a faster and equivalent definition of standard deviation:
            sigma = SquareRoot(ExpectedValue(|X - mean|^2)) # slow
            sigma = SquareRoot(ExpectedValue(X^2) - ExpectedValue(X)^2) # fast
            (https://en.wikipedia.org/wiki/Standard_deviation#Definition_of_population_values)

        Assumptions:
        - If we don't have any observations in a column i, mean_array[i] be set to 0.0, and std_array[i] will be set to 1.0.
        - If we have a single observation, or if standard deviation is 0.0 for a column, we only subtract the mean for that column.


        The function allows the normalization to be based on pre-specified mean and standard deviation arrays.
        The function also allows only a given subset of features to be normalized.

        Parameters
        ----------
        x : csr_matrix (scipy.sparse.csr_matrix)
            The CSR matrix to normalize. x should have shape N x D where N is number of samples and D is number of features.

        meanarr : array_like (np.array), or None
            If not None, meanarr needs to be one dimensional and of shape D
            Default is None.
            - If None, the mean array will be computed according to the non-zero values of the CSR input x, and will be returned.
               (Useful when normalizing 'training set'. Pickle this mean array for future use.)
            - If not None, normalization will be done according to this mean array rather than a computed mean array.
               (Useful when normalizing 'test set')

        stdarr : array_like (np.array), or None
            If not None, stdarr needs to be one dimensional and of shape D
            Default is None.
            - If None, the std array will be computed according to the non-zero values of the CSR input x, and will be returned.
               (Useful when normalizing 'training set'. Pickle this std array for future use.)
            - If not None, normalization will be done according to this std array rather than a computed mean array.
               (Useful when normalizing 'test set').

        ixnormed : array_like (np.array), or None
            Indicated which columns of the CSR should be normalized at all.
            Only relevant if stdarr and meanarr are both not None.
            If None, all columns will be normalized.
            If not None, only the ixnormed subset of the columns will be normalized.

        threshold_to_clip: scalar number either float or int.
            If standard deviation of each column is above this value, we won't normalize that column.
            Set to np.inf, if you don't desire th is functionality.

        verbose: bool (Default: True)
            If True, print status while normalizing.


        Returns
        -------
        xnorm : csr_matrix (scipy.sparse.csr_matrix)
            Normalized csr array of nonzero values of x.
            xnorm has shape N x D where N is number of samples and D is number of features.
            Normalization will be such that each column (feature)'s non-zero values will have mean of 0.0 and standard deviation of 1.0.
            xnorm is scalable equivalent of x = x.todense(); x[(x==0)] = np.nan; (x - np.nanmean(x, axis=0)) / np.nanstd(x, axis=0)
            Only ix_done_normalized columns are normalized (i.e. columns where standard deviation is not zero.)

        mean_array : array_like (np.array)
            mean_array is one dimensional and of shape D
            The mean_array[i] is the mean value of nonzero values of column i in input x.

        std_array : array_like (np.array)
            std_array is one dimensional and of shape D
            The std_array[i] is the standard deviation value of nonzero values of column i in input x.

        ix_done_normalized : array_like (np.array)
            ix_done_normalized is one dimensional array of size K <= D,
            and contains the index of columns that were normalized afterall.
            (If a column has standard deviation of zero or standard deviation above threshold_to_clip, it is NOT normalized.)

        Example
        -------
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

    """
    xnorm = x.copy()

    if meanarr is None and stdarr is None:
        nnz_cnt_denominator = np.array((x != 0).sum(axis=0)).ravel()
        nnz_columns_ix_cnt_zro = (nnz_cnt_denominator == 0).ravel() # these are columns that have no non-zero values.
        nnz_cnt_denominator[nnz_columns_ix_cnt_zro] = 1.0 # setting these columns to 1.0 to turn 0/0 into 0/1 (and get 0)
        nnz_mean_sum = np.array(x.sum(axis=0)).ravel()
        mean_array = nnz_mean_sum/nnz_cnt_denominator

        nnz_std_sum_sqr = np.array((x.multiply(x)).sum(axis=0)).ravel() # sum of squares of nonzero values of csr X[:,i]
        std_array = np.sqrt((nnz_std_sum_sqr/nnz_cnt_denominator) - (mean_array ** 2))
        ix_to_normalize_std = (std_array != 0) & (std_array < threshold_to_clip)
        ix_to_not_normalize_std = (ix_to_normalize_std == False ).nonzero()[0].ravel()
        std_array[ix_to_not_normalize_std] = 1.0
        ix_to_normalize = ix_to_normalize_std

        if ixnormed is not None:
            ixnormed_inverse = (ixnormed == False)
            mean_array[ixnormed_inverse] = 0.0
            std_array[ixnormed_inverse] = 1.0
            ix_to_normalize[ixnormed_inverse] = False
    else:
        if verbose:
            print('mean and sd already specified. normalizing with given mean/sd.')
            if meanarr is None or stdarr is None:
                raise ValueError('Both meanarr and stdarr are required, if you want to normalized based on pre-computed values. Aborting.')

        mean_array = meanarr
        std_array = stdarr
        if ixnormed is not None:
            ix_to_normalize = np.zeros((std_array.shape), dtype=bool)
            ix_to_normalize[ixnormed] = True
        else:
            ix_to_normalize = np.ones((std_array.shape), dtype=bool)

    # normalize the nonzero values: Note that we won't eliminate_zeros() here to keep the values that were equal to the mean available for next steps.
    xnorm.data = (xnorm.data - mean_array[xnorm.indices])/std_array[xnorm.indices]
    ix_done_normalized = ix_to_normalize.nonzero()[0].ravel()

    return xnorm, mean_array, std_array, ix_done_normalized
