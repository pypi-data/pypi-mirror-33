#! /usr/bin/env python3
#
#  Copyright 2018 California Institute of Technology
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ISOFIT: Imaging Spectrometer Optimal FITting
# Author: David R Thompson, david.r.thompson@jpl.nasa.gov
#

import re
import argparse
import os
import sys
import subprocess
import os.path
import time
from os.path import expandvars, split, abspath
from spectral.io import envi

from isofit.common import expand_all_paths, json_load_ascii, spectrumLoad

sleep_time = 5
max_jobs = 30
template = '''#!/bin/bash
#PBS -l walltime={walltime}
export ISOFIT_BASE={isofit_base}
export MODTRAN_DIR={modtran_dir}
export PYTHONPATH={python_path}
{python_exe} {isofit_base}/isofit/isofit.py --row_column {row} {config}'''


# How many PBS jobs are running? Parse the output of qstat
def jobs_in_queue():
    result = str(subprocess.check_output('qstat', shell=True), 'utf-8')
    username = os.getenv('USER')
    matches = [r for r in re.finditer(username, result)]
    return len(matches)


def main():

    description = 'Submit individual lines of a flightline to the cluster'
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('--walltime', default='03:00:00')
    parser.add_argument('--lines_list', default='')
    parser.add_argument('--start_line', default=0)
    args = parser.parse_args()
    config_file = abspath(args.config_file)

    # Setup
    config = json_load_ascii(config_file)
    configdir, f = split(config_file)
    config = expand_all_paths(config, configdir)
    rdnfile = config['input']['measured_radiance_file']
    I = envi.open(rdnfile+'.hdr', rdnfile)
    jobs = list(range(int(args.start_line), I.nrows))
    if len(args.lines_list) > 0:
        with open(args.lines_list, 'r') as fin:
            jobs = [int(line) for line in fin.readlines()]

    while len(jobs) > 0:

        if jobs_in_queue() < max_jobs:

            line = jobs[0]
            with open('.tmp', 'w') as fout:
                params = {'row': line, 'config': config_file,
                          'isofit_base': os.getenv('ISOFIT_BASE'),
                          'modtran_dir': os.getenv('MODTRAN_DIR'),
                          'python_path': os.getenv('PYTHONPATH'),
                          'python_exe': sys.executable,
                          'walltime': args.walltime}
                fout.write(template.format(**params))
            os.system('qsub .tmp')
            os.system('rm .tmp')
            del jobs[0]

        else:
            time.sleep(sleep_time)


if __name__ == '__main__':
    main()
