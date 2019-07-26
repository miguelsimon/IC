import os
import tempfile
import unittest

from assemble_jobs.ic_jobs import CitySpec, Config, LocalAssembly


class Test(unittest.TestCase):
    def get_config(self):
        return Config(
            bashrc="/home/icdev/.bashrc",
            conda_sh="/home/icdev/miniconda/etc/profile.d/conda.sh",
            conda_activate="IC-3.7-2018-11-14",
            conda_lib="home/icdev/miniconda/lib",
            remote_dir="home/data_extra2/icdev/miguel_scratch",
        )

    def test_Config(self):
        config = self.get_config()

        print(config.get_conf_path("irene"))
        print(config.get_ictdir("master"))

    def test_CitySpec_CityJob(self):
        config = self.get_config()
        spec = CitySpec(
            city="irene",
            input_path="/data_extra2/mmkekic/example_inputs/run_6971_0009_trigger1_waveforms.h5",
            output_path="/data_extra2/icdev/miguel_scratch/outputs/run_6971_0009_trigger1_pmaps.h5",
            ic_version="master",
        )

        job = spec.get_job(config)
        print(job)
        print(job.to_sh())

    def test_LocalAssembly(self):
        config = self.get_config()
        spec = CitySpec(
            city="irene",
            input_path="/data_extra2/mmkekic/example_inputs/run_6971_0009_trigger1_waveforms.h5",
            output_path="/data_extra2/icdev/miguel_scratch/outputs/run_6971_0009_trigger1_pmaps.h5",
            ic_version="master",
        )

        jobs = [spec.get_job(config)]
        with tempfile.TemporaryDirectory() as dummy_ic_dir:
            local_assembly = LocalAssembly(
                master_path=dummy_ic_dir,
                pr_path=dummy_ic_dir,
                city_conf_dir=dummy_ic_dir,
            )

            with tempfile.TemporaryDirectory() as target_dir:
                local_assembly.assemble_skeleton(config, target_dir)
                print(os.listdir(target_dir))
                local_assembly.assemble_jobs(jobs, target_dir)
