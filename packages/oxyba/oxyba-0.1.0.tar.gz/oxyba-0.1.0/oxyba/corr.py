
def corr(x, axis=0):
    """
    Sample Correlation Matrix

    Parameters
    ----------
    x : ndarray
        data set
    axis : int, optional
        Variables as columns is the default (axis=0). If variables are in the rows use axis=1

    Returns
    -------
    r : ndarray
        Sample Correlation Matrix
    p : ndarray
        p-values
    """
    #load modules
    from scipy.stats import pearsonr
    import numpy as np
    #transpose if axis<>0
    if axis is not 0:
        x = x.T
    #read dimensions and allocate variables
    n,c = x.shape
    r = np.ones((c,c))
    p = np.zeros((c,c))
    #compute each (i,j)-th correlation
    for i in range(0,c):
        for j in range(i+1,c):
            r[i,j], p[i,j] = pearsonr(x[:,i], x[:,j])
            r[j,i] = r[i,j]
            p[j,i] = p[i,j]
    #done
    return r,p
