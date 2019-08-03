import argparse
import os
import re
from typing import List

from assemble_jobs.ic_jobs import CitySpec, ComparePmapSpec, Config, LocalAssembly, Spec

config = Config(
    bashrc="/home/icdev/.bashrc",
    conda_sh="/home/icdev/miniconda/etc/profile.d/conda.sh",
    conda_activate="IC-3.7-2018-11-14",
    conda_lib="/home/icdev/miniconda/lib",
    remote_dir="/data_extra2/icdev/miguel_scratch",
)

inputs = """run_6971_0324_trigger1_waveforms.h5  run_6971_0658_trigger1_waveforms.h5  run_6971_0992_trigger1_waveforms.h5
run_6971_0325_trigger1_waveforms.h5  run_6971_0659_trigger1_waveforms.h5  run_6971_0993_trigger1_waveforms.h5
run_6971_0326_trigger1_waveforms.h5  run_6971_0660_trigger1_waveforms.h5  run_6971_0994_trigger1_waveforms.h5
run_6971_0327_trigger1_waveforms.h5  run_6971_0661_trigger1_waveforms.h5  run_6971_0995_trigger1_waveforms.h5
run_6971_0328_trigger1_waveforms.h5  run_6971_0662_trigger1_waveforms.h5  run_6971_0996_trigger1_waveforms.h5
run_6971_0329_trigger1_waveforms.h5  run_6971_0663_trigger1_waveforms.h5  run_6971_0997_trigger1_waveforms.h5
run_6971_0330_trigger1_waveforms.h5  run_6971_0664_trigger1_waveforms.h5  run_6971_0998_trigger1_waveforms.h5
run_6971_0331_trigger1_waveforms.h5  run_6971_0665_trigger1_waveforms.h5  run_6971_0999_trigger1_waveforms.h5""".split()

specs: List[Spec] = []

for filename in inputs:
    pmap_filename = re.sub("waveforms", "pmaps", filename)
    input_path = os.path.join("/analysis/6971/hdf5/data", filename)

    for branch in ["master", "pr"]:
        output_path = os.path.join(
            "/data_extra2/icdev/miguel_scratch/outputs/", branch, pmap_filename
        )
        specs.append(
            CitySpec(
                city="irene",
                input_path=input_path,
                output_path=output_path,
                ic_version=branch,
            )
        )

    specs.append(
        ComparePmapSpec(
            master_path=os.path.join(
                "/data_extra2/icdev/miguel_scratch/outputs/", "master", pmap_filename
            ),
            pr_path=os.path.join(
                "/data_extra2/icdev/miguel_scratch/outputs/", "pr", pmap_filename
            ),
            output_path=os.path.join(
                "/data_extra2/icdev/miguel_scratch/comparison_outputs", pmap_filename
            ),
            ic_version="master",
        )
    )

jobs = [spec.get_job(config) for spec in specs]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--target_dir", type=str, required=True)

    parser.add_argument(
        "--master_dir",
        type=str,
        required=True,
        help="source directory to use as master",
    )

    parser.add_argument(
        "--pr_dir", type=str, required=True, help="source directory to use as pr"
    )

    parser.add_argument(
        "--city_conf_dir",
        type=str,
        required=True,
        help="source directory where city configurations are found",
    )

    args = parser.parse_args()

    local_assembly = LocalAssembly(
        master_path=args.master_dir,
        pr_path=args.pr_dir,
        city_conf_dir=args.city_conf_dir,
    )

    local_assembly.assemble_skeleton(config, args.target_dir)
    local_assembly.assemble_jobs(jobs, args.target_dir)
