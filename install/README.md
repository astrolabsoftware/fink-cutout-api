# Hadoop installation

Execute the script to install it under `/opt`:

```bash
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
