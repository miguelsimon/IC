* [Overview](#overview)
* [Usage](#usage)
  * [Concourse](#concourse)
    * [Online demo version](#online-demo-version)
    * [Walkthrough for executing concourse locally](#walkthrough-for-executing-concourse-locally)
    * [Running on a server](#running-on-a-server)
    * [fly execute for cluster tests](#fly-execute-for-cluster-tests)
    * [building the job artifact](#building-the-job-artifact)
  * [Job specification](#job-specification)
    * [run unit tests](#run-unit-tests)
    * [command line usage](#command-line-usage)

# Overview

Proof of concept is up at [https://ci.ific-invisible-cities.com/](https://ci.ific-invisible-cities.com/). It's password protected, ask @mmkekic for access if you want to poke around, authorization for the real version would be mediated via oauth by membership in the [nextic github organization](https://github.com/nextic).

This sets up an example CI pipeline for the invisible cities project. The idea is that, whenever a pull request to a [protected branch](https://help.github.com/en/articles/about-protected-branches) happens:

1. the CI runs the unit tests (currently what your travis CI runs) and errors out if they fail
2. if unit tests pass, the CI submits a job to the majorana cluster that performs sanity checks; a report is generated and put somewhere (eg. a gce bucket)
3. If the sanity checks also pass, the CI marks the PR as approved in github and the merge can now be performed.

I set this up using [concourse](https://concourse-ci.org/) because:
* as a side effect of dragging my current company's devs into the 19th century, I can now set up continuous integration environments based on concourse in my sleep
* concourse is awesome; it does have a learning curve (as do all CI tools) but it's very flexible and forces you to decouple stuff in a way that makes deploying in cloud environments easy.


# Usage

## Concourse

### Online demo version

The concourse interface is up at [https://ci.ific-invisible-cities.com/](https://ci.ific-invisible-cities.com/).

The easiest way to understand what's going on is just to open a test PR to the master branch in the [https://github.com/miguelsimon/IC](https://github.com/miguelsimon/IC) repo, you should see:
* Merges are disallowed until the build passes
* At least 1 review is required.

### Walkthrough for executing concourse locally

#### Prerequisites

* [docker-compose](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04)
* make ie if you're on some unix flavor you're fine
* required credentials are text files that belong in a `credentials` directory which is .gitignored to avoid committing credentials; for a local deploy, these are:
  * `credentials/github_access_token` a github access token to write PR status back to github
  * `credentials/key_concourse` is an ssh private key which lets the `icdev` user access the majorana cluster

These steps must be executed from within this directory:

1. launch the local concourse instance:
  `docker-compose up -d`
2. navigate to [http://localhost:8080](http://localhost:8080) and login with username: test password: test
3. download the [fly cli](https://concourse-ci.org/fly.html) from your local concourse installation
4. log in to concourse via the command line:
  `fly -t local login -c http://localhost:8080`
5. push the pr pipeline (you'll need appropriate credentials)
  `make set_local_pr_pipeline`

Voilà, you can now unpause the pipeline.

### Running on a server

I've set it up at [https://ci.ific-invisible-cities.com/](https://ci.ific-invisible-cities.com/).

Doing that involves quite a bit of onerous and annoying details, dealing with dns, certificates, hosting etc. These are just annoying if you know what you're doing but require loads of time to learn all that boring trivia if you don't. I can talk to you guys and help you set it up in your context.

The set up is mostly sane but the top priority was getting it working in < 3 hours so I'm mainly using stuff I'm comfortable with.

Birds-eye overview of the current setup:
* The deploy is specified in docker compose; I'm running postgres, concourse, an nginx frontend and [certbot](https://certbot.eff.org/) to set up free certificates via letsencrypt.
* I'm running it on a trial google compute engine VM (google cloud is a very sane cloud provider when compared to others *cough* amazon *cough*)
* access control is via username - password now, we'd delegate access control to github via oauth to avoid operational hassles

### fly execute for cluster tests

To test the `simple-cluster-tests.sh` script it's convenient to launch it using local content; you can do this via fly execute (if you've got the proper credentials); the following example uses an IC_master checkout to populate both the IC and IC_master inputs to the script, and leaves results in the `outputs` directory:

```
mkdir outputs

SSH_PRIVATE_KEY=$(cat credentials/key_concourse) \
  fly -t remote execute \
    --include-ignored \
    --input IC=~/IC_master \
    --input IC_master=~/IC_master \
    --input IC_operations=../ \
    --output outputs=./outputs \
    --config simple-cluster-tests.yml
```

## Job specification

There's a lot of configuration involved in managing the tests and it's probably going to get worse when we want to test against other conda versions, add fancier tests, etc. Life's too short to deal with this by hand.

It's a pretty heavyweight approach but it's the fastest way, because:
* I use the python typesystem to catch bugs
* when things get complicated I can easily do fancy stuff like automatically calculate job dependencies and express these to pbs to parallelize this as much as possible

The approach I'm taking is:
1. specify the desired configuration in a python dsl, see [assemble_jobs/miguel_jobs.py](assemble_jobs/miguel_jobs.py) for an example (work in progress as I don't fully understand the IC system yet)
2. use the specification to build a directory locally with all the necessary stuff (scripts, checked out source etc) so it can be inspected
3. push the directory to the cluster, submit the jobs

### run unit tests

`make test`

### command line usage

Let's assume you've got a checkout of IC in `~/IC_master`. You can compile the artifact (using the same directory for both the PR and master version) like so:

```
make env_ok #ensure python env is up
mkdir job

env/bin/python -m assemble_jobs.miguel_jobs \
  --master_dir ~/IC_master \
  --pr_dir ~/IC_master \
  --city_conf_dir conf \
  --target_dir job
```
