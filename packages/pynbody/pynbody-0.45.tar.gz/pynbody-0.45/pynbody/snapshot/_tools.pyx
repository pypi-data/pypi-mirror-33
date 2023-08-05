@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def gen_partial_grid(np.ndarray[input_quantities_type, ndim=2] pos, 
    						       	int start, int stop, int step, int nx, int ny, int nz) :
    cdef int n
    cdef int i=0
    cdef int x=0, y=0, z=0
    with nogil:
        for n in range(start, stop, step) :
            x = n%nx;
            y = (n/nx)%ny;
            z = (n/(nx*ny))%nz;
            pos[i,0] = (float(x)+0.5)/nx
            pos[i,1] = (float(y)+0.5)/ny
            pos[i,2] = (float(z)+0.5)/nz
            i+=1
            
