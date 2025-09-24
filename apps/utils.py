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
from flask import Response, jsonify, send_file

import io
import gzip
import yaml

import pandas as pd
import numpy as np
from pyarrow import fs
import pyarrow.parquet as pq
import pyarrow.dataset as ds

from astropy.io import fits


def readstamp(stamp: str, return_type="array", gzipped=True):
    """Decode stamps from the datalake"""

    def extract_stamp(fitsdata):
        """Extract FITS data from binary payload"""
        with fits.open(fitsdata, ignore_missing_simple=True) as hdul:
            if return_type == "array":
                data = hdul[0].data.tolist()
            elif return_type == "FITS":
                data = io.BytesIO()
                hdul.writeto(data)
                data.seek(0)
        return data

    if not isinstance(stamp, io.BytesIO):
        stamp = io.BytesIO(stamp)

    if gzipped:
        with gzip.open(stamp, "rb") as f:
            return extract_stamp(io.BytesIO(f.read()))
    else:
        return extract_stamp(stamp)


def format_and_send_cutout_from_ztf(payload: dict) -> pd.DataFrame:
    """Extract data returned by HBase and jsonify it

    Data is from /api/v1/cutouts

    Parameters
    ----------
    payload: dict
        See https://fink-portal.org/api/v1/cutouts

    Return
    ----------
    out: pandas dataframe
    """
    if payload["kind"] == "All":
        columns = ["objectId", "cutoutScience", "cutoutTemplate", "cutoutDifference"]
    elif payload["kind"] in ["Science", "Template", "Difference"]:
        columns = ["objectId", "cutout{}".format(payload["kind"])]
    else:
        raise AssertionError(
            "`col_kind` must be one of Science, Template, Difference, or All."
        )

    return_type = payload.get("return_type", "array")

    # If FITS is chosen, only one cutout is allowed
    if return_type == "FITS":
        if payload["kind"] == "All":
            rep = {
                "status": "error",
                "text": "return_type=All is not allowed for FITS.\n",
            }
            return Response(str(rep), 400)

    filters = [["objectId", "=", payload["objectId"]]]
    if "candid" in payload:
        filters.append(["candid", "=", int(payload["candid"])])

    args = yaml.load(open("config.yml"), yaml.Loader)
    hdfs = fs.HadoopFileSystem(args["HDFS"], args["HDFSPORT"], user=args["HDFSUSER"])

    # Fetch the relevant block
    table = pq.read_table(
        payload["hdfsPath"],
        columns=columns,
        filters=filters,
        filesystem=hdfs,
    )
    # TODO: check the table is not empty
    dic = table.to_pydict()
    cutouts = [
        readstamp(dic[col][0]["stampData"], return_type=return_type)
        for col in columns[1:]
    ]

    if return_type == "array":
        return jsonify(cutouts)
    elif return_type == "FITS":
        return send_file(
            cutouts[0],
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=payload["objectId"] + ".fits",
        )


def format_and_send_cutout_from_lsst(payload: dict) -> pd.DataFrame:
    """Extract data returned by HBase and jsonify it

    Data is from /api/v1/cutouts

    Parameters
    ----------
    payload: dict
        See https://fink-portal.org/api/v1/cutouts

    Return
    ----------
    out: pandas dataframe
    """
    if payload["kind"] == "All":
        columns = [
            "diaObject.diaObjectId",
            "cutoutScience",
            "cutoutTemplate",
            "cutoutDifference",
        ]
    elif payload["kind"] in ["Science", "Template", "Difference"]:
        columns = ["diaObject.diaObjectId", "cutout{}".format(payload["kind"])]
    else:
        raise AssertionError(
            "`col_kind` must be one of Science, Template, Difference, or All."
        )

    return_type = payload.get("return_type", "array")

    # If FITS is chosen, only one cutout is allowed
    if return_type == "FITS":
        if payload["kind"] == "All":
            rep = {
                "status": "error",
                "text": "return_type=All is not allowed for FITS.\n",
            }
            return Response(str(rep), 400)

    filters = ds.field("diaSource", "diaSourceId") == np.int64(payload["diaSourceId"])

    args = yaml.load(open("config.yml"), yaml.Loader)
    hdfs = fs.HadoopFileSystem(args["HDFS"], args["HDFSPORT"], user=args["HDFSUSER"])

    # Fetch the relevant block
    table = pq.read_table(
        payload["hdfsPath"],
        columns=columns,
        filters=filters,
        filesystem=hdfs,
    )
    # TODO: check the table is not empty
    dic = table.to_pydict()
    cutouts = [
        readstamp(dic[col][0], return_type=return_type, gzipped=False)
        for col in columns[1:]
    ]

    if return_type == "array":
        return jsonify(cutouts)
    elif return_type == "FITS":
        return send_file(
            cutouts[0],
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=payload["diaSourceId"] + ".fits",
        )
