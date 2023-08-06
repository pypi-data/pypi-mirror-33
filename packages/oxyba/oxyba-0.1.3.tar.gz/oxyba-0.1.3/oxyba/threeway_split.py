
def threeway_split(*data, test_size=0.2, random_state=None, shuffle=True):
    #load modules
    import numpy as np
    
    #subfunction - enforce numpy arrays, variables as columns
    def to_colvec(dat):
        out = np.asarray(dat)
        if len(out.shape) == 1:
            out = out.reshape(out.shape[0],1)
        return out    
    
    # read *data=(x,y) or data=x
    if len(data) == 2:
        xonly = False
        x = to_colvec(data[0])
        y = to_colvec(data[1])
        #check number of observations
        if x.shape[0] != y.shape[0]:
            raise Exception('x and y have not the same number of observations')
    else:
        xonly = True
        x = to_colvec(data[0])

    #number of obs
    n = x.shape[0]
    
    #check number of observations
    if n < 3:
        raise Exception('only n<3 observations provided')
    
    #number of obs for the validation and test set each
    nv = 1 if test_size*n < 1.0 else round(test_size*n)
    
    #number of obs for the training set
    nt = n - 2*nv
    
    # use a generic row index variable for the splitting task
    idx = np.arange(0,n)
    
    #set initial random state
    if shuffle and random_state:
        np.random.seed(random_state)  
    #shuffle the index
    if shuffle:
        np.random.shuffle(idx)

    #output: x_train, x_valid, x_test, y_train, y_valid, y_test,
    if xonly:
        return x[idx[:nt],:], x[idx[nt:nt+nv],:], x[idx[-nv:],:]
    else:
        return x[idx[:nt],:], x[idx[nt:nt+nv],:], x[idx[-nv:],:], y[idx[:nt],:], y[idx[nt:nt+nv],:], y[idx[-nv:],:]
