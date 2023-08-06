import pyconrad
import sys
import os
from os.path import basename, isfile, abspath
import numpy as np
import argparse


_ = pyconrad.ClassGetter()


def start_pyconrad(*args, **kwargs):
    pyconrad.setup_pyconrad()
    pyconrad.start_reconstruction_pipeline_gui()


def start_conrad_imagej(*args, **kwargs):

    parser = argparse.ArgumentParser(
        'Starts an instance of ImageJ with CONRAD\'s extensions')
    parser.add_argument('filenames', nargs='*', help='Files to open')
    parser.add_argument('--max_memory', type=int, default=8,
                        help='Maximum memory for Java heap space in gigabytes')
    args = parser.parse_args()

    pyconrad.setup_pyconrad(max_ram='%iG' % args.max_memory)
    pyconrad.start_gui()

    for f in args.filenames:
        try:
            filename = basename(f)
            if isfile(f):
                f = abspath(f)
                if str.lower(f).endswith('.vtk') or str.lower(f).endswith('.vti'):
                    _.NumericGrid.from_vtk(f).show(filename)
                elif str.lower(f).endswith('.npy'):
                    numpy_array = np.load(f)
                    _.NumericGrid.from_numpy(numpy_array).show(filename)
                elif str.lower(f).endswith('.np') or str.lower(f).endswith('.npz'):
                    file_object = np.load(f)
                    for key in file_object.keys():
                        numpy_array = file_object[key]
                        _.NumericGrid.from_numpy(numpy_array).show(key)

                else:
                    pyconrad.ij().IJ.openImage(
                        f).show(basename(f))

        except Exception as e:
            print(e)


if __name__ == "__main__":
    start_pyconrad()
