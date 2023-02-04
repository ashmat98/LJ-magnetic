#!/bin/bash

# configure job arrays, %A, %a, $SLURM_ARRAY_JOB_ID, $SLURM_ARRAY_TASK_ID are defined
#SBATCH --array=1-3


# Set max time to your time estimation for your program be as precise as possible
# for optimal cluster utilization
#SBATCH --time=00:08:00

#
# There are a lot of ways to specify hardware ressources we recommend this one
#

# Set ntasks to 1 except when you are trying to run 2 tasks that are exactly the same
# although in some cases like simulations with random events this may be desirable
#SBATCH --ntasks=1  # number of processor cores (i.e. tasks)

# Now set your cpu and memory requirements and onve again be as precise as possible
# keep in mind if your pregram exceeds the requested memory it will be terminated prematurely
# the configuration below will result in a job allocation of 2 cores and 40 MB of RAM
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=800M

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
# #SBATCH --mail-type END

#SBATCH --mail-type FAIL
#SBATCH --mail-type TIME_LIMIT


# Feel free to give your job a good name to better identify it later
# the same name expansions as for the ourput and error path apply here as well
# see below for additional information
#SBATCH --job-name="beta_omega"

# Always try to use absolute paths for your output and error files
# IF you only specify an output file all error messages will automaticly be redirected in there
# You can utilize name expansion to make sure each job has a uniq output file if the file already exists 
# Slurm will delete all the content that was there before before writing to this file so beware.

#SBATCH --output=/home/ashmat/cluster/outputs/task-%A_%a.out
# #SBATCH --error=/home/ashmat/cluster/outputs/task-%A_%a.err
# #SBATCH --output=/scratch/$USER/%j/results/output-%j.out


# causes jobs to fail if one command fails - makes failed jobs easier to find with tools like sacct
set -e
# set -x

START=$(date +%s.%N)



# Set variables you need
job_id=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}

root="/home/ashmat/cluster/"
project=$root/LJ-magnetic
scratch="/scratch/$USER/$job_id"



#Create your scratch space
mkdir -p $project/results
mkdir -p $project/results/$job_id
mkdir -p $scratch


cd $scratch
# Copy your program (and maybe input files if you need them)
cp -r $project/source .
mkdir -p ./results
cd ./source

ln -s $root/outputs/task-$job_id.out $project/results/$job_id/stdout.txt
# ln -s $root/outputs/task-$SLURM_JOB_ID.err $project/results/$SLURM_JOB_ID/stderr.txt

export HDF5_PATH=${scratch}/results
export LOG_PATH=${scratch}/results/

module load python-3.7.4
make offline
python tasks/beta_omega/run_simulation.py -i 1


# srun ./your_program parameters

# copy results to an accessable location
# only copy things you really need
cp -Tr $scratch/results $project/results/$job_id 

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