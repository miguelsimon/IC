#!/bin/bash

set -ex

# error out if the credentials haven't been provided

: "${SSH_PRIVATE_KEY:?}"

echo "$SSH_PRIVATE_KEY" > ssh_key
chmod 600 ssh_key

apt-get update && apt install -y curl rsync ssh python3 python3-pip

# IC holds the PR
# IC_master holds the reference version
# IC_operations holds this code

cd IC_operations/concourse-ci
mkdir job

pip3 install -r requirements.txt

python3 -m assemble_jobs.production_jobs \
  --master_dir ../../IC_master \
  --pr_dir ../../IC \
  --city_conf_dir conf \
  --target_dir job

rsync \
  -e "ssh -i ../../ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  --delete \
  job/* \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/

ssh \
  -i ../../ssh_key \
  -o StrictHostKeyChecking=no \
  icdev@majorana1.ific.uv.es \
  "cd /data_extra2/icdev/miguel_scratch && bash chain.sh"

rsync \
  -e "ssh -i ../../ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/comparison_outputs \
  .

python3 -m assemble_jobs.reports \
  --output_dir comparison_outputs \
  --format txt
