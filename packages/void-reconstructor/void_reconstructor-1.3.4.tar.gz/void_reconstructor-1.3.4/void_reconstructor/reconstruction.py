#!/usr/bin/env python
import numpy as np
from scipy import spatial
import scipy
import time
import copy
import lapjv as lapjv
import itertools as it
from numpy import random
import copy
from astropy.cosmology import FlatLambdaCDM

def calculate_mass_discr(masses, m):
    masses = np.asarray(masses)
    return (masses/m).astype(int)+1

def new_sum(n):
    res = 0
    i = 0
    for n_i in n:
        res = res + n_i
        i = i + 1
    return res
def convert_discr_masses(n, mass, X, V,ID,mass_0):
    length = new_sum(n)
    mass_return = np.zeros(length)
    X_return = np.zeros((length,3))
    V_return = np.zeros((length,3))
    ID_return = np.zeros(length)
    i = 0
    k = 0
    for n_i in n:
        for j in range(0,n_i):
            mass_return[k] = mass_0
            X_return[k] = X[i]
            V_return[k] = V[i]
            ID_return[k] = ID[i]
            k = k+1
        i = i+1
    return (mass_return, X_return, V_return, ID_return)

def create_haloes(mass,X,V,ID,length):
    mass_return = np.zeros(length)
    X_return = np.zeros((length,3))
    V_return = np.zeros((length,3))
    ID_return = np.zeros(length)
    mass = np.asarray(mass)
    X = np.asarray(X)
    V = np.asarray(V)
    ID = np.asarray(ID)
    i = 0
    for ID_i in ID:
        indices = np.where(ID==ID_i)
        mass_return[i] = mass[indices].sum()
        X_return[i] = X[indices[0]] #we only need the first one, as all are identical
        V_return[i] = V[indices].mean()
        ID_return[i] = ID_i
    return (mass_return,X_return,V_return,ID_return)


def pad_matrix(matrix, pad_value=0):
    shape_matrix = np.shape(matrix)
    #print('size of matrix in bytes', sys.getsizeof(matrix))
    dim_0 = shape_matrix[0]
    dim_1 = shape_matrix[1]
    #print('dim_0 :', dim_0)
    #print('dim_1 :', dim_1)
    if dim_0 > dim_1:
        N = dim_0 - dim_1
        matrix_return = np.pad(matrix, ((0, 0), (0, N)), mode='constant', constant_values=pad_value)
    elif dim_1 > dim_0:
        N = dim_1 - dim_0
        matrix_return = np.pad(matrix, ((0, N), (0, 0)), mode='constant', constant_values=pad_value)
    else:
        matrix_return = matrix
    #print('size of cost matrix', sys.getsizeof(matrix_return))
    return matrix_return


def get_xyz_C(cosmo, z, ra, dec):
    deg2rad = math.pi / 180.
    dcv = cosmo.comoving_distance(z).value
    x = dcv * np.cos(dec * deg2rad) * np.cos(ra * deg2rad)
    y = dcv * np.cos(dec * deg2rad) * np.sin(ra * deg2rad)
    z = dcv * np.sin(dec * deg2rad)

    return x, y, z

class Reconstructor:
    'Class that contains the methods to reconstruct position and velocities from a pNbody simulation'

    def __init__(self, X,ID,mass,z_r = 0, RA = 0, DEC = 0,particle_mass = None, V = None, periodic_condition = True, H0=67.77, Omega0=0.307115):
        #Setting up the Cosmology#
        self.H0 = H0 #Hubble parameter
        self.Omega0 = Omega0
        self.cosmo = FlatLambdaCDM(H0=self.H0, Om0=self.Omega0)




        if particle_mass == None:
            self.pos = X
            self.mass = mass
            self.ID = ID
            self.V = None #Bad implementation... (change this later)
            self.periodic_condition = periodic_condition
        else:
            n = calculate_mass_discr(mass,particle_mass)
            (mass,X,V,ID) = convert_discr_masses(n,mass,X,V,ID,particle_mass)
            self.pos = X
            self.mass = mass
            self.ID = ID
            self.V = V
            self.periodic_condition = periodic_condition

        self.z_r = z_r
        self.RA = RA
        self.DEC = DEC


    @staticmethod
    def get_grid(start=[], stop=[], Resolution=8):
        # create a 3d initial homogeneous grid
        # start and fin are arrays that determine the starting position and the final position in each direction [x,y,z]
        step = [(stop[0] - start[0]) / float(Resolution), (stop[1] - start[1]) / float(Resolution),
                (stop[2] - start[2]) / float(Resolution)]
        x_init = np.arange(start[0], stop[0], step[0]) + 0.5 * step[0]  # Add 0.5*step to have the points in the middle
        y_init = np.arange(start[1], stop[1], step[1]) + 0.5 * step[1]
        z_init = np.arange(start[2], stop[2], step[2]) + 0.5 * step[2]
        x_mesh, y_mesh, z_mesh = np.meshgrid(x_init, y_init, z_init)
        x_mesh = np.ravel(x_mesh).astype(np.float32)
        y_mesh = np.ravel(y_mesh).astype(np.float32)
        z_mesh = np.ravel(z_mesh).astype(np.float32)
        Q = np.array([x_mesh, y_mesh, z_mesh]).transpose()
        return Q

    @staticmethod
    def get_rectangular_grid(npart, start=[], stop=[], rank=0):
        lenx = abs(stop[0] - start[0])
        leny = abs(stop[1] - start[1])
        lenz = abs(stop[2] - start[2])

        nz = int((npart * lenz * lenz / (lenx * leny)) ** (1.0 / 3.0))
        nx = int(nz * lenx / lenz)
        ny = int(nz * leny / lenz)
        s1 = nx * ny * nz
        s2 = (nx + 1) * ny * nz
        s3 = nx * (ny + 1) * nz
        s4 = nx * ny * (nz + 1)
        s5 = (nx + 1) * (ny + 1) * nz
        s6 = nx * (ny + 1) * (nz + 1)
        s7 = (nx + 1) * ny * (nz + 1)
        s8 = (nx + 1) * (ny + 1) * (nz + 1)
        if s8 < npart:
            nx = nx + 1
            ny = ny + 1
            nz = nz + 1

            s1 = nx * ny * nz
            s2 = (nx + 1) * ny * nz
            s3 = nx * (ny + 1) * nz
            s4 = nx * ny * (nz + 1)
            s5 = (nx + 1) * (ny + 1) * nz
            s6 = nx * (ny + 1) * (nz + 1)
            s7 = (nx + 1) * ny * (nz + 1)
            s8 = (nx + 1) * (ny + 1) * (nz + 1)

        all_s = np.array([s1, s2, s3, s4, s5, s6, s7, s8])
        all_s_ind = np.where(all_s >= npart)[0]
        all_s = all_s[all_s_ind]
        min_s = np.min(all_s)
        if (min_s == s2):
            nx = nx + 1
        elif (min_s == s3):
            ny = ny + 1
        elif (min_s == s4):
            nz = nz + 1
        elif (min_s == s5):
            nx = nx + 1
            ny = ny + 1
        elif (min_s == s6):
            ny = ny + 1
            nz = nz + 1
        elif (min_s == s7):
            nx = nx + 1
            nz = nz + 1
        elif (min_s == s8):
            print('ULTIMATE DECREASING NECESSARY')
            nx = nx + 1
            ny = ny + 1
            nz = nz + 1

        '''
        while nx*ny*nz<npart:
            print('DECREASING HOMOGENEOUS GRID SIZE')
            print(start[1])
            print(stop[1])
            print(npart)
            print(lenx,leny,lenz)
            print((nx,ny,nz))
            nx = nx+1
            ny = ny+1
            nz = nz+1

        '''
        n_max = max(nx, ny, nz)
        # nx,ny,nz = n_max, n_max, n_max

        print('Rank %d: (nx,ny,nz) : %r' % (rank, (nx, ny, nz)))
        step = [abs((stop[0] - start[0])) / nx, abs((stop[1] - start[1])) / ny, abs((stop[2] - start[2])) / nz]
        x_init = np.linspace(start[0] - 0.0 * step[0], stop[0] + 0.0 * step[0], nx + 0) + 0.5 * step[0]
        y_init = np.linspace(start[1] - 0.0 * step[1], stop[1] + 0.0 * step[1], ny + 0) + 0.5 * step[1]
        z_init = np.linspace(start[2] - 0.0 * step[2], stop[2] + 0.0 * step[2], nz + 0) + 0.5 * step[2]
        x_init = np.linspace(start[0] - 0.0 * step[0], stop[0] + 0.0 * step[0], nx + 0) + 0.0 * step[0]
        y_init = np.linspace(start[1] - 0.0 * step[1], stop[1] + 0.0 * step[1], ny + 0) + 0.0 * step[1]
        z_init = np.linspace(start[2] - 0.0 * step[2], stop[2] + 0.0 * step[2], nz + 0) + 0.0 * step[2]
        x_mesh, y_mesh, z_mesh = np.meshgrid(x_init, y_init, z_init)
        x_mesh = np.ravel(x_mesh).astype(np.float32)
        y_mesh = np.ravel(y_mesh).astype(np.float32)
        z_mesh = np.ravel(z_mesh).astype(np.float32)
        Q = np.array([x_mesh, y_mesh, z_mesh]).transpose()
        hom_print = np.array(
            [np.min(Q[:, 0]), np.max(Q[:, 0]), np.min(Q[:, 1]), np.min(Q[:, 1]), np.min(Q[:, 2]), np.min(Q[:, 2])])
        len_print = np.array([lenx, leny, lenz])
        print('Rank %d: (homogeneous grid, min and max) : %r' % (rank, hom_print))
        print('Rank %d: (homogeneous grid, lengths) : %r' % (rank, len_print))

        return Q




    def get_mass(self, Resolution=8, seed=1):
        mass_tot = self.mass
        high = size(mass_tot)
        N = Resolution ** 3
        np.random.seed(seed)
        iran = np.random.randint(0, high, size=N)
        return mass_tot[iran]

    def get_final_position(self, start=[0, 0, 0], stop=[100, 100, 100], Resolution=8, mirror_length=0,seed=1,box_size_total=100.0, z_min=0.0, z_max=0.0):
        # Returns the position array [x,y,z] for Resolution**3.0 randomly selected particles
        x = self.pos[:, 0]
        y = self.pos[:, 1]
        z = self.pos[:, 2]
        ID = self.ID
        redshift = self.z_r
        X = np.array([x, y, z]).transpose()
        high = np.size(x)
        N = Resolution ** 3
        np.random.seed(seed)
        #iran = np.random.randint(0, high, size = N)
        iran = np.random.choice(np.arange(0, high), size=min(N,high),replace=False)
        X = X[iran, :]
        ID = ID[iran]
        redshift = redshift[iran]

        if z_max != 0:
            redshift_ind = np.where(np.logical_and(redshift >= z_min, redshift < z_max))[0]
            X = X[redshift_ind,:]
            ID = ID[redshift_ind]

        selection_ind = np.where(np.logical_and(X[:, 2] >= start[2], np.logical_and(X[:, 2] <= stop[2],
                                                                                   np.logical_and(X[:, 1] >= start[1],
                                                                                                  np.logical_and(
                                                                                                      X[:, 1] <= stop[1],
                                                                                                      np.logical_and(
                                                                                                          X[:, 0] >=
                                                                                                          start[0],
                                                                                                          X[:, 0] <=
                                                                                                          stop[
                                                                                                              0]))))))  # Determines the indices where thee particle position is in given box
        selection_ind = selection_ind[0]  # Because there is an additional, useless dimension...
        if self.periodic_condition == True:
            X_mirror = self.mirror_positions(X, mirror_length=mirror_length, box_size=box_size_total)
            start_mirror = np.asarray(start)
            stop_mirror = np.asarray(stop)
            selection_ind_mirror = np.where(np.logical_and(X_mirror[:, 2] >= start_mirror[2], np.logical_and(X_mirror[:, 2] <= stop_mirror[2],
                                                                                       np.logical_and(X_mirror[:, 1] >= start_mirror[1],
                                                                                                      np.logical_and(
                                                                                                          X_mirror[:, 1] <= stop_mirror[1],
                                                                                                          np.logical_and(
                                                                                                              X_mirror[:, 0] >=
                                                                                                              start_mirror[0],
                                                                                                              X_mirror[:, 0] <=
                                                                                                              stop_mirror[
                                                                                                                  0]))))))
            selection_ind_mirror = selection_ind_mirror[0]
            return X[selection_ind, :], ID[selection_ind], X_mirror[selection_ind_mirror, :]
        else:
            X_mirror = np.empty((0, 3))
            return X[selection_ind, :], ID[selection_ind], X_mirror
        # return [x,y,z,ID], the ID is returned to be able to extract the corresponding particles from the simulation



    @staticmethod
    def get_costMatrix(X_fin, X_init, padding=False, val=0):
        # Calculates the costmatrix
        # If padding is true, the rectangular matrix is padded with values val
        cost = (spatial.distance.cdist(X_fin, X_init)) ** 2
        cost = cost.astype(dtype=np.float32)
        #high_ind = np.where(cost>1000)
        #cost[high_ind] = float('NaN')
        if not padding:
            return cost
        else:
            return pad_matrix(cost, val)

    def reconstruct_positions(self, X_final, X_init,N_particles = None,rank=0):
        #N_particles allows to cut the final particles that are reconstructed (necessary for mirror particles)
        print('Rank %d: Starting reconstruction' %rank)
        print('Rank %d: Shape of X_final : %s' %(rank,str(np.shape(X_final))))
        print('Rank %d: Shape of X_init (homogeneous grid) : %s' %(rank, str(np.shape(X_init))))
        t0 = time.clock()
        # This calls the hungarian algorithm to reconstruct the positions
        # hung.lap(a)[0] are the assignments for the rows,e.g. row_assigns[0] is the column index of the first row.
        cost = self.get_costMatrix(X_final, X_init, padding=True, val=0)
        # print 'size in GB of cost matrix :', cost.nbytes*10**(-9)
        # print 'type of cost matrix :', cost.dtype
        if N_particles == None:
            N_particles = len(X_final[:,0])
        row_assigns = lapjv.lapjv(cost)[0]
        x_r = []
        y_r = []
        z_r = []
        for j in np.arange(0,N_particles):
            i = row_assigns[j]
            x_r.append(X_init[i, 0])
            y_r.append(X_init[i, 1])
            z_r.append(X_init[i, 2])
        X_r = np.array([x_r, y_r, z_r]).transpose()
        del cost
        t1 = time.clock()
        print("Rank %d: time needed for reconstruction: %rs." %(rank,round(t1-t0,2)))
        # returns [Reconstructed] positions
        return X_r

    @staticmethod
    #f_Omega = 0.51408803537639658
    def get_velocity_L(X_final, X_init, f_Omega=0.514, h=1.0):
        # Calcualtes the lagrangian velocity from the inital and final velocity
        # f_Omega is a parameter
        # h is the dimensionless Hubble scale
        j = 0
        H = 100 * h
        vx = []
        vy = []
        vz = []
        for x_f in X_final:
            vx.append(-f_Omega * H * (X_init[j, 0] - x_f[0])) # Minus sign has to be verified!!
            vy.append(-f_Omega * H * (X_init[j, 1] - x_f[1]))
            vz.append(-f_Omega * H * (X_init[j, 2] - x_f[2]))
            j = j + 1
        V = np.array([vx, vy, vz]).transpose()
        # Returns the Lagrangian velocity field
        return V
    '''
    def get_velocity_E(self, Resolution, mass, X_in, V_in, start=[0,0,0], stop=[100,100,100],box_size=100.0):
        # grid_start is an [x,y,z] array that gives the starting points for each direction, same for grid_fin
        # Resolution defines the stepsize
        # box_size is the size of the box in Mpc. Assumed to be 100.
        # X is the position array [x,y,z]
        # V is the velocity array [v_x,v_y,v_z]
        X = copy.deepcopy(X_in)
        V = copy.deepcopy(V_in)
        step = box_size / float(Resolution)
        x_init = np.arange(start[0], stop[0], step) + 0.5 * step  # Add 0.5*step to have the points in the middle
        y_init = np.arange(start[1], stop[1], step) + 0.5 * step
        z_init = np.arange(start[2], stop[2], step) + 0.5 * step
        x = X[:, 0]
        y = X[:, 1]
        z = X[:, 2]
        v_x = V[:, 0]
        v_y = V[:, 1]
        v_z = V[:, 2]
        dx, dy, dz = step, step, step
        mass_tsc, v_x_E, v_y_E, v_z_E = Lagrangian2Eulerian.tsc(box_size, x_init, y_init, z_init, dx, dy, dz, mass, x,
                                                                y, z, v_x, v_y, v_z)
        # returns the vector field values for each point on the grid
        # returns also the mass scalar field
        return mass_tsc, v_x_E, v_y_E, v_z_E
    '''
    @staticmethod
    def get_indices(start,stop,X):
        # Determines the indices where the particle position is in given box
        selection_ind = np.where(np.logical_and(X[:, 2] >= start[2], np.logical_and(X[:, 2] <= stop[2],
                                                                                   np.logical_and(X[:, 1] >= start[1],
                                                                                                  np.logical_and(
                                                                                                      X[:, 1] <= stop[1],
                                                                                                      np.logical_and(
                                                                                                          X[:, 0] >=
                                                                                                          start[0],
                                                                                                          X[:, 0] <=
                                                                                                          stop[
                                                                                                              0]))))))
        selection_ind = selection_ind[0]  # Because there is an additional, useless dimension...
        return selection_ind

    @staticmethod
    def get_indices_compl(start,stop,X):
        # Determines the indices where the particle position is outside a given box
        selection_ind = np.where(np.logical_not(np.logical_and(X[:, 2] >= start[2], np.logical_and(X[:, 2] <= stop[2],
                                                                                   np.logical_and(X[:, 1] >= start[1],
                                                                                                  np.logical_and(
                                                                                                      X[:, 1] <= stop[1],
                                                                                                      np.logical_and(
                                                                                                          X[:, 0] >=
                                                                                                          start[0],
                                                                                                          X[:, 0] <=
                                                                                                          stop[
                                                                                                              0])))))))
        selection_ind = selection_ind[0]  # Because there is an additional, useless dimension...
        return selection_ind

    def full_reconstruction_nested(self,division_number,alpha,Resolution_full, Resolution_hom,beta,starts_all = None,rank=0,box_sizes_return = False,box_size_total=100.0, N_fake_particle=0):
        #division_number is the number which divides the length of the cube size
        #alpha is the parameter used to quantify the ratio between the sub-volume and the volume of the corresponding homogeneous grid (alpha = 1, same size)
        #beta is the parameter used to quantify the ratio between the sub-volume and the volume where final particles are selected (beta = 1, no particles outside the sub-volume are selected)
        #Resolution_full is the resolution of the full grid (Resolution_full^3 particles from the whole volume are selected
        #Resolution_hom is the resolution of the homogeneous grid
        #
        #
        starts_all = np.asarray(starts_all)
        N_tasks = len(starts_all[:,0])
        Resolution = Resolution_full
        Resolution_hom = Resolution_hom
        # loop over the whole box
        X_r_tot = np.empty((0, 3))
        ID_tot = np.empty((0, 0),dtype=int)
        box_sizes=np.array([])
        for i, start in enumerate(starts_all[:,0:3]):

            print("Rank %d: Starting task %d of %d"  %(rank, i, N_tasks))
            box_size_x = starts_all[i, 3]
            box_size_y = starts_all[i, 4]
            box_size_z = starts_all[i, 5]
            box_size = np.array([box_size_x, box_size_y, box_size_z])

            stop = start + box_size
            length_final = box_size * (beta - 1) * 0.5
            #length_hom = box_size * (beta - 1) * 0.5 + box_size * beta * (alpha - 1) * 0.5
            length_hom = (box_size + 2 * length_final) * (alpha - 1) * 0.5
            start_hom = start - length_hom-length_final
            stop_hom = stop + length_hom+length_final
            start_final = start-length_final
            stop_final = stop+length_final
            if len(starts_all[:,])>6:
                z_min = starts_all[i,6]
                z_max = starts_all[i,7]
            else:
                z_min = 0.0
                z_max = 0.0
            X, ID, X_mirror = self.get_final_position(start_final, stop_final, Resolution=Resolution,
                                                      mirror_length=length_final,box_size_total=box_size_total, z_min = z_min, z_max = z_max)
            N_part_tot = len(X[:, 0]) + len(X_mirror[:, 0])
            print("Rank %d: Shape of X_mirror : %s" % (rank, str(np.shape(X_mirror))))
            print("Rank %d: Shape of X : %s" % (rank, str(np.shape(X))))

            '''
            print N_part_tot
            if N_part_tot > 700:
                beta = 1.1
                length_final = box_size * (beta - 1) * 0.5
                start_final = start - length_final
                stop_final = stop + length_final
                X, ID, X_mirror = self.get_final_position(start_final, stop_final, Resolution=Resolution,
                                                          mirror_length=length_final)



            '''
            Resolution_temp = Resolution
            '''
            while N_part_tot >= 128**3:
                print("Rank %d: Decreasing Resolution from %d to %d") % (rank, Resolution_temp, Resolution_temp-2)
                Resolution_temp = Resolution_temp-2
                X, ID, X_mirror = self.get_final_position(start - length_final, stop + length_final,
                                                          Resolution=Resolution_temp, mirror_length=length_final)
                N_part_tot = len(X[:, 0]) + len(X_mirror[:, 0])
            '''
            indices_subvolume = self.get_indices(start, stop, X)
            N_particles = len(X[:,0])
            N_mirror = len(X_mirror[:,0])
            #print 'Number of particles  in subvolume: ', N_particles

            if N_fake_particle != 0:
                size_fake = int(abs(int(len(X[:, 0]))) * N_fake_particle)
                X_fake = np.random.uniform(start_final, stop_final, size=(size_fake, 3))
                X  = np.append(X,X_fake,axis=0)
                Resolution_hom = int(((N_particles + N_mirror + size_fake) ** (1.0 / 3.0))) + 1  # try this...
            else:
                Resolution_hom = int(((N_particles + N_mirror) ** (1.0 / 3.0))) + 1  # try this...
            #Different points for homogeneous grid
            X = np.append(X, X_mirror, axis=0)
            if len(X)==0:
                print('X is empty')
                continue
            start_point = np.array([min(X[:, 0]) - 0.5, min(X[:, 1]) - 0.5, min(X[:, 2]) - 0.5])
            stop_point = np.array([max(X[:, 0]) + 0.5, max(X[:, 1]) + 0.5, max(X[:, 2]) + 0.5])
            start_hom = start_point
            stop_hom = stop_point
            print('Selection for homogeneous grid:')
            print(start_hom)
            print(stop_hom)
            #Finished selection of points for homogeneous grid
            Q = self.get_grid(start_hom, stop_hom, Resolution=Resolution_hom)
            X_r = self.reconstruct_positions(X, Q,N_particles,rank=rank)
            X_r = X_r[np.arange(0, N_particles)] #choose only the particles that we want to reconstruct
            X_r = X_r[indices_subvolume]
            ID = ID[indices_subvolume]
            #X_in = X_in[indices_subvolume]
            X_r_tot = np.append(X_r_tot, X_r, axis=0)
            ID_tot = np.append(ID_tot,ID)
            print("Rank %d: Finished task %d of %d" % (rank, i+1, N_tasks))
            box_sizes = np.append(box_sizes, np.asarray([box_size] * len(ID)))  #to keep track of the volume size in which a particle is

        if box_sizes_return == True:
            return X_r_tot,ID_tot, box_sizes, z_mins, z_maxs
        else:
            return X_r_tot, ID_tot, z_mins, z_maxs

    def correct_boundaries(self,X,box_size=100):
        X_new = np.empty(np.shape(X))
        for i in np.arange(0,len(X[:,0])):
            if X[i,0] <= 0:
                X_new[i,0] = X[i,0]+box_size
            elif X[i,0] >= box_size:
                X_new[i,0] = X[i,0]-box_size
            else:
                X_new[i,0] = X[i,0]

            if X[i,1] <= 0:
                X_new[i,1] = X[i,1]+box_size
            elif X[i,1] >= box_size:
                X_new[i,1] = X[i,1]-box_size
            else:
                X_new[i,1] = X[i,1]

            if X[i,2] <= 0:
                X_new[i,2] = X[i,2]+box_size
            elif X[i,2] >= box_size:
                X_new[i,2] = X[i,2]-box_size
            else:
                X_new[i,2] = X[i,2]

        return X_new

    def correct_boundaries_new(self,X,X_in,box_size=100):
        X_new = np.empty(np.shape(X))
        for i in np.arange(0,len(X[:,0])):
            dx = abs(X[i,0]-X_in[i,0])
            dy = abs(X[i,1] - X_in[i,1])
            dz = abs(X[i,2] - X_in[i,2])
            if dx >= 100-dx:
                X_new[i,0] = 100-X[i,0]
            else:
                X_new[i,0] = X[i,0]
            if dy >= 100-dy:
                X_new[i,1] = 100-X[i,1]
            else:
                X_new[i,1] = X[i,1]
            if dz >= 100-dz:
                X_new[i,2] = 100-X[i,2]
            else:
                X_new[i,2] = X[i,2]
        return X_new

    def mirror_positions(self,X_in,mirror_length,box_size = 100.0):
        X = copy.deepcopy(X_in)
        start = [mirror_length,mirror_length,mirror_length]
        stop = [box_size-mirror_length,box_size-mirror_length,box_size-mirror_length]
        selection_ind = self.get_indices_compl(start,stop,X)
        selection_ind_inside = self.get_indices(start,stop,X)
        X1 = X[selection_ind,:]
        X2 = X[selection_ind, :]
        X3 = X[selection_ind, :]
        X4 = X[selection_ind, :]
        X5 = X[selection_ind, :]
        X6 = X[selection_ind, :]
        X7 = X[selection_ind, :]
        ###############
        X1[np.logical_and(X1[:,0]>=(box_size-mirror_length),X1[:,0]<=box_size),0]=X1[np.logical_and(X1[:,0]>=(box_size-mirror_length),X1[:,0]<=box_size),0]-box_size
        X1[np.logical_and(X1[:, 0] >= 0.0, X1[:, 0] <= mirror_length), 0] = box_size + X1[
            np.logical_and(X1[:, 0] >= 0.0, X1[:, 0] <= mirror_length), 0]

        X1[np.logical_and(X1[:,1]>=(box_size-mirror_length),X1[:,1]<=box_size),1]=X1[np.logical_and(X1[:,1]>=(box_size-mirror_length),X1[:,1]<=box_size),1]-box_size
        X1[np.logical_and(X1[:, 1] >=0.0, X1[:, 1] <= mirror_length), 1] = box_size + X1[
            np.logical_and(X1[:, 1] >= 0.0, X1[:, 1] <= mirror_length), 1]

        X1[np.logical_and(X1[:,2]>=(box_size-mirror_length),X1[:,2]<=box_size),2]=X1[np.logical_and(X1[:,2]>=(box_size-mirror_length),X1[:,2]<=box_size),2]-box_size
        X1[np.logical_and(X1[:, 2] >= 0.0, X1[:, 2] <= mirror_length), 2] = box_size + X1[
            np.logical_and(X1[:, 2] >= 0.0, X1[:, 2] <= mirror_length), 2]

        ##############
        X2[np.logical_and(X2[:, 0] >= (box_size - mirror_length), X2[:, 0] <= box_size), 0] = X2[np.logical_and(
            X2[:, 0] >= (box_size - mirror_length), X2[:, 0] <= box_size), 0] - box_size
        X2[np.logical_and(X2[:, 0] >= 0.0, X2[:, 0] <= mirror_length), 0] = box_size + X2[
            np.logical_and(X2[:, 0] >= 0.0, X2[:, 0] <= mirror_length), 0]

        X2[np.logical_and(X2[:, 1] >= (box_size - mirror_length), X2[:, 1] <= box_size), 1] = X2[np.logical_and(
            X2[:, 1] >= (box_size - mirror_length), X2[:, 1] <= box_size), 1] - box_size
        X2[np.logical_and(X2[:, 1] >= 0.0, X2[:, 1] <= mirror_length), 1] = box_size + X2[
            np.logical_and(X2[:, 1] >= 0.0, X2[:, 1] <= mirror_length), 1]
        #################
        X3[np.logical_and(X3[:, 1] >= (box_size - mirror_length), X3[:, 1] <= box_size), 1] = X3[np.logical_and(
            X3[:, 1] >= (box_size - mirror_length), X3[:, 1] <= box_size), 1] - box_size
        X3[np.logical_and(X3[:, 1] >= 0.0, X3[:, 1] <= mirror_length), 1] = box_size + X3[
            np.logical_and(X3[:, 1] >= 0.0, X3[:, 1] <= mirror_length), 1]

        X3[np.logical_and(X3[:, 2] >= (box_size - mirror_length), X3[:, 2] <= box_size), 2] = X3[np.logical_and(
            X3[:, 2] >= (box_size - mirror_length), X3[:, 2] <= box_size), 2] - box_size
        X3[np.logical_and(X3[:, 2] >= 0.0, X3[:, 2] <= mirror_length), 2] = box_size + X3[
            np.logical_and(X3[:, 2] >= 0.0, X3[:, 2] <= mirror_length), 2]
        #################
        X4[np.logical_and(X4[:,0]>=(box_size-mirror_length),X4[:,0]<=box_size),0]=X4[np.logical_and(X4[:,0]>=(box_size-mirror_length),X4[:,0]<=box_size),0]-box_size
        X4[np.logical_and(X4[:, 0] >= 0.0, X4[:, 0] <= mirror_length), 0] = box_size + X4[
            np.logical_and(X4[:, 0] >= 0.0, X4[:, 0] <= mirror_length), 0]

        X4[np.logical_and(X4[:,2]>=(box_size-mirror_length),X4[:,2]<=box_size),2]=X4[np.logical_and(X4[:,2]>=(box_size-mirror_length),X4[:,2]<=box_size),2]-box_size
        X4[np.logical_and(X4[:, 2] >= 0.0, X4[:, 2] <= mirror_length), 2] = box_size + X4[
            np.logical_and(X4[:, 2] >= 0.0, X4[:, 2] <= mirror_length), 2]
        #################
        X5[np.logical_and(X5[:,0]>=(box_size-mirror_length),X5[:,0]<=box_size),0]=X5[np.logical_and(X5[:,0]>=(box_size-mirror_length),X5[:,0]<=box_size),0]-box_size
        X5[np.logical_and(X5[:, 0] >= 0.0, X5[:, 0] <= mirror_length), 0] = box_size + X5[
            np.logical_and(X5[:, 0] >= 0.0, X5[:, 0] <= mirror_length), 0]
        #################
        X6[np.logical_and(X6[:,1]>=(box_size-mirror_length),X6[:,1]<=box_size),1]=X6[np.logical_and(X6[:,1]>=(box_size-mirror_length),X6[:,1]<=box_size),1]-box_size
        X6[np.logical_and(X6[:, 1] >= 0.0, X6[:, 1] <= mirror_length), 1] = box_size + X6[
            np.logical_and(X6[:, 1] >= 0.0, X6[:, 1] <= mirror_length), 1]
        #################
        X7[np.logical_and(X7[:,2]>=(box_size-mirror_length),X7[:,2]<=box_size),2]=X7[np.logical_and(X7[:,2]>=(box_size-mirror_length),X7[:,2]<=box_size),2]-box_size
        X7[np.logical_and(X7[:, 2] >= 0.0, X7[:, 2] <= mirror_length), 2] = box_size + X7[
            np.logical_and(X7[:, 2] >= 0.0, X7[:, 2] <= mirror_length), 2]
        X1 = np.append(X1, X2, axis=0)
        X1 = np.append(X1, X3, axis=0)
        X1 = np.append(X1, X4, axis=0)
        X1 = np.append(X1, X5, axis=0)
        X1 = np.append(X1, X6, axis=0)
        X1 = np.append(X1, X7, axis=0)

        seen = set()
        new_X = []
        for item in X1:
            t = tuple(item)
            if t not in seen:
                new_X.append(item)
                seen.add(t)
        new_X = np.asarray(new_X)
        start = [0,0,0]
        stop = [100,100,100]
        if not new_X.size:
            return np.empty((0,3))
        selection_ind = self.get_indices_compl(start,stop,new_X)
        new_X = new_X[selection_ind]
        return new_X

