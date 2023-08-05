import mpi4py.MPI as mpi

print(mpi.COMM_WORLD.rank, mpi.COMM_WORLD.size)
