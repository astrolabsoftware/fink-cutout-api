# Copyright 2024 AstroLab Software
# Author: Julien Peloton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
import numpy as np

from astropy.io import fits

import io
import sys
import json

APIURL = sys.argv[1]

TESTFILE="archive/science/year=2024/month=11/day=14/part-00019-14b4d19b-5bd1-4a33-a3d2-d7484c407981.c000.snappy.parquet"

def cutouttest(
    objectId="ZTF24abssjsb",
    kind="Science",
    return_type="array",
    candid=None,
):
    """Perform a cutout search in HDFS"""
    payload = {
        "hdfsPath": TESTFILE,
        "objectId": objectId,
        "kind": kind,  # Science, Template, Difference, All
        "return_type": return_type,
    }

    if candid is not None:
        payload.update({"candid": candid})

    r = requests.post("{}/api/v1/cutouts".format(APIURL), json=payload)

    assert r.status_code == 200, r.content

    if return_type == "FITS":
        data = fits.open(io.BytesIO(r.content), ignore_missing_simple=True)
    elif return_type == "array":
        data = json.loads(r.content)

    return data


def test_fits_cutout() -> None:
    """
    Examples
    --------
    >>> test_fits_cutout()
    """
    data = cutouttest(return_type="FITS")

    assert len(data) == 1
    assert np.shape(data[0].data) == (63, 63), np.shape(data[0].data)


def test_array_cutout() -> None:
    """
    Examples
    --------
    >>> test_array_cutout()
    """
    data = cutouttest(return_type="array")

    assert np.shape(data[0]) == (63, 63), np.shape(data[0])
    assert isinstance(data, list)


def test_kind_cutout() -> None:
    """
    Examples
    --------
    >>> test_kind_cutout()
    """
    data1 = cutouttest(kind="Science", return_type="array")
    data2 = cutouttest(kind="Template", return_type="array")
    data3 = cutouttest(kind="Difference", return_type="array")

    assert data1 != data2
    assert data2 != data3

    cutouts = cutouttest(kind="All", return_type="array")
    assert len(cutouts) == 3
    assert cutouts[0] != cutouts[1]
    assert cutouts[1] != cutouts[2]


def test_integrity() -> None:
    """
    Examples
    --------
    >>> test_integrity()
    """
    data1 = cutouttest(kind="Science", return_type="array")
    data2 = cutouttest(kind="Science", return_type="FITS")
    assert np.alltrue(data1[0] == data2[0].data)


#def test_candid_cutout() -> None:
#    """
#    Examples
#    --------
#    >>> test_candid_cutout()
#    """
#    data1 = cutouttest()
#    data2 = cutouttest(candid="1622215345315015012")
#
#    assert data1.getextrema() != data2.getextrema()


if __name__ == "__main__":
    """ Execute the test suite """
    import sys
    import doctest

    sys.exit(doctest.testmod()[0])
