###########################
# Host specific settings? #
###########################

if [ -z "$SM_CUSTOMIZATION" ]; then
    read -r -d '' SM_CUSTOMIZATION <<EOF
spack load python@3.6.5
spack load jdk
EOF
    export SM_CUSTOMIZATION
fi

export SPARK_HOME=${SPARK_HOME:-$HOME/work/spark-2.3.0-bin-hadoop2.7}

##############################
# Create and use environment #
##############################

create_work_environment() {
    workdir=$1

    mkdir -p $workdir/{conf,derby,eventlog,log,tmp,warehouse,worker}

    python3.6 -m venv $workdir/venv3.6

    cat > $workdir/conf/spark-defaults.conf <<EOF
# see https://stackoverflow.com/questions/37871194/how-to-tune-spark-executor-number-cores-and-executor-memory
spark.executor.cores=8
spark.executor.memory=30g

# recommended, not the default due to backwards compatibility
spark.serializer=org.apache.spark.serializer.KryoSerializer

# increase network timeouts, as mentioned in some logs
spark.network.timeout=6000
# also increase the heartbeat timeout
spark.executor.heartbeatInterval=120

spark.eventLog.enabled=true
spark.eventLog.dir=$workdir/eventlog
spark.history.fs.logDirectory=$workdir/eventlog

spark.local.dir=/nvme,$workdir/tmp
spark.sql.warehouse.dir=$workdir/warehouse
EOF

    if [[ "$(uname -r)" == 2.6.32* ]]; then
        cat >> $workdir/conf/spark-defaults.conf <<EOF

# This is a 2.6.32 kernel bug…
spark.file.transferTo=false
EOF
    fi

    if [ -n "$SM_CUSTOMIZATION" ]; then
        echo "$SM_CUSTOMIZATION" > $workdir/env.sh
    fi

    cat >> $workdir/env.sh <<EOF
. $workdir/venv3.6/bin/activate

export SPARK_HOME=$SPARK_HOME
export SPARK_USER=$(whoami)

export SPARK_CONF_DIR=$workdir/conf
export SPARK_LOG_DIR=$workdir/log
export SPARK_WORKER_DIR=$workdir/worker

export PATH=\$SPARK_HOME/bin:\$PATH
EOF
}

workdir=$(readlink -f ${SM_WORKDIR:-$HOME/scratch/_default})

if [ ! -d "$workdir" ]; then
    create_work_environment $workdir
fi

. $workdir/env.sh
