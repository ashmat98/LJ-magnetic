#!/bin/bash
set -e
set -x

build_dir="/data/biophys/ashmat/builds/LAMMPS/mylammps/builds/build_$HOSTNAME"
# build_dir="/data/biophys/ashmat/builds/LAMMPS/mylammps/build"
BASE_DIR=${BASE_DIR:-"/home/ashmat/cluster/LJ-magnetic"}

#wait random amount of time
python -c "import time, random, os; random.seed(os.getpid()+int(time.time()));x=10*random.random(); print(x);time.sleep(x)"

if [[ ! -d "$build_dir" ]]; then
    mkdir -p $build_dir; cd $build_dir
    echo $JOB_ID > ./not_ready

    # module load intel/compiler
    
    cmake -D CMAKE_BUILD_TYPE=Release \
      -D INTEL_ARCH=cpu \
      -D PKG_H5MD=yes \
      -D PKG_OPENMP=yes \
      ../../cmake       # configuration reading CMake scripts from ../cmake
      # -DCMAKE_C_COMPILER=icc -DCMAKE_CXX_COMPILER=icpc -DCMAKE_Fortran_COMPILER=ifort \
    make -j 16

    rm ./not_ready
fi

while [ -e "$build_dir/not_ready" ]; do
    # rm -rf $build_dir
    echo "Waiting for compilation in task " $(cat "$build_dir/not_ready")
    sleep 1
done


cd $BASE_DIR
rm -rf ./.lammps_build


cp -r $build_dir ./.lammps_build

# cmake --build . 
    