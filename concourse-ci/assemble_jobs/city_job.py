from typing import NamedTuple

CITY_JOB_TEMPLATE = """#!/bin/bash
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
