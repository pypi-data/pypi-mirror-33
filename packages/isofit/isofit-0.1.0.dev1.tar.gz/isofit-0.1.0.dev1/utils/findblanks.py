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

import argparse
import sys
from spectral.io import envi


def main():

    description = 'Submit individual lines of a flightline to the cluster'
    parser = argparse.ArgumentParser()
    parser.add_argument('rdnfile')
    args = parser.parse_args()

    # Setup
    I = envi.open(args.rdnfile+'.hdr', args.rdnfile)
    x = I.read_band(0)
    for i in range(x.shape[0]):
        if all(x[i, :] == 0):
            sys.stdout.write('%i\n' % i)


if __name__ == '__main__':
    main()
