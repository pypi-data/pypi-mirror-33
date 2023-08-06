import numpy as np

# Replicates first output (i.e. Lia) of MATLAB's ismember(A,B)
# Inputs A and B should be numpy arrays
def ismember(A,B):
    return np.logical_or.reduce([A == Bi for Bi in B])
