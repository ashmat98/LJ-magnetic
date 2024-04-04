#!/bin/bash

# set -e
set -x

send-telegram-log "Start mathematica export"

# ./scripts/export_for_mathematica.py --prefix="ER300.6" "ER 3.303.6.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER300.15" "ER 3.303.15.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER300.25" "ER 3.303.25.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER300.35" "ER 3.303.35.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER300.45" "ER 3.303.45.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER300.55" "ER 3.303.55.lammps"

./scripts/export_for_mathematica.py --prefix="ERlong" "ER 3.303.weak.lammps"

# ./scripts/export_for_mathematica.py --prefix="ER3.631" "ER 3.631.weak.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER3.632" "ER 3.632.weak.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER3.630" "ER 3.630.weak.lammps"

# ./scripts/export_for_mathematica.py --prefix="ER3.600" "ER 3.600.weak.lammps"
# ./scripts/export_for_mathematica.py --prefix="ER3.610" "ER 3.610.weak.lammps"




send-telegram-log "End mathematica export"
