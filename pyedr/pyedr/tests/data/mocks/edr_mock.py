# -*- coding: utf-8 -*-
# Helper script to generate mock EDR files with manipulated values. This allows
# setting some values in EDR files in such a way that certain conditions can be
# triggered while parsing. Note that not all parameter combinations are
# sensible and produce valid EDR files.

import xdrlib
from dataclasses import dataclass

MAGIC = -55555  # File magic number
ENX_VERSION = 4  # File version
assert ENX_VERSION >= 1
NSUM = 0  # Value of fr.nsum
# Column names with associated units (units are ignored for version 1)
# These values are parsed in do_enxnms and stored as fr.nms
NMS = [("DUMMY1", "UNIT1"), ("DUMMY2", "UNIT2")]
NRE = len(NMS)  # Derive number of columns from NMS
FIRST_REAL = -1.0  # Value of first_real_to_check in do_eheader
FRAME_MAGIC = -7777777  # Frame magic number
NSTEPS = 3  # Number of steps to write
# Time step between frames
# Frame times are simply set to step*DT
DT = 0.5
NDISRE = 0  # Number of distance restraints (can be > 0 for versions < 4)
E_SIZE = 0  # Value to write as fr.e_size


@dataclass
class Block:
    bid: int  # block id
    sub: []  # list of sub blocks


@dataclass
class SubBlock:
    nr: int  # number of values stored in sub block
    btype: int  # type of stored values


# Option 1: Write no other data blocks

BLOCKS = []

# Option 2: Write blocks of every possible sub-block type

# BLOCKS = []
# for t in range(6):
# bid = t + 3  # generate some arbitrary block id
# sub_nr1 = 7 - t  # and nr of values in the sub block
# sub_nr2 = 6 - t
# BLOCKS.append(Block(bid, [SubBlock(sub_nr1, t), SubBlock(sub_nr2, t)]))

# Option 3: Write a block with an invalid sub-block type (> 5)

# BLOCKS = [Block(7, [SubBlock(2, 0), SubBlock(1, 1_000_000_000)])]

# Option 4: Write some additional distance restraints
# and optionally some more blocks
# Version must be set to < 4
# Note from pyedr: blocks in old version files always have 1 subblock
# that consists of reals

# NDISRE = 2
# BLOCKS = []
# for i in range(3):
# BLOCKS.append(Block(i, [SubBlock(4, 1)]))
# ENX_VERSION = 3

NBLOCK = len(BLOCKS)

p = xdrlib.Packer()

# do_enxnms
if ENX_VERSION == 1:
    p.pack_int(NRE)
else:
    p.pack_int(MAGIC)
    p.pack_int(ENX_VERSION)
    p.pack_int(NRE)
for nm, u in NMS:
    p.pack_string(nm.encode("ascii"))
    if ENX_VERSION >= 2:
        p.pack_string(u.encode("ascii"))

for step in range(NSTEPS):
    t = step * DT  # Just set some value for fr.t
    # do_enx
    # -> do_eheader
    if ENX_VERSION == 1:
        p.pack_float(t)
        p.pack_int(step)
    else:
        p.pack_float(FIRST_REAL)
        p.pack_int(FRAME_MAGIC)
        p.pack_int(ENX_VERSION)
        p.pack_double(t)
        p.pack_hyper(step)
        p.pack_int(NSUM)
        if ENX_VERSION >= 3:
            p.pack_hyper(NSTEPS)
        if ENX_VERSION >= 5:
            p.pack_double(DT)
    p.pack_int(NRE)
    p.pack_int(NDISRE)
    p.pack_int(NBLOCK)
    if NDISRE != 0:
        assert ENX_VERSION < 4

    frame_blocks = BLOCKS.copy()
    startb = 0
    if NDISRE > 0:
        enxDISRE = 3  # Some constant defined by Gromacs
        # Sub-block type is 1 = float
        frame_blocks.insert(
            0, Block(enxDISRE, [SubBlock(NDISRE, 1), SubBlock(NDISRE, 1)])
        )
        startb += 1
    for b in range(startb, len(frame_blocks)):
        if ENX_VERSION < 4:
            # Old versions have only one sub block of reals (here 1 = float)
            assert len(frame_blocks[b].sub) == 1
            assert frame_blocks[b].sub[0].btype == 1
            p.pack_int(frame_blocks[b].sub[0].nr)
        else:
            p.pack_int(frame_blocks[b].bid)
            p.pack_int(len(frame_blocks[b].sub))
            for sub in frame_blocks[b].sub:
                p.pack_int(sub.btype)
                p.pack_int(sub.nr)

    p.pack_int(E_SIZE)
    p.pack_int(0)  # dummy
    p.pack_int(0)  # dummy
    # <- do_eheader
    for i in range(NRE):
        # Just generate some arbitrary value for the energy
        # Depends on step and column number
        p.pack_float(step * 100 + i)  # e
        if ENX_VERSION == 1 or NSUM > 0:
            p.pack_float(0.0)  # eav
            p.pack_float(0.0)  # esum
            if ENX_VERSION == 1:
                p.pack_float(0.0)  # dummy

    for b in range(len(frame_blocks)):
        for sub in frame_blocks[b].sub:
            for n in range(sub.nr):
                if sub.btype == 0:
                    p.pack_int(0)
                elif sub.btype == 1:
                    p.pack_float(0.0)
                elif sub.btype == 2:
                    p.pack_double(0.0)
                elif sub.btype == 3:
                    p.pack_hyper(0)
                elif sub.btype == 4:
                    # GMX casts the char to an u8 and writes this as an u32
                    p.pack_int(0)
                elif sub.btype == 5:
                    p.pack_string("ABC".encode("ascii"))
                else:
                    print("WARNING: Unknown sub-block type")
                    p.pack_int(0)


with open("dump.edr", "wb") as f:
    f.write(p.get_buffer())
