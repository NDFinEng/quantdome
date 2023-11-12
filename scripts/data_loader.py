# insert historical equities data from pandas df to mysql db

import pandas as pd
from datetime import datetime
import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.db.mysql import MysqlHandler
from utils.events import MarketUpdate
from utils import (
    get_script_name,
    validate_cli_args,
    get_system_config,
    log_ini,
    save_pid,
    get_hostname,
)

# Global Variables
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

# Validate command arguments
kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

# Get system config file
SYS_CONFIG = get_system_config(sys_config_file)

def main():

    # Get source data file from command line
    if len(sys.argv) < 4:
        print("Usage: python data_loader.py <KAFKA_CONFIG_FILE> <SYS_CONFIG_FILE> <DATA_FILE>")
        sys.exit(1)

    data_file = sys.argv[3]

    # Read data file
    df = pd.read_csv(data_file)

    # Insert data to mysql db
    for index, row in df.iterrows():

        market_update = MarketUpdate(
            symbol=data_file.split("/")[-1].split(" ")[0],
            timestamp=datetime.strptime(row["Dates"], "%m/%d/%Y"),
            high=row["PX_HIGH"],
            low=row["PX_LOW"],
            open=row["PX_OPEN"],
            close=row["PX_LAST"],
            volume=row["PX_VOLUME"],
        )

        with MysqlHandler("quantdome_db", SYS_CONFIG) as db:
            db.insert_equities_historical(market_update)
        

if __name__ == "__main__":
    main()