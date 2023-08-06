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

from sys import platform
import re
import argparse
import os
import subprocess
import os.path
import time
from os.path import expandvars, split, abspath

from isofit.common import expand_all_paths, json_load_ascii, spectrumLoad

sleep_time = 5
max_jobs = 10
template = '''#!/bin/bash
#PBS -l walltime={walltime}
#PBS -N MODTRAN6_{filenum}
export MODTRAN_DIR={modtran_dir}
export MODTRAN_DATA={modtran_data}
export PYTHONPATH={python_path}
export MODTRAN_LIC_SERVER={modtran_lic_server}
cd {lut_dir}
{modtran_cmd}'''


# How many PBS jobs are running? Parse the output of qstat
def jobs_in_queue():
    result = str(subprocess.check_output('qstat', shell=True), 'utf-8')
    username = os.getenv('USER')
    matches = [r for r in re.finditer(username, result)]
    return len(matches)


def main():

    description = 'Submit individual MODTRAN configs to the cluster'
    parser = argparse.ArgumentParser()
    parser.add_argument('--walltime', default='03:00:00')
    parser.add_argument('--modtran_dir', default=os.environ['MODTRAN_DIR'])
    parser.add_argument('--modtran_data', default=os.environ['MODTRAN_DATA'])
    parser.add_argument('--modtran_lic_server',
                        default=os.environ['MODTRAN_LIC_SERVER'])
    parser.add_argument('--pythonpath', default=os.getenv('PYTHONPATH'))
    parser.add_argument('infiles', nargs='+')
    args = parser.parse_args()

    jobs = []
    for filenum, filename in enumerate(args.infiles):

        # Specify location of the proper MODTRAN 6.0 binary for this OS
        infilepath = abspath(filename)
        xdir = {'linux': 'linux', 'darwin': 'macos', 'windows': 'windows'}
        cmd = args.modtran_dir+'/bin/'+xdir[platform]+'/mod6c_cons '+infilepath
        jobs.append((filenum, cmd))

    while len(jobs) > 0:

        if jobs_in_queue() < max_jobs:

            filenum, cmd = jobs[0]
            with open('.tmp', 'w') as fout:
                params = {'lut_dir': os.getcwd(),
                          'modtran_dir': args.modtran_dir,
                          'modtran_data': args.modtran_data,
                          'modtran_lic_server': args.modtran_lic_server,
                          'python_path': args.pythonpath,
                          'modtran_cmd': cmd,
                          'filenum': filenum,
                          'walltime': args.walltime}
                fout.write(template.format(**params))
            os.system('qsub .tmp')
            os.system('rm .tmp')
            del jobs[0]

        else:
            time.sleep(sleep_time)


if __name__ == '__main__':
    main()
