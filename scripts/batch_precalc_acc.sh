#!/bin/bash

# set -e
set -x

shift=5000
wide=2000
W=500
dt1=100
dt2=500

groups=(
# 'ER 3.303.6.lammps' 
# 'ER 3.303.15.lammps' 'ER 3.303.25.lammps'
# 'ER 3.303.35.lammps' 'ER 3.303.45.lammps'
# 'ER 3.303.55.lammps' 
# 'ER 3.600.weak.lammps' 
'ER 3.303.weak.lammps'
)

for group in "${groups[@]}"
do 
./scripts/precalc_acs/submit_job.py --group-name="$group" \
    --shift=$shift --wide=$wide --dt1=$dt1 --dt2=$dt2 \
    --W 5 15 30 50 100 200 500 1000 1500
done
