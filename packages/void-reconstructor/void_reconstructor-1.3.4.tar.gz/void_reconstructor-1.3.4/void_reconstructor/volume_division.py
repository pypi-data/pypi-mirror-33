import numpy as np
from void_reconstructor import reconstruction as rec
import itertools as it
import time
from astropy.io import ascii
import pickle
from mpi4py import MPI

def volume_division(Reconstruction,Resolution, division_number,beta,starts_all,rank,N_lim=128**3, flag = False):
    i = 0
    R = Reconstruction
    starts_all_new = np.empty((0, 4))
    tx1 = time.clock()
    print('rank %d: Starting volume division' % (rank))
    print('rank %d: Shape of starts_all %r' % (rank,np.shape(starts_all)))

    for start in starts_all[:,0:3]:
        box_size = starts_all[i, 3]
        i = i+1
        #length_final = box_size * (beta ** (1.0 / 3.0) - 1) * 0.5
        length_final = box_size * (beta - 1) * 0.5
        stop = start + box_size
        X, ID, X_mirror = R.get_final_position(start - length_final, stop + length_final, Resolution=Resolution,
                                               mirror_length=length_final)


        N_part = len(X[:, 0]) + len(X_mirror[:, 0])
        if N_part > N_lim:
            print('N_part too big')
            starts_sub = np.empty((0, 3))
            #print box_size
            starts_sub = np.append(starts_sub,
                                   start + np.asarray(list(it.product(np.arange(0.0, box_size, box_size / 2.0), repeat=3))),
                                   axis=0)
            box_length = np.full((8, 1), box_size / 2.0)
            starts_sub = np.append(starts_sub, box_length, axis=1)
            starts_all_new = np.append(starts_all_new, starts_sub, axis=0)
            flag = True
        else:
            starts_sub = np.append(start, box_size)
            starts_sub = np.reshape(starts_sub, (1, 4))
            starts_all_new = np.append(starts_all_new, starts_sub, axis=0)

    if (flag == True):
        return volume_division(Reconstruction,Resolution, division_number,beta,starts_all_new,rank=rank,N_lim = N_lim ,flag=False)
    else:
        tx2 = time.clock()
        print('rank %d: Finished volume division, time needed: %r s' %(rank, tx2-tx1))
        return starts_all_new

