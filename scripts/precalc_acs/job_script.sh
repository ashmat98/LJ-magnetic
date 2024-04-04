#!/bin/bash

#SBATCH --array=1-500

#SBATCH --ntasks=1  # number of processor cores (i.e. tasks)
#SBATCH --cpus-per-task=1

#SBATCH --mem-per-cpu=100000M
#SBATCH --time=0-5:00:02

#SBATCH --partition medium

# The following partitions are available
# debug	        10:00
# short	        2:00:00	
# medium	    2-00:00:00
# long	        14-00:00:00
# graphic	    2-00:00:00
# extra_long	28-00:00:00


# If you so choose Slurm will notify you when certain events happen for your job 
# for a full list of possible options look furhter down
# NONE
# BEGIN (job has been allocated resources)
# END (job terminated with exit code 0)
# FAIL (job terminated with non-zero exit code)
# REQUEUE (job has been returened to queue - most likely due to a host failure)
# ALL (equivalent to BEGIN, END, FAIL, REQUEUE, and STAGE_OUT - STAGE_OUT does not apply to our cluster)
# TIME_LIMIT (job has reached the specified time limit)
# TIME_LIMIT_90 (80, 50) (job has reached x percent of its time limit)
# ARRAY_TASKS (use with caution this sends individual e-mails for each array task which could number in the thousands)

#SBATCH --mail-type FAIL
#SBATCH --mail-type TIME_LIMIT
# #SBATCH --mail-type END
#SBATCH --mail-type ARRAY_TASKS

#SBATCH --job-name="precalc acs"


#SBATCH --output=/data/biophys/ashmat/outputs/%A_%a
#SBATCH --error=/data/biophys/ashmat/outputs/%A_%a.err

#
# rsync -av --files-from=<(echo "utils/ACfunctions.py" "simulator/hdf5IO.py" "tools/gamma_estimator.py") /home/ashmat/cluster/LJ-magnetic/ /home/ashmat/cluster/LJ-magnetic//aaa
set -e
set -x

START=$(date +%s.%N)


# Set variables you need
job_id=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}

source_dir="/home/ashmat/cluster/LJ-magnetic/"
scratch="/scratch/$USER/$job_id"
hdf5_dir="/data/biophys/ashmat/LJ-magnetic/hdf5s"
output_dir="/data/biophys/ashmat/LJ-magnetic/subresults"

export HDF5_PATH="/data/biophys/ashmat/LJ-magnetic/hdf5s"
export ACS_PATH="/data/biophys/ashmat/LJ-magnetic/acs"

#Create your scratch space
mkdir -p $scratch
mkdir -p $ACS_PATH


files_to_copy="\
utils/ACfunctions.py\n\
simulator/hdf5IO.py\n\
settings.py\n\
tools/gamma_estimator.py"

cd $scratch

rsync -av --files-from=<(echo -e $files_to_copy ) \
    $source_dir $scratch
cp $source_dir/scripts/precalc_acs/script.py ./


params=$(sed -n -e "$SLURM_ARRAY_TASK_ID p" "$PARAM_FILE")

echo $params

# cp "$hdf5_dir/$filename" "./$filename"
module load python/3.8
# python3 script.py $params
eval "python3 script.py $params"

# Clean up
cd
rm -rf $scratch

END=$(date +%s.%N)
DIFF=$(echo " ($END - $START)" | bc )
echo Job actual time: $DIFF

exit 0



