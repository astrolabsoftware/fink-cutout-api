# Fink cutout API

This API is used internally by Fink web components to retrieve cutouts from the data lake on HDFS. We take advantage of the pyarrow connector to read parquet files to efficiently extract required cutouts from an HDFS block.

## Usage

To deploy the API, you need access to the Fink HDFS cluster. Once `config.yml` is filled, just deploy using:

```bash
python cutout_app.py
```

Test the connection:

```python
import requests

r = requests.post(
    "{}/api/v1/cutouts".format(URL),
    json={
        "hdfsPath": HDFS_PATH, 
        "kind": "Science", 
        "objectId": "ZTF24abssjsb"
    }
)
```

Note that `HDFS_PATH` should be an URI relative to the user home folder on HDFS, e.g.:

```diff
- NO: hdfs://IP:PORT/user/toto/somefolder/myparquet.parquet
+ YES: somefolder/myparquet.parquet
```
