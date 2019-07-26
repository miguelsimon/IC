import os
import shutil
from typing import List, NamedTuple

CITY_JOB_TEMPLATE = """
source {bashrc}
source {conda_sh}
conda activate {conda_activate}
export LD_LIBRARY_PATH="{conda_lib}:$LD_LIBRARY_PATH"
export ICTDIR={ictdir}
export ICDIR="$ICTDIR/invisible_cities"
export PATH="$ICTDIR/bin:$PATH"
export PYTHONPATH="$ICTDIR:$PYTHONPATH"

city {city} \\
    -i {input_path} \\
    -o {output_path}  \\
    {conf_path}
"""


class CityJob(NamedTuple):
    city: str
    input_path: str
    output_path: str
    conf_path: str
    ictdir: str
    bashrc: str
    conda_sh: str
    conda_activate: str
    conda_lib: str

    def to_sh(self) -> str:
        return CITY_JOB_TEMPLATE.format(**self._asdict())


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


class LocalAssembly(NamedTuple):
    master_path: str
    pr_path: str
    city_conf_dir: str

    def assemble_skeleton(self, config: Config, target_dir: str) -> None:
        os.mkdir(os.path.join(target_dir, "jobs"))
        shutil.copytree(self.city_conf_dir, os.path.join(target_dir, "conf"))
        shutil.copytree(self.master_path, os.path.join(target_dir, "master"))
        shutil.copytree(self.pr_path, os.path.join(target_dir, "pr"))

    # TODO: add job chaining script to tie these together see https://www.nics.tennessee.edu/computing-resources/running-jobs/job-chaining
    def assemble_jobs(self, jobs: List[CityJob], target_dir: str) -> None:
        chain_sh = ["#!/bin/bash"]

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
            chain_sh.append(line)

        chain_sh.append("")
        with open(os.path.join(target_dir, "chain.sh"), "w") as f:
            f.write("\n".join(chain_sh))
