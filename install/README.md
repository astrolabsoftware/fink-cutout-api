# API installation and deployment

Fire a Virtual Machine, and follow instructions. Work perfectly on recent AlmaLinux.

## Python dependencies

Clone this repository as `root` under `/opt`, and install all python dependencies:

```bash
pip install -r requirements.txt
```

## Java installation

You need Java 11 or 17. Execute:

```bash
dnf install java-11-openjdk java-11-openjdk-devel
```

and then update your `.bashrc` with:

```bash
# Java -- put your path
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-11.0.25.0.9-3.el9.x86_64/
```

Check you have it set:

```bash
source ~/.bashrc
java -version
# openjdk version "11.0.25" 2024-10-15 LTS
# OpenJDK Runtime Environment (Red_Hat-11.0.25.0.9-1) (build 11.0.25+9-LTS)
# OpenJDK 64-Bit Server VM (Red_Hat-11.0.25.0.9-1) (build 11.0.25+9-LTS, mixed mode, sharing)
```

## Hadoop installation

First execute the script as sudo to install it under `/opt`:

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

Install a new unit (as root) for systemd under `/etc/systemd/system/fink_cutout_api.service`:

```bash
[Unit]
Description=gunicorn daemon for fink_cutout_api
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/fink-cutout-api
Restart=on-failure
RestartSec=5s
ExecStart=/bin/sh -c 'source /root/.bashrc; exec /opt/fink-env/bin/gunicorn --log-file=/tmp/fink_cutout_api.log app:app -b localhost:PORT --workers=2 --threads=8 --timeout 180 --chdir /opt/fink-cutout-api --bind unix:/run/fink_cutout_api.sock 2>&1 >> /tmp/fink_cutout_api.out'

[Install]
WantedBy=multi-user.target
```

Make sure you change `PORT` with your actual port. Finally update the `config.yml` with your parameters (put the same `PORT`!), reload units and launch the application:

```bash
systemctl daemon-reload
systemctl enable fink_cutout_api
systemctl start fink_cutout_api
```

You are ready to use the API!
