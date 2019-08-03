from typing import NamedTuple

COMPARE_KDST_JOB_TEMPLATE = """#!/bin/bash
source {bashrc}
source {conda_sh}
conda activate {conda_activate}
export LD_LIBRARY_PATH="{conda_lib}:$LD_LIBRARY_PATH"
export ICTDIR={ictdir}
export ICDIR="$ICTDIR/invisible_cities"
export PATH="$ICTDIR/bin:$PATH"
export PYTHONPATH="$ICTDIR:$PYTHONPATH"

mkdir {output_path}

h5diff -c {master_path} {pr_path} > {output_path}/h5diff.txt
if [ $? -eq 0 ]; then
    echo "ok" > {output_path}/status
else
    echo "DIFFERENCES" > {output_path}/status
fi
"""


class CompareKdstJob(NamedTuple):
    master_path: str
    pr_path: str
    output_path: str
    ictdir: str
    bashrc: str
    conda_sh: str
    conda_activate: str
    conda_lib: str

    def to_sh(self) -> str:
        return COMPARE_KDST_JOB_TEMPLATE.format(**self._asdict())
