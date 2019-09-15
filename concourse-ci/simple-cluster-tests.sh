#!/bin/bash

set -ex

# error out if the credentials haven't been provided

: "${SSH_PRIVATE_KEY:?}"

echo "$SSH_PRIVATE_KEY" > ssh_key
chmod 600 ssh_key

apt-get update && apt install -y curl rsync ssh

# IC holds the PR
# IC_master holds the reference version
# IC_operations holds this code

ssh \
  -i ssh_key \
  -o StrictHostKeyChecking=no \
  icdev@majorana1.ific.uv.es \
  "cd /data_extra2/icdev && rm -rf miguel_scratch && mkdir -p miguel_scratch/outputs"

rsync \
  -e "ssh -i ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  --delete \
  IC_master \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/

rsync \
  -e "ssh -i ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  --delete \
  IC \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/

rsync \
  -e "ssh -i ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  --delete \
  IC_operations/concourse-ci/jobs \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/

rsync \
  -e "ssh -i ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  --delete \
  IC_operations/concourse-ci/irene.conf \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/

ssh \
  -i ssh_key \
  -o StrictHostKeyChecking=no \
  icdev@majorana1.ific.uv.es \
  "cd /data_extra2/icdev/miguel_scratch && bash jobs/submit.sh"

rsync \
  -e "ssh -i ssh_key -o StrictHostKeyChecking=no" \
  -vzr \
  icdev@majorana1.ific.uv.es:/data_extra2/icdev/miguel_scratch/outputs \
  .

ls outputs
