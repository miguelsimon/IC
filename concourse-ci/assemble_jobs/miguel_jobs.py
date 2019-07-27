import argparse

from assemble_jobs.ic_jobs import CitySpec, Config, LocalAssembly

config = Config(
    bashrc="/home/icdev/.bashrc",
    conda_sh="/home/icdev/miniconda/etc/profile.d/conda.sh",
    conda_activate="IC-3.7-2018-11-14",
    conda_lib="/home/icdev/miniconda/lib",
    remote_dir="/data_extra2/icdev/miguel_scratch",
)

specs = [
    CitySpec(
        city="irene",
        input_path="/data_extra2/mmkekic/example_inputs/run_6971_0009_trigger1_waveforms.h5",
        output_path="/data_extra2/icdev/miguel_scratch/outputs/master_run_6971_0009_trigger1_pmaps.h5",
        ic_version="master",
    ),
    CitySpec(
        city="dorothea",
        input_path="/data_extra2/icdev/miguel_scratch/outputs/master_run_6971_0009_trigger1_pmaps.h5",
        output_path="/data_extra2/icdev/miguel_scratch/outputs/master_run_6971_0009_trigger1_kdst.h5",
        ic_version="master",
    ),
    CitySpec(
        city="irene",
        input_path="/data_extra2/mmkekic/example_inputs/run_6971_0009_trigger1_waveforms.h5",
        output_path="/data_extra2/icdev/miguel_scratch/outputs/pr_run_6971_0009_trigger1_pmaps.h5",
        ic_version="pr",
    ),
    CitySpec(
        city="dorothea",
        input_path="/data_extra2/icdev/miguel_scratch/outputs/pr_run_6971_0009_trigger1_pmaps.h5",
        output_path="/data_extra2/icdev/miguel_scratch/outputs/pr_run_6971_0009_trigger1_kdst.h5",
        ic_version="pr",
    ),
]

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
