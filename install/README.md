# API installation and deployment

Fire a Virtual Machine, and follow instructions. Work perfectly on recent AlmaLinux.

## Python dependencies

Clone this repository, and install all python dependencies:

```bash
pip install -r requirements.txt
```

## Hadoop installation

First Execute the script to install it under `/opt`:

```bash
cd install/
./install_hadoop.sh
```

and then update your `.bashrc` with (careful with the version number):

```bash
# Hadoop
export HADOOP_HDFS_HOME=/opt/hadoop-3.3.6
export HADOOP_HOME=$HADOOP_HDFS_HOME
export CLASSPATH=`$HADOOP_HOME/bin/hadoop classpath --glob`
export PATH=$PATH:$HADOOP_HDFS_HOME/bin:$HADOOP_HDFS_HOME/sbin
export ARROW_LIBHDFS_DIR=$HADOOP_HOME/lib/native
```

## Systemctl and gunicorn

Install a new unit for systemd under `/etc/systemd/system/fink_cutout_api.service`:

```bash
[Unit]
Description=gunicorn daemon for fink_cutout_api
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/centos/fink-cutout-api

ExecStart=/bin/sh -c 'source /root/.bashrc; exec /root/miniconda/bin/gunicorn --log-file=/tmp/fink_cutout_api.log app:app -b localhost:PORT --workers=1 --threads=8 --timeout 180 --chdir /home/centos/fink-cutout-api --bind unix:/run/fink_cutout_api.sock 2>&1 >> /tmp/fink_cutout_api.out'

[Install]
WantedBy=multi-user.target
```

Make sure you change `PORT` with your actual port. Reload units and launch the application:

```bash
systemctl daemon-reload
systemctl start fink_cutout_api
```

You are ready to use the API!
