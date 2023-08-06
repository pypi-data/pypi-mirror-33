
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import jpype
import numpy as np
import pyconrad
import sys

try:
    import pycuda.gpuarray as gpuarray
except ImportError:
    pass


class ImageUtil:

    ########################
    ## Convert Grid/numpy ##
    ########################

    @staticmethod
    def grid_from_numpy(grid):
        return np.ndarray.view(pyconrad.PyGrid.from_numpy(grid))

    @staticmethod
    def numpy_from_grid(ndarray):
        return np.ndarray.view(pyconrad.PyGrid.from_grid(ndarray))

    #################
    ## Save Images ##
    #################

    @staticmethod
    def save_grid_as_tiff(grid, path):
        jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    @staticmethod
    def save_numpy_as_tiff(array, path):
        grid = ImageUtil.grid_from_numpy(array)
        jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.saveAs(grid, path)

    #################
    ## Load Images ##
    #################

    @staticmethod
    def grid_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return grid

    @staticmethod
    def array_from_tiff(path):
        ij = jpype.JPackage('ij').IJ.openImage(path)
        if not ij:
            raise RuntimeError('Error opening file \'%s\'' % path)
        grid = jpype.JPackage(
            'edu').stanford.rsl.conrad.utils.ImageUtil.wrapImagePlus(ij)
        return ImageUtil.numpy_from_grid(grid)


def to_conrad_grid(img):

    if isinstance(img, pyconrad.edu().stanford.rsl.conrad.data.numeric.NumericGrid):
        grid = img
    elif isinstance(img, pyconrad.PyGrid):
        grid = img.grid
    elif isinstance(img, np.ndarray):
        grid = pyconrad.PyGrid.from_numpy(img.astype(
            pyconrad.java_float_dtype))
    elif 'pycuda' in sys.modules and isinstance(img, gpuarray.GPUArray):
        grid = pyconrad.PyGrid.from_numpy(img.get().astype(
            pyconrad.java_float_dtype))
    elif isinstance(img, list):
        imgs = np.stack(img)
        grid = pyconrad.PyGrid.from_numpy(imgs.astype(
            pyconrad.java_float_dtype))
    else:
        raise TypeError('Unsupported Type')

    return grid


def imshow(img, title="", wait_key_press=False):

    if not pyconrad.is_gui_started():
        pyconrad.start_gui()

    grid = to_conrad_grid(img)

    window = pyconrad.ij().WindowManager.getImage(title) if title else None

    if window:
        grid = pyconrad.PyGrid.from_numpy(img.astype(
            pyconrad.java_float_dtype)).grid
        imageplus = pyconrad.stanfordrsl().conrad.utils.ImageUtil.wrapGrid(grid, title)
        window.setImage(imageplus)
    else:
        grid.show(title)

    if wait_key_press:
        input("press key")
