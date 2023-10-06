#!/bin/bash

# 14840

# 12211589
# 12213264
# 12215400

#SBATCH --array=1-163

#SBATCH --ntasks=1  # number of processor cores (i.e. tasks)
#SBATCH --cpus-per-task=1

#SBATCH --mem-per-cpu=20000M
#SBATCH --time=0-6:00:00

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

#SBATCH --job-name="convert"

#SBATCH --output=/data/biophys/ashmat/outputs/%A_%a
# #SBATCH --error=/data/biophys/ashmat/outputs/%A_%a.err


set -e
set -x

START=$(date +%s.%N)


# Set variables you need
job_id=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}


hdf5_dir="/data/biophys/ashmat/LJ-magnetic/hdf5s"

base_dir=/home/ashmat/cluster/LJ-magnetic/

scratch="/scratch/$USER/$job_id"



#Create your scratch space
mkdir -p $scratch


# Copy your program (and maybe input files if you need them)
cd $scratch
mkdir ./utils
cp $base_dir/utils/convert.py ./utils/
cp $base_dir/tasks/migrate_total_props/convert.py ./convert.py
cp $base_dir/tasks/migrate_total_props/file_names.txt ./file_names.txt 
# sed -n -e "1 p" ./tasks/migrate_total_props/file_names.txt
filename=$(sed -n -e "$SLURM_ARRAY_TASK_ID p" ./file_names.txt)
echo $filename


module load python/3.8
python3 convert.py "$hdf5_dir/$filename" 

# copy results to an accessable location
# cp "$scratch/source/$filename" "$dfs_dir/$filename"

# Clean up
cd
rm -rf $scratch

END=$(date +%s.%N)
DIFF=$(echo " ($END - $START)" | bc )
echo Job actual time: $DIFF

exit 0



#All array instruction are inclusive meaning the numbers 
#you specify are part of the array

# Simplest case array goes from 0 to X
# #SBATCH --array=X (0..X)

# You can also specify a range like this
# #SBATCH --array=X-Y
# #SBATCH --array=10-57

# You can specify a step size so only every nth number is used
# #SBATCH --array=12:4 (0,4,8,12)
# #SBATCH --array=1-12:4 (1,5,9)

# If you want the most control you can specify numbers 
# individually by listing them with commas seperating them
# #SBATCH --array=X,Y,Z

# You can also mix the versions seen above except case 1 because 
# it would conflict with specifying individual numbers
# #SBATCH --array=0-9,10-100:10,200
# 0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200

# srun <your_program> $(sed -n -e "$SLURM_ARRAY_TASK_ID p" <your_parameterfile>)
