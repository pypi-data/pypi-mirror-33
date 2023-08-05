#!/usr/bin/env python
"""
Utility to parse and manipulate Fullwave3D VTR files

vtrtool info         prints metadata concerning the VTR file
    (you can additionally specify just the property to print, e.g.,
    `vtrtool info nx1 file.vtr` will just print out the 1st dimension of file.vtr)
vtrtool to_binary    converts a VTR file to a single-property float32 binary file
vtrtool to_stdout    reads a VTR file and pipes the float32 binary model property to stdout
    (--property=<index> specifies the <index-th> property in the VTR file to convert,
     starting with 1)

Usage:
    vtrtool info      [(ndims|nprops|nx1|nx2|nx3)] <vtr_filename>
    vtrtool to_binary [--property=<index>] <vtr_filename> <bin_filename>
    vtrtool to_stdout [--property=<index>] <vtr_filename>

Options:
    -h --help       Show this help

"""
from __future__ import print_function
import sys
import vtrtool
import docopt


def main():

    arguments = docopt.docopt(__doc__, version=vtrtool.__version__)

    if arguments["info"]:
        # prints metadata concerning the VTR file
        vtr = vtrtool.VTRModel(arguments["<vtr_filename>"], read_model=False)
        if arguments["ndims"]:
            print(vtr.num_dimensions)
        elif arguments["nprops"]:
            print(vtr.num_properties)
        elif arguments["nx1"]:
            print(vtr.nx1)
        elif arguments["nx2"]:
            print(vtr.nx2)
        elif arguments["nx3"]:
            print(vtr.nx3)
        else:
            vtrtool.print_vtr_metadata(vtr)
    elif (arguments["to_binary"] or arguments["to_stdout"]):
        # converts a VTR file to a single-property float32 binary file, or
        # pipe the float32 binary model property to stdout
        vtr = vtrtool.VTRModel(arguments["<vtr_filename>"])
        if arguments["--property"]:
            prop_index = int(arguments["--property"]) - 1  # CLI uses Fortran index
        else:
            prop_index = 0  # first property
        model = vtr.arrays[prop_index]
        if arguments["to_binary"]:
            vtrtool.print_vtr_metadata(vtr)
            print("Dumping property", prop_index + 1)
            model.tofile(arguments["<bin_filename>"], sep="")
        elif arguments["to_stdout"]:
            model.tofile(sys.stdout, sep="")
    else:
        pass


if __name__ == '__main__':
    main()
