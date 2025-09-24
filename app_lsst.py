# Copyright 2025 AstroLab Software
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
import flask
from flask import request, jsonify
from apps.utils import format_and_send_cutout_from_lsst

app = flask.Flask(__name__)

args_cutouts = [
    {
        "name": "hdfsPath",
        "required": True,
        "description": "Data path on HDFS",
    },
    {
        "name": "diaSourceId",
        "required": True,
        "description": "diaSource ID of the alert",
    },
    {
        "name": "kind",
        "required": True,
        "description": "Science, Template, Difference, or All",
    },
    {
        "name": "return_type",
        "required": False,
        "description": "Returned type among `array` or `FITS`. If not provided, `array` is chosen.",
    },
]


@app.route("/api/v1/cutouts", methods=["GET"])
def cutouts_arguments():
    """Obtain information about the cutouts service"""
    if len(request.args) > 0:
        # POST from query URL
        return return_cutouts(payload=request.args)
    else:
        return jsonify({"args": args_cutouts})


@app.route("/api/v1/cutouts", methods=["POST"])
def return_cutouts(payload=None):
    """Retrieve cutout data from the Fink data lake"""
    # get payload from the JSON
    if payload is None:
        payload = request.json

    # Make some checks
    assert payload["kind"] in ["Science", "Template", "Difference", "All"]

    return format_and_send_cutout_from_lsst(payload)


if __name__ == "__main__":
    import yaml

    input_args = yaml.load(open("config.yml"), yaml.Loader)
    app.run(input_args["APIURL"], port=int(input_args["PORT"]))
