#!/usr/bin/env bash

mkdir -p pid
mkdir -p logs

kafka_config_file="config_kafka/$1"
sys_config_file="config_sys/${2:-default.ini}"

if [ -z "$1" ]
then
    echo
    echo "Error: Missing configuration file. Usage: ./start_demo.sh {KAFKA_CONFIG_FILE} (under the folder 'config_kafka/')"
    echo
    exit 1
fi

if ! test -f "$kafka_config_file"
then
    echo
    echo "Error: Kafka configuration file not found: $kafka_config_file"
    echo
    exit 1
fi

if ! test -f "$sys_config_file"
then
    echo
    echo "Error: System configuration file not found: $sys_config_file"
    echo
    exit 1
else
    source env/bin/activate

    ./stop_demo.sh

    python3 microservice_data.py $1 $2 &
    python3 microservice_strategy.py $1 $2 &
    python3 microservice_order.py $1 $2 &
    python3 microservice_execution.py $1 $2 &

    sleep 3

    deactivate
fi