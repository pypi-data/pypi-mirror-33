
def hist_corr_pval(r, pval, plim = 0.01, rlim = 0.4):
    #load modules
    import matplotlib.pyplot as plt
    import numpy as np
    
    #reshape
    if len(r.shape) == 2:
        idx = (np.tri(N=r.shape[0], k=-1) == 1);
        r = r[idx]
        pval = pval[idx]

    #indicies for the three groups
    i1 = (pval>=plim)
    i2 = (pval<plim) & (np.abs(r)>rlim)
    i3 = (pval<plim) & (np.abs(r)<=rlim)

    #plot paramters
    absmax = np.max(np.abs(r))
    b = (np.arange(0,21)/10-1) * absmax
    c = plt.get_cmap('tab10').colors; c=(c[1],c[8],c[7])

    #create plot
    fig,ax = plt.subplots()
    ax.hist((r[i1],r[i2],r[i3]), histtype='bar', stacked=True, bins=b, color=c);

    #legend, title, labels
    ax.legend(['p >= ' + str(plim), 
               'p < ' + str(plim) + ' and |r| > ' + str(rlim),
               'p < ' + str(plim) + ' and |r| <= ' + str(rlim)],
              loc=2, bbox_to_anchor=(1.04, 1.04) );
    ax.set_ylabel('frequency');
    ax.set_xlabel('correlation coefficient');

    #design grid
    ax.grid(color='darkgray', linestyle='-.')
    for edge, spine in ax.spines.items():
        spine.set_visible(False)
    
    #output figure/axes onbjects
    return fig, ax