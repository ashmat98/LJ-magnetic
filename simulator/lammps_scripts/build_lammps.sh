#!/bin/bash
set -e
set -x
lamps_source="/data/biophys/ashmat/builds/LAMMPS/mylammps/"
build_dir="$lamps_source/builds/build_$HOSTNAME"

# build_dir="/data/biophys/ashmat/builds/LAMMPS/mylammps/build"
BASE_DIR=${BASE_DIR:-"/home/ashmat/cluster/LJ-magnetic"}

#wait random amount of time
python -c "import time, random, os; random.seed(os.getpid()+int(time.time()));x=10*random.random(); print(x);time.sleep(x)"

if [[ ! -d "$build_dir" ]]; then
    mkdir -p "$build_dir"; 
    echo $JOB_ID > "$build_dir/not_ready"

    cd $BASE_DIR
    mkdir -p ./tmp_lamps
    rm -rf ./tmp_lammps/source
    rsync -a --exclude 'builds*' --exclude '.*' "$lamps_source" ./tmp_lammps/source/
    
    mkdir ./tmp_lammps/source/build
    cd ./tmp_lammps/source/build
    ls -a ../

    cmake -D CMAKE_BUILD_TYPE=Release \
      -D INTEL_ARCH=cpu \
      -D PKG_H5MD=yes \
      -D PKG_OPENMP=yes \
      -D PKG_EXTRA-PAIR=yes \
      ../cmake       # configuration reading CMake scripts from ../cmake
      # -DCMAKE_C_COMPILER=icc -DCMAKE_CXX_COMPILER=icpc -DCMAKE_Fortran_COMPILER=ifort \
    make -j 16

    cp -r ./ "$build_dir"

    rm "$build_dir/not_ready"
fi

while [ -e "$build_dir/not_ready" ]; do
    # rm -rf $build_dir
    echo "Waiting for compilation in task " $(cat "$build_dir/not_ready")
    sleep 1
done


cd $BASE_DIR
rm -rf ./.lammps_build
mkdir ./.lammps_build
cp  $build_dir/lmp ./.lammps_build/lmp

# cmake --build . 
    