from typing import NamedTuple

COMPARE_PMAP_JOB_TEMPLATE = """#!/bin/bash
source {bashrc}
source {conda_sh}
conda activate {conda_activate}
export LD_LIBRARY_PATH="{conda_lib}:$LD_LIBRARY_PATH"
export ICTDIR={ictdir}
export ICDIR="$ICTDIR/invisible_cities"
export PATH="$ICTDIR/bin:$PATH"
export PYTHONPATH="$ICTDIR:$PYTHONPATH"

report=$(h5diff -c {master_path} {pr_path})
if [ $? -eq 0 ]; then
    echo "{master_path} {pr_path} ok" > {output_path}
else
    echo "{master_path} {pr_path} DIFFER" > {output_path}
    echo $'\\n' >> {output_path}
    echo "$report" >> {output_path}
fi
"""


class ComparePmapJob(NamedTuple):
    master_path: str
    pr_path: str
    output_path: str
    ictdir: str
    bashrc: str
    conda_sh: str
    conda_activate: str
    conda_lib: str

    def to_sh(self) -> str:
        return COMPARE_PMAP_JOB_TEMPLATE.format(**self._asdict())
