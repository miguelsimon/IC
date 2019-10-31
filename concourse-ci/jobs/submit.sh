#!/bin/bash

function echo_info () {
    echo
    echo "`qstat`"
    echo
}

(cd IC_master && git lfs pull && source manage.sh work_in_python_version_no_tests 3.7)
(cd IC && git lfs pull && source manage.sh work_in_python_version_no_tests 3.7)

master_job=$(qsub jobs/master_job.sh)
pr_job=$(qsub jobs/pr_job.sh)

all_ok=$(qsub -W depend=afterok:$master_job:$pr_job jobs/all_ok.sh)

echo_info
status=`qstat | grep $all_ok`
while [ -n "$status" ] # while $status is not empty
    do
    sleep 10
    echo_info
    status=`qstat | grep $all_ok`
    done


if [[ -f /data_extra2/icdev/miguel_scratch/all_ok ]]; then
    echo "all ok"
else
    echo "not all ok"
    exit 1
fi
