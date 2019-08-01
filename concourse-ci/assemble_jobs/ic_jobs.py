import os
import shutil
from typing import NamedTuple, Sequence, Union

from assemble_jobs.city_job import CityJob
from assemble_jobs.compare_pmap import ComparePmapJob

CHAIN_TEMPLATE = """#!/bin/bash

rm -f {all_ok_file}

function echo_info () {{
    echo
    echo "`qstat`"
    echo
}}

(cd master && git lfs pull && source manage.sh work_in_python_version_no_tests 3.7)
(cd pr && git lfs pull && source manage.sh work_in_python_version_no_tests 3.7)

{job_chain}

all_ok=$(qsub -W depend=afterok:${last_job} jobs/all_ok.sh)

echo_info
status=`qstat | grep $all_ok`
while [ -n "$status" ] # while $status is not empty
    do
    sleep 10
    echo_info
    status=`qstat | grep $all_ok`
    done


if [[ -f {all_ok_file} ]]; then
    echo "all ok"
else
    echo "not all ok"
    exit 1
fi

"""

ALL_OK_TEMPLATE = """#!/bin/bash
touch {all_ok_file}
"""


class Config(NamedTuple):
    bashrc: str
    conda_sh: str
    conda_activate: str
    conda_lib: str
    remote_dir: str

    def get_conf_path(self, city: str) -> str:
        return os.path.join(self.remote_dir, "conf", "{0}.conf".format(city))

    def get_ictdir(self, version: str) -> str:
        assert version in ["pr", "master"]
        return os.path.join(self.remote_dir, version)


class CitySpec(NamedTuple):
    city: str
    input_path: str
    output_path: str
    ic_version: str

    def get_job(self, config: Config) -> CityJob:
        return CityJob(
            city=self.city,
            input_path=self.input_path,
            output_path=self.output_path,
            conf_path=config.get_conf_path(self.city),
            ictdir=config.get_ictdir(self.ic_version),
            bashrc=config.bashrc,
            conda_sh=config.conda_sh,
            conda_activate=config.conda_activate,
            conda_lib=config.conda_lib,
        )


class ComparePmapSpec(NamedTuple):
    master_path: str
    pr_path: str
    output_path: str
    ic_version: str

    def get_job(self, config: Config) -> ComparePmapJob:
        return ComparePmapJob(
            master_path=self.master_path,
            pr_path=self.pr_path,
            output_path=self.output_path,
            ictdir=config.get_ictdir(self.ic_version),
            bashrc=config.bashrc,
            conda_sh=config.conda_sh,
            conda_activate=config.conda_activate,
            conda_lib=config.conda_lib,
        )


Spec = Union[CitySpec, ComparePmapSpec]

Job = Union[CityJob, ComparePmapJob]


class LocalAssembly(NamedTuple):
    master_path: str
    pr_path: str
    city_conf_dir: str

    def assemble_skeleton(self, config: Config, target_dir: str) -> None:
        os.mkdir(os.path.join(target_dir, "jobs"))
        os.mkdir(os.path.join(target_dir, "outputs"))
        os.mkdir(os.path.join(target_dir, "comparison_outputs"))

        shutil.copytree(self.city_conf_dir, os.path.join(target_dir, "conf"))
        shutil.copytree(self.master_path, os.path.join(target_dir, "master"))
        shutil.copytree(self.pr_path, os.path.join(target_dir, "pr"))

    def assemble_jobs(self, jobs: Sequence[Job], target_dir: str) -> None:

        # TODO: factor out this hardcode
        all_ok_file = "/data_extra2/icdev/miguel_scratch/all_ok"

        job_lines = []

        for i, job in enumerate(jobs):
            path = os.path.join(target_dir, "jobs", "job_{0}.sh".format(i))
            with open(path, "w") as f:
                f.write(job.to_sh())

            if i == 0:
                line = "job_0=$(qsub jobs/job_0.sh)"
            else:
                line = "job_{0}=$(qsub -W depend=afterok:$job_{1} jobs/job_{0}.sh)".format(
                    i, i - 1
                )
            job_lines.append(line)

        job_chain = "\n".join(job_lines)

        chain_sh = CHAIN_TEMPLATE.format(
            **dict(
                job_chain=job_chain,
                last_job="job_{0}".format(i),
                all_ok_file=all_ok_file,
            )
        )

        with open(os.path.join(target_dir, "chain.sh"), "w") as f:
            f.write(chain_sh)

        with open(os.path.join(target_dir, "jobs", "all_ok.sh"), "w") as f:
            all_ok_sh = ALL_OK_TEMPLATE.format(**dict(all_ok_file=all_ok_file))
            f.write(all_ok_sh)
