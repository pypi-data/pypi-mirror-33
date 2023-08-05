from .vtrmodel import VTRModel


def vtrfile_to_ndarray(filename, prop_index=0):
    """
    Convenience function to read a VTR file and return an NDarray
    that points to the `prop_index`-th property (0 is first, default)

    :param filename: file name of VTR file to read
    :type filename: str
    :param prop_index: desired property index (zero-based indexing), defaults to 0
    :type prop_index: int, optional
    :returns: a NumPy NDArray instance holding the desired model property
    :rtype: numpy.ndarray
    :raises: IOError
    """
    vtr = VTRModel(filename)
    if not vtr._file_exists():
        raise IOError("specified vtr file does not exist")
    return vtr.arrays[prop_index]


def print_vtr_metadata(vtr_object):
    """
    Quick diagnostic tool for printing the metadata of VTR objects

    :param vtr_object: input vtr model object
    :type vtr_object: VTRModel
    """
    print("VTR filename: ", vtr_object.file)
    print("Number of properties: ", vtr_object.num_properties)
    print("Number of dimensions: ", vtr_object.num_dimensions)
    print("NX1: ", vtr_object.nx1)
    print("NX2: ", vtr_object.nx2)
    print("NX3(fastest): ", vtr_object.nx3)
