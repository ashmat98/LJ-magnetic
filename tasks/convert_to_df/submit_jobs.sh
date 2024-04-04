#!/usr/bin/env bash

export hdf5_dir="/data/biophys/ashmat/LJ-magnetic/hdf5s"
export dfs_dir="/data/biophys/ashmat/LJ-magnetic/dfs"

cd tasks/convert_to_df
python ./export_file_list.py
line_count=$(wc -l < file_names.txt)

echo "Total lines $line_count"

sbatch --array=1-$line_count ./job_script.sh
