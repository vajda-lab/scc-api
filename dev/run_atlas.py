#!/usr/bin/env python
# $ -pe omp 16


import os, sys

pdb_file = "replace1"


nslots = os.getenv("NSLOTS", None)

if nslots is not None:
    os.environ["OMP_NUM_THREADS"] = nslots

os.system(
    "/projectnb/docking/awake/atlas-1.7.3/atlas_package/bin/run_atlas {0}".format(
        pdb_file
    )
)
