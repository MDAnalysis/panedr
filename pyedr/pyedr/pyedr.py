# -*- coding:utf-8 -*-
# PyEDR -- a library to manipulate Gromacs EDR file in python
# Copyright (C) 2022  Jonathan Barnoud
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301  USA

# Most of this file is a python rewrite of part of
# `src/gromacs/fileio/enxio.c` from Gromacs 5.1.
# See gromacs.org.

"""
PyEDR -- Read Gromacs energy file (EDR) in python
==================================================

The ``pyedr`` library allows to read and manipulate the content of Gromacs
energy file (.edr files) in python.

The current version of ``pyedr`` tries to be in par with Gromacs 5.1.1 and
newer when it comes to reading EDR files.

The library exposes the following functions:

- the :func:`read_edr` function parses an EDR file and returns the energy terms
  in a nested list

- the :func:`edr_to_dict` function that turns the nested list created by
  :func:`read_edr` into a dictionary that maps term names to numpy arrays

.. autofunction:: edr_to_dict
"""
from mda_xdrlib import xdrlib
import collections
import warnings
from pathlib import Path
from tqdm import tqdm
from typing import List, Tuple, Dict

import numpy as np


# Index for the IDs of additional blocks in the energy file.
# Blocks can be added without sacrificing backward and forward
# compatibility of the energy files.

# For backward compatibility, the order of these should not be changed.
(
  enxOR,      # Time and ensemble averaged data for orientation restraints
  enxORI,     # Instantaneous data for orientation restraints
  enxORT,     # Order tensor(s) for orientation restraints
  enxDISRE,   # Distance restraint blocks
  enxDHCOLL,  # Data about the free energy blocks in this frame
  enxDHHIST,  # BAR histogram
  enxDH,      # BAR raw delta H data
  enxNR       # Total number of extra blocks in the current code,
              # note that the enxio code can read files written by
              # future code which contain more blocks.
) = range(8)

# xdr_datatype
# note that there is no data type 'real' because
# here we deal with the types as they are actually written to disk.
(xdr_datatype_int, xdr_datatype_float, xdr_datatype_double,
 xdr_datatype_int64, xdr_datatype_char, xdr_datatype_string) = range(6)

Enxnm = collections.namedtuple('Enxnm', 'name unit')
ENX_VERSION = 5

__all__ = ['ENX_VERSION', 'edr_to_dict', 'read_edr', 'get_unit_dictionary']


class EDRFile(object):
    def __init__(self, path):
        content = Path(path).read_bytes()
        self.data = GMX_Unpacker(content)
        self.do_enxnms()

    def __iter__(self):
        while True:
            try:
                self.frame = Frame()
                self.do_enx()
            except EOFError:
                return
            else:
                yield self.frame

    def do_enxnms(self):
        data = self.data
        magic = data.unpack_int()

        if magic > 0:
            # Assume this is an old edr format
            file_version = 1
            nre = magic
            bOldFileOpen = True
            self.bReadFirstStep = False
            # For file version 1: store previous energies for convert_full_sums
            self.ener_prev = [Energy() for _ in range(nre)]
        else:
            bOldFileOpen = False
            if magic != -55555:
                raise ValueError("Energy names magic number mismatch, "
                                 "this is not a GROMACS edr file")
            file_version = ENX_VERSION
            file_version = data.unpack_int()
            if (file_version > ENX_VERSION):
                raise ValueError(f'Reading file version {file_version} '
                                 f'with version {ENX_VERSION} implementation')
            nre = data.unpack_int()
        if file_version != ENX_VERSION:
            warnings.warn(f'Note: enx file_version {file_version}, '
                          f'implementation version {ENX_VERSION}')
        nms = edr_strings(data, file_version, nre)

        self.file_version = file_version
        self.nre = nre
        self.nms = nms
        self.bOldFileOpen = bOldFileOpen

    def do_eheader(self):
        data = self.data
        file_version = self.file_version
        fr = self.frame

        ndisre = 0
        startb = 0

        # We decide now whether we're single- or double-precision.
        base_pos = data.get_position()
        if self.file_version == 1:
            # Peek ahead check if nre matches value found in do_enxnms.
            # skip first_real_to_check:double(8) and step:int(4)
            data.set_position(base_pos + 12)
            nre = data.unpack_int()
            data.gmx_double = nre == self.nre
        else:
            # Just peek ahead and see whether we find the magic number
            # where it should be.
            # first_real_to_check:float(4)
            data.set_position(base_pos + 4)
            data.gmx_double = not is_frame_magic(data)
        data.set_position(base_pos)

        # Set expected datatype of subblocks
        dtreal = xdr_datatype_double if data.gmx_double else xdr_datatype_float

        first_real_to_check = data.unpack_real()
        if first_real_to_check > -1e-10:
            # Assume we are reading an old format
            if self.file_version != 1:
                raise ValueError('Expected file version 1, '
                                 f'found version {self.file_version}')
            fr.t = first_real_to_check
            fr.step = data.unpack_int()
        else:
            if not is_frame_magic(data):
                raise ValueError("Energy header magic number mismatch, "
                                 "this is not a GROMACS edr file")
            file_version = data.unpack_int()
            if file_version > ENX_VERSION:
                raise ValueError(f'Reading file version {file_version} '
                                 f'with version {ENX_VERSION} implementation')
            fr.t = data.unpack_double()
            fr.step = data.unpack_hyper()
            fr.nsum = data.unpack_int()
            if file_version >= 3:
                fr.nsteps = data.unpack_hyper()
            else:
                fr.nsteps = max(1, fr.nsum)
            if file_version >= 5:
                fr.dt = data.unpack_double()
            else:
                fr.dt = 0
        fr.nre = data.unpack_int()
        if file_version < 4:
            ndisre = data.unpack_int()
        else:
            # now reserved for possible future use
            data.unpack_int()
        fr.nblock = data.unpack_int()
        assert fr.nblock >= 0
        if ndisre != 0:
            # Distance restraint blocks of old style in new style file
            # ndisre is only read from file for older than 4 versions
            assert file_version < 4
            fr.nblock += 1
        # we now know what these should be,
        # or we've already bailed out because
        # of wrong precision
        if file_version == 1 and (fr.t < 0 or fr.t > 1e20 or fr.step < 0):
            raise ValueError("edr file with negative step number "
                             "or unreasonable time "
                             "(and without version number).")
        fr.add_blocks(fr.nblock)
        startb = 0
        if ndisre > 0:
            # sub[0] is the instantaneous data, sub[1] is time averaged
            fr.block[0].add_subblocks(2)
            fr.block[0].id = enxDISRE
            fr.block[0].sub[0].nr = ndisre
            fr.block[0].sub[1].nr = ndisre
            fr.block[0].sub[0].type = dtreal
            fr.block[0].sub[1].type = dtreal
            startb += 1
        # read block header info
        for b in range(startb, fr.nblock):
            if file_version < 4:
                # blocks in old version files always have 1 subblock that
                # consists of reals.
                fr.block[b].add_subblocks(1)
                nrint = data.unpack_int()
                fr.block[b].id = b - startb
                fr.block[b].sub[0].nr = nrint
                fr.block[b].sub[0].type = dtreal
            else:
                fr.block[b].id = data.unpack_int()
                nsub = data.unpack_int()
                fr.block[b].nsub = nsub
                fr.block[b].add_subblocks(nsub)
                for sub in fr.block[b].sub:
                    typenr = data.unpack_int()
                    sub.nr = data.unpack_int()
                    sub.type = typenr
        fr.e_size = data.unpack_int()
        # now reserved for possible future use
        data.unpack_int()
        data.unpack_int()

        # The following data is used in convert_full_sums
        # See do_eheader in enxio.cpp
        if file_version == 1:
            if not self.bReadFirstStep:
                # Store the first step
                self.bReadFirstStep = True
                self.first_step = fr.step
                self.step_prev = fr.step
                self.nsum_prev = 0
            self.frame.nsum = fr.step - self.first_step + 1
            self.frame.nsteps = fr.step - self.step_prev
            self.frame.dt = 0

    def do_enx(self):
        data = self.data
        fr = self.frame
        file_version = self.file_version

        framenr = 0
        frametime = 0
        try:
            self.do_eheader()
        except ValueError as e:
            print("Last energy frame read {} time {:8.3f}".format(framenr - 1,
                                                                  frametime))
            raise RuntimeError("Failed reading header") from e
        framenr += 1
        frametime = fr.t

        bSane = (fr.nre > 0)
        for block in fr.block:
            bSane |= (block.nsub > 0)
        if not (fr.step >= 0 and bSane):
            raise ValueError('Something went wrong')
        if fr.nre > fr.e_alloc:
            for i in range(fr.nre - fr.e_alloc):
                fr.ener.append(Energy())
            fr.e_alloc = fr.nre
        for i in range(fr.nre):
            fr.ener[i].e = data.unpack_real()
            if file_version == 1 or fr.nsum > 0:
                fr.ener[i].eav = data.unpack_real()
                fr.ener[i].esum = data.unpack_real()
                if file_version == 1:
                    # Old, unused real
                    data.unpack_real()

        # Here we can not check for file_version==1, since one could have
        # continued an old format simulation with a new one with mdrun -append.
        if self.bOldFileOpen:
            self.convert_full_sums()

        # Read the blocks
        ndo_readers = (ndo_int, ndo_float, ndo_double,
                       ndo_int64, ndo_char, ndo_string)
        for block in fr.block:
            for sub in block.sub:
                try:
                    sub.val = ndo_readers[sub.type](data, sub.nr)
                except IndexError:
                    raise ValueError("Reading unknown block data type: "
                                     "this file is corrupted "
                                     "or from the future")

    def convert_full_sums(self):
        """Convert old energy sums

        Old energy files seem to store the sums
        over all preceding energy frames.
        Therefore one has to calculate the difference between frames.
        See convert_full_sums in enxio.cpp
        """
        fr = self.frame

        first_step = self.first_step
        nsum_prev = self.nsum_prev
        step_prev = self.step_prev
        ener_prev = self.ener_prev

        if fr.nsum > 0:
            ne = ns = 0
            for ener in fr.ener:
                if ener.e != 0:
                    ne += 1
                if ener.esum != 0:
                    ns += 1
            if ne > 0 and ns == 0:
                # We do not have all energy sums
                fr.nsum = 0

        # Convert old full simulation sums to sums between energy frames
        nstep_all = fr.step - first_step + 1
        if fr.nsum > 1 and fr.nsum == nstep_all and nsum_prev > 0:
            # Set the new sum length: the frame step difference
            fr.nsum = fr.step - step_prev
            for i in range(fr.nre):
                esum_all = fr.ener[i].esum
                eav_all = fr.ener[i].eav
                fr.ener[i].esum = esum_all - ener_prev[i].esum
                fr.ener[i].eav = eav_all - ener_prev[i].eav \
                    - (ener_prev[i].esum
                       / (nstep_all - fr.nsum)
                       - esum_all / nstep_all)**2 \
                    * (nstep_all - fr.nsum) * nstep_all / fr.nsum
                ener_prev[i].esum = esum_all
                ener_prev[i].eav = eav_all
            nsum_prev = nstep_all
        elif fr.nsum > 0:
            # Conversion is only done for version 1 files
            # For those files, fr.nsum is always set
            # to nstep_all while parsing the header
            assert fr.nsum == nstep_all
            nsum_prev = nstep_all
            # Copy all sums to ener_prev
            for i in range(fr.nre):
                ener_prev[i].esum = fr.ener[i].esum
                ener_prev[i].eav = fr.ener[i].eav

        self.nsum_prev = nsum_prev
        self.step_prev = fr.step
        self.ener_prev = ener_prev


class Energy(object):
    __slot__ = ['e', 'eav', 'esum']

    def __init__(self):
        self.e = 0
        self.eav = 0
        self.esum = 0

    def __repr__(self):
        return '<{} e={}, eav={}, esum={}>'.format(type(self).__name__,
                                                   self.e, self.eav,
                                                   self.esum)


class SubBlock(object):
    def __init__(self):
        self.nr = 0
        # should be double if compile in double
        self.type = xdr_datatype_float
        self.val = []


class Block(object):
    def __init__(self):
        # See enxblock_init
        self.id = enxOR
        self.nsub = 0
        self.sub = []
        self.nsub_alloc = 0

    def add_subblocks(self, final_number):
        # See add_subblocks_enxblock
        self.nsub = final_number
        if final_number > self.nsub_alloc:
            for _ in range(final_number - self.nsub_alloc):
                self.sub.append(SubBlock())
            self.nsub_alloc = final_number


class Frame(object):
    def __init__(self):
        # See init_enxframe
        self.e_alloc = 0
        self.ener = []
        self.nblock = 0
        self.nblock_alloc = 0
        self.block = []

    def add_blocks(self, final_number):
        # See add_blocks_enxframe
        self.nblock = final_number
        if final_number > self.nblock_alloc:
            for _ in range(final_number - self.nblock_alloc):
                self.block.append(Block())
            self.nblock_alloc = final_number


class GMX_Unpacker(xdrlib.Unpacker):
    """xdrlib.Unpacker subclass that implements `unpack_real`

    Decision on whether to return 32- or 64-bit reals is controlled by the
    `gmx_double` attribute, set to ``False`` by default.
    """
    gmx_double = False

    def unpack_real(self):
        if self.gmx_double:
            return self.unpack_double()
        return self.unpack_float()


def ndo_int(data, n):
    """mimic of gmx_fio_ndo_int in gromacs"""
    return [data.unpack_int() for i in range(n)]


def ndo_float(data, n):
    """mimic of gmx_fio_ndo_float in gromacs"""
    return [data.unpack_float() for i in range(n)]


def ndo_double(data, n):
    """mimic of gmx_fio_ndo_double in gromacs"""
    return [data.unpack_double() for i in range(n)]


def ndo_int64(data, n):
    """mimic of gmx_fio_ndo_int64 in gromacs"""
    return [data.unpack_hyper() for i in range(n)]


def ndo_char(data, n):
    """mimic of gmx_fio_ndo_char in gromacs"""
    # Note: chars are encoded as int(32)
    return [data.unpack_int() for i in range(n)]


def ndo_string(data, n):
    """mimic of gmx_fio_ndo_string in gromacs"""
    return [data.unpack_string() for i in range(n)]


def edr_strings(data, file_version, n):
    nms = []
    for i in range(n):
        name = data.unpack_string().decode('ascii')
        if file_version >= 2:
            unit = data.unpack_string().decode('ascii')
        else:
            unit = 'kJ/mol'
        nms.append(Enxnm(name=name, unit=unit))
    return nms


def is_frame_magic(data):
    """Unpacks an int and checks whether it matches the EDR frame magic number

    Does not roll the reading position back.
    """
    magic = data.unpack_int()
    return magic == -7777777


all_energies_type = List[List[float]]
all_names_type = List[str]
times_type = List[float]
read_edr_return_type = Tuple[all_energies_type,
                             all_names_type,
                             times_type]


def read_edr(path: str, verbose: bool = False) -> read_edr_return_type:
    """Parse EDR files and make contents available in Python

    :func:`read_edr` does the actual reading of EDR files. It is called by
    :func:`edr_to_df` and :func:`edr_to_dict` to provide the file contents.
    Under the hood, it is using :class:`xdrlib.Unpacker` to access the binary
    EDR file.

    Parameters
    ----------
    path : str
        path to EDR file to be read
    verbose : bool
        Optionally show verbose output while reading the file

    Returns
    -------
    all_energies: list[list[float]]
        A nested containing the energy values for each frame found in the EDR
        file
    all_names: list[str]
        A list containing the names of the energy terms found in the file
    times: list[float]
        A list containing the time of each step/frame.
    """
    edr_file = EDRFile(path)
    all_energies = []
    all_names = [u'Time'] + [nm.name for nm in edr_file.nms]
    times = []
    for ifr, frame in tqdm(enumerate(edr_file), disable=(not verbose)):
        if frame.ener:
            # Export only frames that contain energies
            times.append(frame.t)
            all_energies.append([frame.t] + [ener.e for ener in frame.ener])
    return all_energies, all_names, times


def get_unit_dictionary(path: str) -> Dict[str, str]:
    """Creates an EDRFile object which executes the :func:`do_enxnms`
    method. This reads the names and units of the EDR data, which is returned
    as a dictionary mapping column names (str) to unit names (str).

    Parameters
    ----------
    path : str
        path to EDR file to be read

    Returns
    -------
    unit_dict: Dict[str, str]
        A dictionary mapping the term names to their units.
    """
    edr_file = EDRFile(path)
    unit_dict = {'Time': "ps"}
    for nm in edr_file.nms:
        unit_dict[nm.name] = nm.unit
    return unit_dict


def edr_to_dict(path: str, verbose: bool = False) -> Dict[str, np.ndarray]:
    """Calls :func:`read_edr` and packs its return values into a dictionary

    The returned dictionary's keys are the names of the energy terms present in
    the EDR file, the values are the time-series energy data for those terms.

    Parameters
    ----------
    path : str
        path to EDR file to be read
    verbose : bool
        Optionally show verbose output while reading the file

    Returns
    -------
    enery_dict: dict[str, np.ndarray]
        dictionary that holds all energy terms found in the EDR file.
    """
    all_energies, all_names, times = read_edr(path, verbose=verbose)
    energy_dict = {}
    for idx, name in enumerate(all_names):
        energy_dict[name] = np.array(
            [all_energies[frame][idx] for frame in range(len(times))])
    return energy_dict
