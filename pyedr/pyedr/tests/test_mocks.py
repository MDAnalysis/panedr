# -*- coding: utf-8 -*-

"""
Tests for pyedr
"""
import pytest
from numpy.testing import assert_allclose

import pyedr
from pyedr.tests.datafiles import (
    EDR_MOCK_V1_ESUM0,
    EDR_MOCK_V5_STEP_NEGATIVE,
    EDR_MOCK_V1_STEP_NEGATIVE,
    EDR_MOCK_V_LARGE,
    EDR_MOCK_V4_LARGE_VERSION_FRAME,
    EDR_MOCK_V4_FIRST_REAL_V1,
    EDR_MOCK_V4_INVALID_FILE_MAGIC,
    EDR_MOCK_V4_INVALID_FRAME_MAGIC,
    EDR_MOCK_V4_INVALID_BLOCK_TYPE,
    EDR_MOCK_V4_ALL_BLOCK_TYPES,
    EDR_MOCK_V3_NDISRE2_BLOCKS,
)


def assert_dict(d):
    assert len(d) == 3
    assert_allclose(d["Time"], [0.0, 0.5, 1.0])
    assert_allclose(d["DUMMY1"], [0.0, 100.0, 200.0])
    assert_allclose(d["DUMMY2"], [1.0, 101.0, 201.0])


def test_esum_zero_v1():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 1, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        d = pyedr.edr_to_dict(EDR_MOCK_V1_ESUM0)
        assert_dict(d)


def test_step_negative_v5():
    with pytest.raises(ValueError, match="Something went wrong"):
        pyedr.edr_to_dict(EDR_MOCK_V5_STEP_NEGATIVE)


def test_step_negative_v1():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 1, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        with pytest.raises(RuntimeError, match="Failed reading header") as e:
            pyedr.edr_to_dict(EDR_MOCK_V1_STEP_NEGATIVE)
        assert (
            isinstance(e.value.__cause__, ValueError)
            and str(e.value.__cause__)
            == "edr file with negative step number or "
               "unreasonable time (and without version number)."
        )


def test_large_invalid_version():
    with pytest.raises(
        ValueError,
        match="Reading file version 1000000000 with "
              f"version {pyedr.ENX_VERSION} implementation",
    ):
        pyedr.edr_to_dict(EDR_MOCK_V_LARGE)


def test_large_invalid_version_frame_v4():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 4, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        with pytest.raises(RuntimeError, match="Failed reading header") as e:
            pyedr.edr_to_dict(EDR_MOCK_V4_LARGE_VERSION_FRAME)
        assert (
            isinstance(e.value.__cause__, ValueError)
            and str(e.value.__cause__)
            == "Reading file version 1000000000 with "
               f"version {pyedr.ENX_VERSION} implementation"
        )


def test_step_negative_v4():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 4, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        with pytest.raises(RuntimeError, match="Failed reading header") as e:
            pyedr.edr_to_dict(EDR_MOCK_V4_FIRST_REAL_V1)
        assert (
            isinstance(e.value.__cause__, ValueError)
            and str(e.value.__cause__)
            == "Expected file version 1, found version 4"
        )


def test_invalid_file_magic_v4():
    with pytest.raises(
        ValueError,
        match="Energy names magic number mismatch, "
              "this is not a GROMACS edr file",
    ):
        pyedr.edr_to_dict(EDR_MOCK_V4_INVALID_FILE_MAGIC)


def test_invalid_frame_magic_v4():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 4, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        with pytest.raises(RuntimeError, match="Failed reading header") as e:
            pyedr.edr_to_dict(EDR_MOCK_V4_INVALID_FRAME_MAGIC)
        assert (
            isinstance(e.value.__cause__, ValueError)
            and str(e.value.__cause__)
            == "Energy header magic number mismatch, "
               "this is not a GROMACS edr file"
        )


def test_block_type_v4():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 4, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        with pytest.raises(
            ValueError,
            match="Reading unknown block data type: "
                  "this file is corrupted or from the future",
        ):
            pyedr.edr_to_dict(EDR_MOCK_V4_INVALID_BLOCK_TYPE)


def test_all_block_types_v4():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 4, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        d = pyedr.edr_to_dict(EDR_MOCK_V4_ALL_BLOCK_TYPES)
        assert_dict(d)


def test_ndisre2_blocks_v3():
    with pytest.warns(
        UserWarning,
        match=f"enx file_version 3, "
              f"implementation version {pyedr.ENX_VERSION}",
    ):
        d = pyedr.edr_to_dict(EDR_MOCK_V3_NDISRE2_BLOCKS)
        assert_dict(d)
