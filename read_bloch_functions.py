import numpy as np
import netCDF4 as nc


# Read and store Bloch wavefunctions into numpy array
# In futre, the script could be turned into a function

wf_header = 'SAVE/ns.wf'
db_filename = 'SAVE/ns.db1'
output_file = 'wfn_GaAs'
read_dips = True
dips_file = 'dipoles/ndb.dipoles' 
output_dips = 'dipoles'
output_eig = 'eigenvalues'


############## Function for reading dipoles #####################

def read_dipoles(dips_file):
    dips = nc.Dataset(dips_file,'r')
    dipoles  = np.array(dips.variables['DIP_iR'])
    # Here change the variable to 'DIP_P' or 'DIP_v'
    # for momentum or velcity matrix elements
    dipoles = dipoles[0,...,0] + 1j*  dipoles[0,...,1]
    # nkpt, nbnd, nbnd, directions
    return(dipoles)

############## Function for reading eigenvalues #####################

def read_eigs(db_filename):
    dips = nc.Dataset(dips_file,'r')
    dipoles  = np.array(dips.variables['DIP_iR'])
    dipoles = dipoles[0,...,0] + 1j*  dipoles[0,...,1]
    # nkpt, nbnd, nbnd, directions
    return(dipoles)


############## Function for reading databse #####################

database = nc.Dataset(db_filename)
nkpt = int( database['EIGENVALUES'][...].shape[1] )
nbnd = int( database['EIGENVALUES'][...].shape[2] )

# nG is an array of the number of G-vectors used for description of a Bloch function
# nG are slightly differernt for different k-points 
 
nG = database['WFC_NG'][...].data # Note that the nG

#####################################################################

# Initiating WFN array 
# Note that we use np.max(nG) to accommodate all coefficents for G-vectors
# For k-point where nG < np.max(nG), the additinoal coefficients will be set to zero
wfn = np.zeros((nkpt,nbnd,2,int(np.max(nG))),dtype=complex) # 2 : for spinors

for i in range(nkpt):
    print("Reading wavefunction for k-point: ",i)
    wf = nc.Dataset(f'{wf_header}_fragments_{i+1}_1','r')
    #nbnd, spinors, Gvecs, real/imag
    wfn[i,:,:int(nG[i]),:] = wf[f'WF_COMPONENTS_@_SP_POL1_K{i+1}_BAND_GRP_1'][...,0].data
    wfn[i,:,:int(nG[i]),:] +=  1j* wf[f'WF_COMPONENTS_@_SP_POL1_K{i+1}_BAND_GRP_1'][...,1].data
    nc.Dataset.close(wf)

# Dumping the wfn array to a binary output file
np.save(output_file,wfn,allow_pickle=True)
# Note the dimensions of the array are 
# nkpt, nbnd, nspinor, nG 
# This can be loaded directly using
# array = np.load(output_file,allow_pickle=True)

######### Dumping eigenvalues #########

print("Reading and dumping eigenvalues")

eigs = np.array(database['EIGENVALUES'])[0,...]
# Dimension of eigenvalue array are nkpt, nbnd

np.save(output_eig,eigs,allow_pickle=True)


######### Dumping diples #########

if read_dips==True:
    print("Reading and dumping dipoles")
    dipoles = read_dipoles(dips_file)
    np.save(output_dips,dipoles,allow_pickle=True)
    # Dipole matrix is stored as an array with
    # indices : nkpt, nbnd, nbnd, cartesian directions


