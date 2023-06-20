#!/bin/bash

#SBATCH --array=0

#SBATCH --ntasks=1  # number of processor cores (i.e. tasks)
#SBATCH --cpus-per-task=1

# #SBATCH --mem-per-cpu=1100M
# #SBATCH --time=0-5:00:00

# #SBATCH --partition medium

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


# #SBATCH --job-name="relaxation_time"


# #SBATCH --output=/home/ashmat/cluster/outputs/task-%A_%a.out
# #SBATCH --error=/home/ashmat/cluster/outputs/task-%A_%a.err


set -e
set -x

START=$(date +%s.%N)


# Set variables you need
job_id=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}

data="/data/biophys/ashmat/LJ-magnetic"
source=/home/ashmat/cluster/LJ-magnetic/
scratch="/scratch/$USER/$job_id"



#Create your scratch space
mkdir -p $data/results
mkdir -p $data/results/$job_id

mkdir -p $scratch
mkdir -p $scratch/results


cd $scratch
# Copy your program (and maybe input files if you need them)
cp -r $source ./source
cd ./source

# ln -s $data/outputs/task-$job_id.out $data/results/$job_id/stdout.txt
# ln -s $root/outputs/task-$SLURM_JOB_ID.err $project/results/$SLURM_JOB_ID/stderr.txt

export HDF5_PATH=${scratch}/results
export LOG_PATH=${scratch}/results/

module load python-3.7.4
make offline
python "scripts/run_simulation_with_params.py" 

# copy results to an accessable location
# only copy things you really need
cp -Tr $scratch/results $data/results/$job_id 

# Clean up after yourself
cd
rm -rf $scratch
# rm -rf $scratch/results

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