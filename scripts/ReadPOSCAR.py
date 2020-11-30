import os
import math
import re
import numpy as np

_POSCAR_DefaultTitleLine = "Unknown Structure"


def ReadPOSCAR(filePath):
    """
    Read a crystal structure from a VASP POSCAR file.

    Return value:
        A tuple of (title_line, lattice_vectors, atomic_symbols, atom_positions_frac) data.

    Notes:
        If the title line is blank, it will be set to the _POSCAR_DefaultTitleLine constant.
        This function only supports VASP 5.x-format POSCAR files (i.e. with atomic symbols as well as counts given in the header).
        Negative scale factors on line 2, interpreted by VASP as the volume of the cell, are not supported.
    """

    titleLine = None
    latticeVectors = None
    atomicSymbols, atomPositions = None, None

    with open(filePath, "r") as inputReader:
        # Read title from line 1.

        titleLine = next(inputReader).strip()

        if titleLine == "":
            titleLine = _POSCAR_DefaultTitleLine

        # Read scale factor.
        scaleFactor = float(next(inputReader).strip())
        if scaleFactor < 0.0:
            raise Exception(
                'Error: Unsupported negative scale factor in input file "{0}".'.format(
                    filePath
                )
            )

        # Read lattice vectors.

        latticeVectors = []

        for i in range(0, 3):
            latticeVectors.append(
                [float(item) for item in next(inputReader).strip().split()[:3]]
            )

        latticeVectors = [
            scaleFactor * np.array(v, dtype=np.float64) for v in latticeVectors
        ]

        # Read atom types and positions.

        atomTypes = next(inputReader).strip().split()

        atomCounts = None

        try:
            atomCounts = [int(item) for item in next(inputReader).strip().split()]
        except ValueError:
            raise Exception(
                'Error: Failed to read atom counts from input file "{0}".'.format(
                    filePath
                )
            )

        if len(atomTypes) != len(atomCounts):
            raise Exception(
                'Error: Inconsistent number of atom types and atom counts in input file "{0}".'.format(
                    filePath
                )
            )

        atomicSymbols = []

        for atomType, atomCount in zip(atomTypes, atomCounts):
            atomicSymbols = atomicSymbols + [atomType] * atomCount

        # Check for direct or Cartesian coordinates.

        key = next(inputReader).strip()[0].lower()

        if key == "s":
            # Selective dynamics keyword -> read first letter of the following line.

            key = next(inputReader).strip()[0].lower()

        coordinateType = None

        if key == "c" or key == "k":
            coordinateType = "cartesian"
        elif key == "d":
            coordinateType = "fractional"
        else:
            raise Exception(
                'Error: Unknown coordinate type in input file "{0}".'.format(filePath)
            )

        # Read atomic positions.

        atomPositions = []

        for i in range(0, sum(atomCounts)):
            atomPositions.append(
                [float(item) for item in next(inputReader).strip().split()[:3]]
            )

        atomPositions = [np.array(v, dtype=np.float64) for v in atomPositions]

        if coordinateType == "cartesian":
            # Scale and convert to fractional coordinates.

            atomPositions = Utilities.CartesianToFractionalCoordinates(
                [scaleFactor * v for v in atomPositions], latticeVectors
            )

    return (titleLine, latticeVectors, atomicSymbols, atomPositions)


def getPositionVectors(filepath):
    filepath = input("Input POSCAR file path : ")
    latticeVectors = np.array(ReadPOSCAR(filepath)[1])
    atoms = np.array(ReadPOSCAR(filepath)[2])
    positions = np.array(ReadPOSCAR(filepath)[3])

    positionsWithAtoms = pd.DataFrame(
        {
            "a": positions[:, 0],
            "b": positions[:, 1],
            "c": positions[:, 2],
            "atom": atoms,
        }
    )

    return positionsWithAtoms
