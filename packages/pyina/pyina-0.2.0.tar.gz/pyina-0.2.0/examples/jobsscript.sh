#!/bin/sh
#PBS -l nodes=1:ppn=4
#PBS -l walltime=00:03:00
cd ${PBS_O_WORKDIR} || exit 2
mpiexec -np 4 python hello_mpi4py.py
