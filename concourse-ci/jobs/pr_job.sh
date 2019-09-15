#!/bin/bash
source /home/icdev/.bashrc
source /home/icdev/miniconda/etc/profile.d/conda.sh
conda activate IC-3.7-2018-11-14
export LD_LIBRARY_PATH="/home/icdev/miniconda/lib:$LD_LIBRARY_PATH"
export ICTDIR=/data_extra2/icdev/miguel_scratch/IC
export ICDIR="$ICTDIR/invisible_cities"
export PATH="$ICTDIR/bin:$PATH"
export PYTHONPATH="$ICTDIR:$PYTHONPATH"

city irene \
    -i /data_extra2/mmkekic/example_inputs/run_6971_0009_trigger1_waveforms.h5 \
    -o /data_extra2/icdev/miguel_scratch/outputs/pr_run_6971_0009_trigger1_pmaps.h5  \
    /data_extra2/icdev/miguel_scratch/jobs/irene.conf
