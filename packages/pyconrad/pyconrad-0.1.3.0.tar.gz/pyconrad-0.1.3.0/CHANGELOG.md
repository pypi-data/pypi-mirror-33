# CHANGELOG

## 0.2.0 (unreleased)
* [x]  Deprecate usage of class PyGrid outside of pyconrad (until memory sharing is efficiently implemented)
* [ ]  Fork JPype to allow unified memory for numpy/Java?
* [ ]  OpenCL support:
  * [ ]  Efficient OpenCLMemory/create OpenCLGrid from pyopencl.array.Array
  * [ ]  Add more examples:
           e.g. use following projects gpyfft,gputools,DeepCL

## 0.1.3
* [x]  Add convinience methods:
        - pyconrad.close_all_windows,
        - pyconrad.imshow
        - pyconrad.to_conrad_grid

## 0.1.2
* [x]  Fix issue #12: Getting rid of the raw data opener
* [x]  Fix issue with cl.array.shape that changed to be of type list[np.int32] instead of list[int]

## 0.1.0

* [x]  Full support of VTK files (also reading)
* [x]  Improvements for conrad_imagej (support of relative paths, support for .npy-files)

## 0.0.9

* Conrad 1.0.8
* Example for custom pyopencl kernel on OpenCLGrids

## 0.0.8.3

* fix problem with MultiChannelGrid

## 0.0.8

* [x]  OpenCL support:
  * [x]  Get CONRAD's OpenCL device, command queue, context
  * [x]  Create OpenCLGrids from Numpy
  * [x]  Upload/Download numpy
  * [x]  Efficient OpenCLMemory/create OpenCLGrid from pyopencl.array.Array
  * [x]  Add example
* [x]  More convenience functions in pyopencl.config
* [x]  Better desktop integration for conrad_imagej:
    * [x]  Add .desktop files
    * [x]  Support for .vtk, .np and  .npz support
