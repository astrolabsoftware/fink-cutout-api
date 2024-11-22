#!/bin/bash

HADOOP_VERSION=3.3.6

cd /opt
wget https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
tar -xf hadoop-$HADOOP_VERSION.tar.gz
rm hadoop-$HADOOP_VERSION.tar.gz
