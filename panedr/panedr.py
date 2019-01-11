#-*- coding:utf-8 -*-
# Panedr -- a library to manipulate Gromacs EDR file in python
# Copyright (C) 2016  Jonathan Barnoud
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
Panedr -- Read Gromacs energy file (EDR) in python
==================================================

The ``panedr`` library allows to read and manipulate the content of Gromacs
energy file (.edr files) in python.

The current version of ``panedr`` tries to be in par with Gromacs 5.1.1 when
it comes to read EDR files.

So far, only one function is exposed by the library : the :fun:`edr_to_df`
function that returns a pandas ``DataFrame`` from an EDR file.

.. autofunction:: edr_to_df
"""

from __future__ import print_function

import xdrlib
import collections
import warnings
import sys
import itertools
import time
import pandas

#Index for the IDs of additional blocks in the energy file.
#Blocks can be added without sacrificing backward and forward
#compatibility of the energy files.

#For backward compatibility, the order of these should not be changed.


(enxOR,     # Time and ensemble averaged data for orientation restraints
 enxORI,    # Instantaneous data for orientation restraints
 enxORT,    # Order tensor(s) for orientation restraints
 ensDISRE,  # Distance restraint blocks
 enxDHCOLL, # Data about the free energy blocks in this frame
 enxDHHIST, # BAR histogram
 enxDH,     # BAR raw delta H data
 enxNR      # Total number of extra blocks in the current code,
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

__all__ = ['edr_to_df']


class EDRFile(object):
    def __init__(self, path):
        with open(path, 'rb') as infile:
            content = infile.read()
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
        bReadFirstStep = False
        data = self.data
        magic = data.unpack_int()

        if magic > 0:
            # Assume this is an old edr format
            file_version = 1
            nre = magic
            bOldFileOpen = True
        else:
            bOldFileOpen = False
            if magic != -55555:
                raise ValueError("Energy names magic number mismatch, this is not a GROMACS edr file")
            file_version = ENX_VERSION
            file_version = data.unpack_int()
            if (file_version > ENX_VERSION):
                raise ValueError('Reading file version {} with version {} implementation'.format(file_version, ENX_VERSION))
            nre = data.unpack_int()
        if file_version != ENX_VERSION:
            warnings.warn('Note: enx file_version {}, implementation version {}'.format(file_version, ENX_VERSION))
        nms = edr_strings(data, file_version, nre)

        self.file_version = file_version
        self.nre = nre
        self.nms = nms
        self.bOldFileOpen = bOldFileOpen
        self.bReadFirstStep = False

    def do_eheader(self, nre_test):
        data = self.data
        file_version = self.file_version
        fr = self.frame

        magic = -7777777
        zero = 0
        dum = 0
        tempfix_nr = 0
        ndisre = 0
        startb = 0

        bWrongPrecision = False
        bOK = True

        # We decide now whether we're single- or double-precision. Just peek
        # ahead and see whether we find the magic number where it should.
        base_pos = data.get_position()
        data.set_position(base_pos + 4)
        data.gmx_double = not is_frame_magic(data)
        data.set_position(base_pos)

        first_real_to_check = data.unpack_real()
        if first_real_to_check > -1e-10:
            # Assume we are reading an old format
            file_version = 1
            fr.t = first_real_to_check
            fr.step = data.unpack_int()
        else:
            if not is_frame_magic(data):
                raise ValueError("Energy header magic number mismatch, this is not a GROMACS edr file")
            file_version = data.unpack_int()
            if file_version > ENX_VERSION:
                raise ValueError('Reading file version {} with version {} implementation'.format(file_version, ENX_VERSION))
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
            if file_version >= 4:
                raise ValueError("Distance restraint blocks in old style in new style file")
            fr.nblock += 1
        # Frames could have nre=0, so we can not rely only on the fr.nre check
        if (nre_test >= 0
            and ((fr.nre > 0 and fr.nre != nre_test)
                 or fr.nre < 0 or ndisre < 0 or fr.nblock < 0)):
            bWrongPrecision = True
            return
        #  we now know what these should be, or we've already bailed out because
        #  of wrong precision
        if file_version == 1 and (fr.t < 0 or fr.t > 1e20 or fr.step < 0):
            raise ValueError("edr file with negative step number or unreasonable time (and without version number).")
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
                fr.block[b].sub[0].typr = dtreal
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

        # here, stuff about old versions

    def do_enx(self):
        data = self.data
        fr = self.frame

        file_version = -1
        framenr = 0
        frametime = 0
        try:
            self.do_eheader(-1)
        except ValueError:
            print("Last energy frame read {} time {:8.3f}".format(framenr - 1,
                                                                  frametime))
            raise RuntimeError()
        framenr += 1
        frametime = fr.t

        bSane = (fr.nre > 0)
        for block in fr.block:
            bSane |= (block.nsub > 0)
        if not (fr.step >= 0 and bSane):
            raise ValueError('Something went wrong')
        if fr.nre > fr.e_alloc:
            for i in range(fr.nre - fr.e_alloc):
                fr.ener.append(Energy(0, 0, 0))
            fr.e_alloc = fr.nre
        for i in range(fr.nre):
            fr.ener[i].e = data.unpack_real()
            if file_version == 1 or fr.nsum > 0:
                fr.ener[i].eav = data.unpack_real()
                fr.ener[i].esum = data.unpack_real()
                if file_version == 1:
                    # Old, unused real
                    data.unpack_real()

        # Old version stuff to add later

        # Read the blocks
        ndo_readers = (ndo_int, ndo_float, ndo_double,
                       ndo_int64, ndo_char, ndo_string)
        for block in fr.block:
            for sub in block.sub:
                try:
                    sub.val = ndo_readers[sub.type](data, sub.nr)
                except IndexError:
                    raise ValueError("Reading unknown block data type: this file is corrupted or from the future")



class Energy(object):
    __slot__ = ['e', 'eav', 'esum']

    def __init__(self, e=0, eav=0, esum=0):
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
        self.type = xdr_datatype_float  # should be double
                                        # if compile in double
        self.val = []
        self.val_alloc = 0

    def alloc(self):
        self.val = [0 for _ in range(self.nr)]
        self.vac_alloc = self.nr


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
    return [data.unpack_huge() for i in range(n)]


def ndo_char(data, n):
    """mimic of gmx_fio_ndo_char in gromacs"""
    return [data.unpack_char() for i in range(n)]


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


def edr_to_df(path, verbose=False):
    begin = time.time()
    edr_file = EDRFile(str(path))
    all_energies = []
    all_names = [u'Time'] + [nm.name for nm in edr_file.nms]
    times = []
    for ifr, frame in enumerate(edr_file):
        if verbose:
            if ((ifr < 20 or ifr % 10 == 0) and
                    (ifr < 200 or ifr % 100 == 0) and
                    (ifr < 2000 or ifr % 1000 == 0)):
                print('\rRead frame : {},  time : {} ps'.format(ifr, frame.t),
                      end='', file=sys.stderr)
        if frame.ener:
            # Export only frames that contain energies
            times.append(frame.t)
            all_energies.append([frame.t] + [ener.e for ener in frame.ener])

    end = time.time()
    if verbose:
        print('\rLast Frame read : {}, time : {} ps'
              .format(ifr, frame.t),
              end='', file=sys.stderr)
        print('\n{} frame read in {:.2f} seconds'.format(ifr, end - begin),
              file=sys.stderr)
    df = pandas.DataFrame(all_energies, columns=all_names, index=times)
    return df
