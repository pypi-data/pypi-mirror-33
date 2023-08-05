VTRTool
=======

[![PyPI Listing](https://img.shields.io/pypi/v/vtrtool.svg)](https://pypi.python.org/pypi/vtrtool)

Python utilities for Fullwave3D VTR model files.

The package contains a `vtrtool` executable, as well as a `vtrtool.py` python package


Installation
------------------------------------------

This tool can be obtained from PyPI. Simply do:

```
pip install vtrtool
```


`vtrtool` executable quick usage
------------------------------------------

`vtrtool -h` to show usage information

`vtrtool info my_model_file.vtr` shows metadata info for `my_model_file.vtr`

`vtrtool info nx1 my_model_file.vtr` prints out just the size of the 1st (x) dimension for `my_model_file.vtr`

`vtrtool to_binary --property=2 my_model_file.vtr my_model_file.bin` to dump the 2nd property from `my_model_file.vtr` to the float32 raw binary file `my_model_file.bin`

`vtrtool to_stdout my_model_file.vtr` to pipe the 1st property (default) from `my_model_file.vtr` to `stdout` in raw float32 binary format


`vtrtool.py` Python module quick usage
------------------------------------------

The `vtrtool.VTRModel` class represents a vtr model that lives at a given filename. The file will be parsed on object initialization:

```
import vtrtool

# read the vtr file `my_model_file.vtr` and construct a new VTRModel object with it
vtr_model = vtrtool.VTRModel("my_model_file.vtr")

# print model properties to stdout
vtrtool.print_vtr_metadata(vtr_model)

# model property 1 will be available as numpy ndarray in
vtr_model.arrays[0]

# model property 2 (if it exists) will be available as numpy ndarray in
vtr_model.arrays[1]

# etc...
```

Set the optional keyword `use_memmap=True` if you want the VTRModel object to use a [NumPy memmap](https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.memmap.html) instead of in-memory representation for holding the model array.

The following instance properties exist for objects of the `VTRModel` class:

- **file**: (str) the vtr filename referenced by the VTRModel object
- **num_dimensions**: (int) number of dimensions in the model
- **num_attributes**: (int) number of properties in the model
- **shape**: (tuple of ints) shape (c-based) of numpy ndarray holding the models in the order `(nx1, nx2, nx3)`
- **shape_fortran**: (tuple of ints) shape (fortran-based) of the models in the order `(nx3, nx2, nx1)`
- **nx1**: (int) number of cells in the 1st (usually x) dimension
- **nx2**: (int) number of cells in the 2nd (usually y) dimension
- **nx3**: (int) number of cells in the 3rd (fastest, usually z) dimension
- **arrays**: (list of ndarrays) holds the model property ndarrays, the length of the list correspond to the number of model properties (i.e., property 1 is in model[0]), and the shape of the ndarray will correspond to `shape` and with the number of dimensions in `num_dimensions`

### Some convenience functions:

- `vtrtool.vtrfile_to_ndarray(filename, prop_index=0)` quickly takes a vtr file and returns the property specified by `prop_index` as an ndarray
- `vtrtool.print_vtr_metadata(vtrmodel_object)` takes a VTRModel object and prints dimension information to stdout


**Maintained by**

Tim Lin <tlin@s-cube.com>, 2017