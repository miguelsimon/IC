#!/bin/bash

set -ex

# error out if the credentials haven't been provided

: "${SSH_PRIVATE_KEY:?}"

echo "$SSH_PRIVATE_KEY" > ssh_key
chmod 600 ssh_key

apt-get update && apt install -y curl rsync ssh

# test access to the cluster
ssh -t \
  -o StrictHostKeyChecking=no \
  -i ssh_key \
  icdev@majorana1.ific.uv.es "ls -lhtr"

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
apt-get install -y git-lfs

# PR resource doesn't automatically pull lfs
(cd IC && git lfs install && git lfs pull)

# IC holds the PR
# IC_master holds the reference version

rsync \
  -e "ssh -o StrictHostKeyChecking=no -i ssh_key" \
  -avzh \
  IC \
  icdev@majorana1.ific.uv.es:/home/icdev/

rsync \
  -e "ssh -o StrictHostKeyChecking=no -i ssh_key" \
  -avzh \
  IC_master \
  icdev@majorana1.ific.uv.es:/home/icdev/
