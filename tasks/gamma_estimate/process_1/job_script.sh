#!/bin/bash

#SBATCH --array=1-500

#SBATCH --ntasks=1  # number of processor cores (i.e. tasks)
#SBATCH --cpus-per-task=6

#SBATCH --mem-per-cpu=100000M
#SBATCH --time=1-1:30:00

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
#SBATCH --mail-type END
# #SBATCH --mail-type ARRAY_TASKS

#SBATCH --job-name="process_1"


#SBATCH --output=/data/biophys/ashmat/outputs/%A_%a.out
# #SBATCH --error=/data/biophys/ashmat/outputs/%A_%a.err


set -e
set -x

START=$(date +%s.%N)


# Set variables you need
job_id=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}


scratch="/scratch/$USER/$job_id"
hdf5_dir="/data/biophys/ashmat/LJ-magnetic/hdf5s"
output_dir="/data/biophys/ashmat/LJ-magnetic/subresults"


#Create your scratch space
mkdir -p $scratch
mkdir -p $output_dir


cd $scratch
# Copy your program (and maybe input files if you need them)
cp /home/ashmat/cluster/LJ-magnetic/tasks/gamma_estimate/process_1/script.py ./
cp /home/ashmat/cluster/LJ-magnetic/tasks/gamma_estimate/process_1/paths.txt ./

filename=$(sed -n -e "$SLURM_ARRAY_TASK_ID p" ./paths.txt)
echo $filename

# cp "$hdf5_dir/$filename" "./$filename"
module load python/3.8
python3 script.py "$hdf5_dir/$filename"

# copy results to an accessable location
cp "./out.hdf5" "$output_dir/ac.$filename"

# Clean up
cd
rm -rf $scratch

END=$(date +%s.%N)
DIFF=$(echo " ($END - $START)" | bc )
echo Job actual time: $DIFF

exit 0



